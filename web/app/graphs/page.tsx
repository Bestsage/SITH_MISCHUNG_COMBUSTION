"use client";

import { useState, useMemo, useRef, useEffect } from "react";
import AppLayout from "@/components/AppLayout";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from "recharts";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Text, Html } from "@react-three/drei";
import * as THREE from "three";
import DualRangeSlider from "@/components/DualRangeSlider";

// --- Configuration ---

type Variable = "pc" | "of" | "eps" | "mdot" | "x" | "isp" | "thrust" | "tc" | "cf" | "twall" | "hg";

interface VarDef {
    id: Variable;
    name: string;
    unit: string;
    type: "input" | "output";
    min?: number;
    max?: number;
    step?: number;
    default?: number;
}

const VARIABLES: VarDef[] = [
    // Inputs (Sweepable)
    { id: "pc", name: "Pression Chambre", unit: "bar", type: "input", min: 10, max: 150, step: 5, default: 25 },
    { id: "of", name: "Ratio O/F", unit: "", type: "input", min: 1.0, max: 6.0, step: 0.1, default: 2.5 },
    { id: "eps", name: "Ratio Expansion", unit: "", type: "input", min: 5, max: 200, step: 5, default: 40 },
    { id: "mdot", name: "Débit Massique", unit: "kg/s", type: "input", min: 0.1, max: 10, step: 0.1, default: 1.0 },
    { id: "x", name: "Position", unit: "mm", type: "input", min: 0, max: 500, step: 5, default: 0 },

    // Outputs
    { id: "isp", name: "Isp (Vide)", unit: "s", type: "output" },
    { id: "thrust", name: "Poussée", unit: "N", type: "output" },
    { id: "tc", name: "Température Chambre", unit: "K", type: "output" },
    { id: "cf", name: "Coef. Poussée", unit: "", type: "output" },
    { id: "twall", name: "Température Paroi", unit: "K", type: "output" },
    { id: "hg", name: "Coef. Convection", unit: "W/m²K", type: "output" },
];

const INPUTS = VARIABLES.filter(v => v.type === "input");
const OUTPUTS = VARIABLES.filter(v => v.type === "output");

// --- Physics Model (Simplified) ---

function calculatePoint(inputs: Record<Variable, number>): Record<Variable, number> {
    const { pc, of, eps, mdot, x } = inputs;

    // Constants
    const gamma = 1.2;
    const R = 350; // J/kg.K approx for exhaust

    // Tc Model (Parabolic approximation around optimal O/F)
    const of_opt = 2.8;
    const tc_max = 3400;
    const tc = tc_max - 400 * Math.pow((of - of_opt) / 1.5, 2);

    // Cf Model
    const pe_pc = Math.pow(1 / eps, gamma); // Simplified pressure ratio
    const pr = Math.pow(2 / (gamma + 1), gamma / (gamma - 1));
    const term1 = 2 * gamma * gamma / (gamma - 1);
    const term2 = 1 - Math.pow(1 / eps, (gamma - 1) / gamma);
    let cf = Math.sqrt(term1 * pr * term2) + (1 / eps) * (pe_pc - 0); // Ideal Cf
    cf = cf * 0.98; // Efficiency

    // Isp Model
    // Isp = c* * Cf / g0
    // c* proportional to sqrt(Tc)
    const cstar_ref = 1500; // m/s
    const cstar = cstar_ref * Math.sqrt(tc / 3400);
    const isp = (cstar * cf) / 9.81 + 20 * Math.log10(pc / 10); // Pc correction

    // Thrust
    const thrust = mdot * isp * 9.81;

    // Spatial Models (x dependent)
    const throat_x = 150;
    const throat_r = 25;
    let r = 0;
    // Geometry approx
    if (x < throat_x) {
        r = 50 - (50 - 25) * (x / throat_x); // Convergent
    } else {
        r = 25 + (60 - 25) * Math.sqrt((x - throat_x) / 350); // Divergent
    }
    const area = Math.PI * r * r;
    const area_throat = Math.PI * throat_r * throat_r;
    const local_eps = area / area_throat;

    const hg = 3000 * Math.pow(pc / 25, 0.8) / Math.pow(local_eps, 0.9); // Bartz scaling
    const twall = 400 + hg * (tc - 400) / 10000; // Simplistic thermal balance

    const result = {
        pc, of, eps, mdot, x,
        isp, thrust, tc, cf, hg, twall
    };
    // console.log("[GraphDebug] Calculated point:", result); 
    return result;
}

// --- 3D Graph Component ---

function Graph3D({ data, xVar, yVar, zVar, resolution }: { data: any[], xVar: Variable, yVar: Variable, zVar: Variable, resolution: number }) {
    const meshRef = useRef<THREE.Mesh>(null);

    const xDef = VARIABLES.find(v => v.id === xVar)!;
    const yDef = VARIABLES.find(v => v.id === yVar)!;
    const zDef = VARIABLES.find(v => v.id === zVar)!;

    // Normalize data
    const xValues = data.map(d => d[xVar]);
    const yValues = data.map(d => d[yVar]);
    const zValues = data.map(d => d[zVar]);

    const xMin = Math.min(...xValues);
    const xMax = Math.max(...xValues);
    const yMin = Math.min(...yValues);
    const yMax = Math.max(...yValues);
    const zMin = Math.min(...zValues);
    const zMax = Math.max(...zValues);

    const geometry = useMemo(() => {
        const countX = resolution + 1;
        const countY = resolution + 1;
        const totalPoints = countX * countY;

        const positions = new Float32Array(totalPoints * 3);
        const colors = new Float32Array(totalPoints * 3);
        const indices: number[] = [];
        const colorObj = new THREE.Color();

        // 1. Generate Vertices & Colors
        data.forEach((d, i) => {
            if (i >= totalPoints) return;

            // Normalize coordinates to fit in the scene
            const nx = ((d[xVar] - xMin) / (xMax - xMin || 1)) * 10 - 5;
            const ny = ((d[zVar] - zMin) / (zMax - zMin || 1)) * 5; // Height (Z value maps to Y visual)
            const nz = ((d[yVar] - yMin) / (yMax - yMin || 1)) * 10 - 5;

            positions[i * 3] = nx;
            positions[i * 3 + 1] = ny;
            positions[i * 3 + 2] = nz;

            // Color map (Inferno-ish: dark purple to yellow)
            const t = (d[zVar] - zMin) / (zMax - zMin || 1);
            colorObj.setHSL(0.7 - t * 0.6, 1, 0.5);

            colors[i * 3] = colorObj.r;
            colors[i * 3 + 1] = colorObj.g;
            colors[i * 3 + 2] = colorObj.b;
        });

        // 2. Generate Indices (Triangulation)
        for (let i = 0; i < resolution; i++) {
            for (let j = 0; j < resolution; j++) {
                // Determine indices of the 4 corners of the grid cell
                const a = i * countY + j;
                const b = i * countY + (j + 1);
                const c = (i + 1) * countY + j;
                const d = (i + 1) * countY + (j + 1);

                // Two triangles per square
                // Triangle 1: a -> b -> d
                indices.push(a, d, b);
                // Triangle 2: a -> d -> c
                indices.push(a, c, d);
            }
        }

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geo.setIndex(indices);
        geo.computeVertexNormals();

        return geo;
    }, [data, xVar, yVar, zVar, xMin, xMax, yMin, yMax, zMin, zMax, resolution]);

    // Find maximum point
    const maxPoint = useMemo(() => {
        if (data.length === 0) return null;
        let maxIdx = 0;
        let maxZ = data[0][zVar];
        data.forEach((d, i) => {
            if (d[zVar] > maxZ) {
                maxZ = d[zVar];
                maxIdx = i;
            }
        });
        const d = data[maxIdx];
        // Normalize to scene coordinates
        const nx = ((d[xVar] - xMin) / (xMax - xMin || 1)) * 10 - 5;
        const ny = ((d[zVar] - zMin) / (zMax - zMin || 1)) * 5;
        const nz = ((d[yVar] - yMin) / (yMax - yMin || 1)) * 10 - 5;
        return {
            position: [nx, ny, nz] as [number, number, number],
            value: d[zVar],
            xVal: d[xVar],
            yVal: d[yVar]
        };
    }, [data, xVar, yVar, zVar, xMin, xMax, yMin, yMax, zMin, zMax]);

    return (
        <group>
            <OrbitControls autoRotate autoRotateSpeed={0.5} />
            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} intensity={1} />

            {/* Mesh Surface */}
            <mesh ref={meshRef} geometry={geometry}>
                <meshStandardMaterial
                    vertexColors
                    side={THREE.DoubleSide}
                    roughness={0.8}
                    metalness={0.2}
                />
            </mesh>

            {/* Wireframe overlay for better grid visibility */}
            <mesh geometry={geometry}>
                <meshBasicMaterial
                    color="#ffffff"
                    wireframe
                    transparent
                    opacity={0.1}
                />
            </mesh>

            <gridHelper args={[20, 20, 0x444444, 0x222222]} position={[0, -2.5, 0]} />

            {/* 3D Axes Lines - at corner of surface */}
            {/* X Axis (cyan) - from corner */}
            <line>
                <bufferGeometry>
                    <bufferAttribute attach="attributes-position" args={[new Float32Array([-5, 0, -5, 5, 0, -5]), 3]} count={2} />
                </bufferGeometry>
                <lineBasicMaterial color="#00d4ff" linewidth={2} />
            </line>
            {/* Y Axis (visual - height, orange) - from corner */}
            <line>
                <bufferGeometry>
                    <bufferAttribute attach="attributes-position" args={[new Float32Array([-5, 0, -5, -5, 5, -5]), 3]} count={2} />
                </bufferGeometry>
                <lineBasicMaterial color="#f59e0b" linewidth={2} />
            </line>
            {/* Z Axis (red) - from corner */}
            <line>
                <bufferGeometry>
                    <bufferAttribute attach="attributes-position" args={[new Float32Array([-5, 0, -5, -5, 0, 5]), 3]} count={2} />
                </bufferGeometry>
                <lineBasicMaterial color="#ef4444" linewidth={2} />
            </line>

            {/* Axis Tick Marks and Values */}
            {/* X Axis ticks (5 ticks) */}
            {[0, 0.25, 0.5, 0.75, 1].map((t, i) => {
                const pos = -5 + t * 10;
                const val = xMin + t * (xMax - xMin);
                return (
                    <group key={`xtick-${i}`}>
                        <line>
                            <bufferGeometry>
                                <bufferAttribute attach="attributes-position" args={[new Float32Array([pos, 0, -5, pos, 0, -5.3]), 3]} count={2} />
                            </bufferGeometry>
                            <lineBasicMaterial color="#00d4ff" />
                        </line>
                        <Html position={[pos, -0.3, -5.5]} className="text-[#00d4ff] text-[9px]">{val.toFixed(1)}</Html>
                    </group>
                );
            })}
            {/* Y Axis ticks (height - 5 ticks) */}
            {[0, 0.25, 0.5, 0.75, 1].map((t, i) => {
                const pos = t * 5;
                const val = zMin + t * (zMax - zMin);
                return (
                    <group key={`ytick-${i}`}>
                        <line>
                            <bufferGeometry>
                                <bufferAttribute attach="attributes-position" args={[new Float32Array([-5, pos, -5, -5.3, pos, -5]), 3]} count={2} />
                            </bufferGeometry>
                            <lineBasicMaterial color="#f59e0b" />
                        </line>
                        <Html position={[-5.6, pos, -5]} className="text-[#f59e0b] text-[9px]">{val.toFixed(0)}</Html>
                    </group>
                );
            })}
            {/* Z Axis ticks (depth - 5 ticks) */}
            {[0, 0.25, 0.5, 0.75, 1].map((t, i) => {
                const pos = -5 + t * 10;
                const val = yMin + t * (yMax - yMin);
                return (
                    <group key={`ztick-${i}`}>
                        <line>
                            <bufferGeometry>
                                <bufferAttribute attach="attributes-position" args={[new Float32Array([-5, 0, pos, -5.3, 0, pos]), 3]} count={2} />
                            </bufferGeometry>
                            <lineBasicMaterial color="#ef4444" />
                        </line>
                        <Html position={[-5.6, -0.3, pos]} className="text-[#ef4444] text-[9px]">{val.toFixed(0)}</Html>
                    </group>
                );
            })}

            {/* Maximum Point Marker */}
            {maxPoint && (
                <>
                    <mesh position={maxPoint.position}>
                        <sphereGeometry args={[0.2, 16, 16]} />
                        <meshStandardMaterial color="#fbbf24" emissive="#fbbf24" emissiveIntensity={0.5} />
                    </mesh>
                    <Html position={[maxPoint.position[0], maxPoint.position[1] + 0.7, maxPoint.position[2]]} className="text-yellow-400 font-bold text-xs bg-black/80 px-2 py-1 rounded whitespace-nowrap border border-yellow-500/50">
                        <div>Max: {maxPoint.value.toFixed(2)} {zDef.unit}</div>
                        <div className="text-[10px] text-gray-300">{xDef.name}: {maxPoint.xVal.toFixed(2)} • {yDef.name}: {maxPoint.yVal.toFixed(2)}</div>
                    </Html>
                </>
            )}

            {/* Axes Labels - at ends of axes from corner */}
            <Html position={[5.5, 0, -5]} className="text-[#00d4ff] font-bold text-xs">{xDef.name}</Html>
            <Html position={[-5, 5.5, -5]} className="text-[#f59e0b] font-bold text-xs">{zDef.name}</Html>
            <Html position={[-5, 0, 5.5]} className="text-[#ef4444] font-bold text-xs">{yDef.name}</Html>
        </group>
    );
}

export default function GraphsPage() {
    // State
    const [is3D, setIs3D] = useState(false);
    const [mounted, setMounted] = useState(false);

    // Axes selection
    const [sweep1, setSweep1] = useState<Variable>("of"); // X-axis
    const [sweep2, setSweep2] = useState<Variable>("pc"); // Y-axis (only in 3D)
    const [valueVar, setValueVar] = useState<Variable>("isp"); // Y-axis (2D) or Z-axis (3D)

    // Ranges for sweep axes
    const [axisRanges, setAxisRanges] = useState<Record<string, [number, number]>>({});

    // Fixed Parameters
    const [params, setParams] = useState<Record<Variable, number>>({
        pc: 25, of: 2.5, eps: 40, mdot: 1.0, x: 0,
        isp: 0, thrust: 0, tc: 0, cf: 0, twall: 0, hg: 0
    });

    const resolution = 30; // Grid resolution for 3D

    useEffect(() => {
        setMounted(true);
        console.log("[GraphDebug] Component Mounted");
    }, []);

    // Initialize ranges if missing
    useEffect(() => {
        const newRanges = { ...axisRanges };
        let changed = false;

        INPUTS.forEach(v => {
            if (!newRanges[v.id]) {
                newRanges[v.id] = [v.min || 0, v.max || 10];
                changed = true;
            }
        });

        if (changed) {
            setAxisRanges(newRanges);
        }
    }, [axisRanges]);

    // Generate Data
    const data = useMemo(() => {
        const points = [];

        const xDef = VARIABLES.find(v => v.id === sweep1)!;
        const xRange = axisRanges[sweep1] || [xDef.min || 0, xDef.max || 10];

        // console.log(`[GraphDebug] Generating data. Mode: ${is3D ? '3D' : '2D'}, Sweep1: ${sweep1}, Value: ${valueVar}`);

        if (!is3D) {
            // 2D Interpolation
            const min = xRange[0];
            const max = xRange[1];
            // Ensure min < max
            const realMin = Math.min(min, max);
            const realMax = Math.max(min, max);

            const step = (realMax - realMin) / 50 || 0.1; // 50 points

            for (let val = realMin; val <= realMax; val += step) {
                const p = { ...params, [sweep1]: val };
                const res = calculatePoint(p);
                points.push(res);
            }
        } else {
            // 3D Grid
            const minX = xRange[0];
            const maxX = xRange[1];

            const yDef = VARIABLES.find(v => v.id === sweep2);
            // Always sweep2 is valid input now due to separate state
            const yRange = axisRanges[sweep2] || [yDef?.min || 0, yDef?.max || 10];
            const minY = yRange[0];
            const maxY = yRange[1];

            // Strict grid generation for Mesh compatibility
            for (let i = 0; i <= resolution; i++) {
                const vx = minX + (i / resolution) * (maxX - minX);
                for (let j = 0; j <= resolution; j++) {
                    const vy = minY + (j / resolution) * (maxY - minY);
                    const p = { ...params, [sweep1]: vx, [sweep2]: vy };
                    const res = calculatePoint(p);
                    points.push(res);
                }
            }
        }

        console.log(`[GraphDebug] Generated ${points.length} points.`);
        return points;
    }, [sweep1, sweep2, valueVar, is3D, params, axisRanges]);

    if (!mounted) {
        console.log("[GraphDebug] Not mounted yet");
        return null;
    }

    return (
        <AppLayout>
            <div className="flex h-screen overflow-hidden w-full">
                {/* Controls Sidebar */}
                <div className="w-80 bg-[#12121a] border-r border-[#27272a] flex flex-col flex-shrink-0 overflow-y-auto z-20">
                    <div className="p-4 border-b border-[#27272a]">
                        <h1 className="text-xl font-bold text-white mb-2">📈 Créateur de Graphes</h1>
                        <div className="flex items-center gap-4 text-sm mb-4">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input type="radio" checked={!is3D} onChange={() => setIs3D(false)} className="accent-[#00d4ff]" />
                                <span className={!is3D ? "text-[#00d4ff]" : "text-[#71717a]"}>2D Line</span>
                            </label>
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input type="radio" checked={is3D} onChange={() => setIs3D(true)} className="accent-[#ef4444]" />
                                <span className={is3D ? "text-[#ef4444]" : "text-[#71717a]"}>3D Surface</span>
                            </label>
                        </div>

                        {/* Axis Selection */}
                        <div className="space-y-6">
                            <div>
                                <label className="text-xs text-[#71717a] uppercase font-bold">Axe X (Balayage)</label>
                                <select
                                    className="input-field w-full mt-1 mb-2"
                                    value={sweep1}
                                    onChange={(e) => setSweep1(e.target.value as Variable)}
                                >
                                    {INPUTS.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
                                </select>
                                {/* Dual Range Slider for X */}
                                <div className="px-1">
                                    <div className="flex justify-between text-xs text-[#00d4ff] mb-1">
                                        <span>{(axisRanges[sweep1]?.[0] ?? 0).toFixed(1)}</span>
                                        <span>{(axisRanges[sweep1]?.[1] ?? 10).toFixed(1)}</span>
                                    </div>
                                    <DualRangeSlider
                                        min={VARIABLES.find(v => v.id === sweep1)?.min || 0}
                                        max={VARIABLES.find(v => v.id === sweep1)?.max || 10}
                                        step={VARIABLES.find(v => v.id === sweep1)?.step || 0.1}
                                        value={axisRanges[sweep1] || [0, 10]}
                                        onChange={(val) => setAxisRanges(prev => ({ ...prev, [sweep1]: val }))}
                                    />
                                </div>
                            </div>

                            {is3D && (
                                <div>
                                    <label className="text-xs text-[#71717a] uppercase font-bold">Axe Y (Balayage 2)</label>
                                    <select
                                        className="input-field w-full mt-1 mb-2"
                                        value={sweep2}
                                        onChange={(e) => setSweep2(e.target.value as Variable)}
                                    >
                                        {INPUTS.filter(v => v.id !== sweep1).map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
                                    </select>
                                    {/* Dual Range Slider for Y (if sweep) */}
                                    <div className="px-1">
                                        <div className="flex justify-between text-xs text-[#ef4444] mb-1">
                                            <span>{(axisRanges[sweep2]?.[0] ?? 0).toFixed(1)}</span>
                                            <span>{(axisRanges[sweep2]?.[1] ?? 10).toFixed(1)}</span>
                                        </div>
                                        <DualRangeSlider
                                            min={VARIABLES.find(v => v.id === sweep2)?.min || 0}
                                            max={VARIABLES.find(v => v.id === sweep2)?.max || 10}
                                            step={VARIABLES.find(v => v.id === sweep2)?.step || 0.1}
                                            value={axisRanges[sweep2] || [0, 10]}
                                            onChange={(val) => setAxisRanges(prev => ({ ...prev, [sweep2]: val }))}
                                            color="#ef4444"
                                        />
                                    </div>
                                </div>
                            )}

                            <div>
                                <label className="text-xs text-[#71717a] uppercase font-bold">
                                    {is3D ? "Axe Z (Valeur)" : "Axe Y (Valeur)"}
                                </label>
                                <select
                                    className="input-field w-full mt-1"
                                    value={valueVar}
                                    onChange={(e) => setValueVar(e.target.value as Variable)}
                                >
                                    {OUTPUTS.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
                                </select>
                            </div>
                        </div>
                    </div>

                    {/* Fixed Parameters */}
                    <div className="p-4">
                        <h3 className="text-xs text-[#71717a] uppercase font-bold mb-3">Constantes</h3>
                        <div className="space-y-3">
                            {INPUTS.filter(v => v.id !== sweep1 && (!is3D || v.id !== sweep2)).map((input) => (
                                <div key={input.id}>
                                    <div className="flex justify-between text-xs mb-1">
                                        <label className="text-gray-300">{input.name}</label>
                                        <span className="text-[#00d4ff]">{params[input.id]} {input.unit}</span>
                                    </div>
                                    <input
                                        type="range"
                                        min={input.min}
                                        max={input.max}
                                        step={input.step}
                                        value={params[input.id]}
                                        onChange={(e) => setParams(p => ({ ...p, [input.id]: parseFloat(e.target.value) }))}
                                        className="w-full accent-[#00d4ff] bg-[#27272a] h-1 rounded appearance-none"
                                    />
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Main Graph Area */}
                <div className="flex-1 bg-[#0a0a0f] relative overflow-hidden min-w-0 flex flex-col">
                    {/* Header: Legend / Title - Compact */}
                    <div className="absolute top-4 left-4 z-10 pointer-events-none p-4 rounded-xl bg-black/50 backdrop-blur-sm border border-white/10">
                        <h2 className="text-xl font-bold text-white shadow-black drop-shadow-md">
                            {VARIABLES.find(v => v.id === valueVar)?.name}
                            <span className="text-[#71717a] mx-2">vs</span>
                            {VARIABLES.find(v => v.id === sweep1)?.name}
                            {is3D && <> <span className="text-[#71717a] mx-2">&</span> {VARIABLES.find(v => v.id === sweep2)?.name}</>}
                        </h2>
                        <div className="text-xs text-[#a1a1aa] mt-1">
                            {data.length} pts • {sweep1} vs {valueVar}
                        </div>
                    </div>

                    {/* Chart Container - Full Space with slight padding */}
                    <div className="flex-1 w-full h-full min-h-0 relative pt-2 pr-2 pb-6">
                        {is3D ? (
                            <div className="w-full h-full relative">
                                <Canvas camera={{ position: [8, 5, 8], fov: 45 }}>
                                    <Graph3D data={data} xVar={sweep1} yVar={sweep2} zVar={valueVar} resolution={resolution} />
                                </Canvas>
                                <div className="absolute bottom-4 right-4 text-xs text-[#71717a]">
                                    Drag to Rotate • Scroll to Zoom
                                </div>
                            </div>
                        ) : (
                            <ResponsiveContainer width="100%" height="100%" debounce={50}>
                                <AreaChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 30 }}>
                                    <defs>
                                        <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                                    <XAxis
                                        dataKey={sweep1}
                                        stroke="#71717a"
                                        label={{ value: VARIABLES.find(v => v.id === sweep1)?.name, position: "insideBottom", offset: -5, fill: "#71717a" }}
                                        tickFormatter={(val) => typeof val === 'number' ? val.toFixed(1) : val}
                                    />
                                    <YAxis
                                        stroke="#71717a"
                                        label={{ value: VARIABLES.find(v => v.id === valueVar)?.name, angle: -90, position: "insideLeft", fill: "#71717a" }}
                                    />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1a1a25', border: '1px solid #27272a', borderRadius: '8px' }}
                                        itemStyle={{ color: '#fff' }}
                                        formatter={(val: any) => [typeof val === 'number' ? val.toFixed(2) : val, VARIABLES.find(v => v.id === valueVar)?.name]}
                                        labelFormatter={(val) => `${VARIABLES.find(v => v.id === sweep1)?.name}: ${Number(val).toFixed(2)}`}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey={valueVar}
                                        stroke="#00d4ff"
                                        strokeWidth={3}
                                        fillOpacity={1}
                                        fill="url(#colorValue)"
                                        animationDuration={500}
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        )}
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
