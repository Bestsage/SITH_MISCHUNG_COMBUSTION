"use client";

import { useState, useMemo, useCallback } from "react";
import AppLayout from "@/components/AppLayout";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Html } from "@react-three/drei";
import * as THREE from "three";

// Types matching Rust backend
interface CFDRequest {
    r_throat: number;
    r_chamber: number;
    r_exit: number;
    l_chamber: number;
    l_nozzle: number;
    p_chamber: number;
    t_chamber: number;
    gamma: number;
    molar_mass: number;
    nx: number;
    ny: number;
    max_iter: number;
    tolerance: number;
}

interface CFDResult {
    x: number[];
    r: number[];
    pressure: number[];
    temperature: number[];
    mach: number[];
    velocity_x: number[];
    velocity_r: number[];
    density: number[];
    nx: number;
    ny: number;
    residual_history: number[];
    converged: boolean;
    iterations: number;
}

type FieldType = "mach" | "pressure" | "temperature" | "velocity_x" | "density";

const FIELD_CONFIG: Record<FieldType, { name: string; unit: string; colormap: string }> = {
    mach: { name: "Nombre de Mach", unit: "", colormap: "plasma" },
    pressure: { name: "Pression", unit: "Pa", colormap: "viridis" },
    temperature: { name: "Température", unit: "K", colormap: "inferno" },
    velocity_x: { name: "Vitesse Axiale", unit: "m/s", colormap: "coolwarm" },
    density: { name: "Densité", unit: "kg/m³", colormap: "magma" },
};

// Color map functions
function plasmaColor(t: number): [number, number, number] {
    // Plasma colormap approximation
    const r = Math.min(1, 0.05 + 3.5 * t - 2.5 * t * t);
    const g = Math.min(1, Math.max(0, 1.5 * t - 0.5));
    const b = Math.min(1, 0.5 + t * 0.5 - t * t * 0.5);
    return [
        Math.max(0.1, 0.13 + 0.85 * t + 0.5 * Math.sin(t * 3.14)),
        Math.max(0, 0.1 * t + 0.6 * t * t),
        Math.max(0.3, 0.53 - 0.4 * t + 0.9 * t * t)
    ];
}

function getColorForValue(t: number, colormap: string): THREE.Color {
    const color = new THREE.Color();
    t = Math.max(0, Math.min(1, t));

    switch (colormap) {
        case "plasma":
            color.setHSL(0.75 - t * 0.75, 1, 0.3 + t * 0.4);
            break;
        case "viridis":
            color.setHSL(0.75 - t * 0.5, 0.8, 0.25 + t * 0.35);
            break;
        case "inferno":
            color.setHSL(0.08 * t, 1, 0.15 + t * 0.5);
            break;
        case "coolwarm":
            if (t < 0.5) {
                color.setHSL(0.6, 0.8, 0.4 + (0.5 - t) * 0.4);
            } else {
                color.setHSL(0.0, 0.8, 0.4 + (t - 0.5) * 0.4);
            }
            break;
        case "magma":
            color.setHSL(0.85 - t * 0.15, 0.9, 0.1 + t * 0.6);
            break;
        default:
            color.setHSL(0.7 - t * 0.7, 1, 0.5);
    }
    return color;
}

// 2D Heatmap visualization using Three.js
function CFDHeatmap({ result, field, colormap }: { result: CFDResult; field: FieldType; colormap: string }) {
    const { geometry, minVal, maxVal } = useMemo(() => {
        const nx = result.nx;
        const ny = result.ny;
        const fieldData = result[field];

        // Find min/max for normalization
        let min = Infinity, max = -Infinity;
        for (const v of fieldData) {
            if (v < min) min = v;
            if (v > max) max = v;
        }

        // Create geometry
        const positions = new Float32Array(nx * ny * 3);
        const colors = new Float32Array(nx * ny * 3);

        // Scale factors for visualization
        const xScale = 20 / Math.max(...result.x);
        const rScale = 10 / Math.max(...result.r);

        for (let idx = 0; idx < nx * ny; idx++) {
            const x = result.x[idx] * xScale - 10;
            const r = result.r[idx] * rScale;

            positions[idx * 3] = x;
            positions[idx * 3 + 1] = r;
            positions[idx * 3 + 2] = 0;

            const t = (fieldData[idx] - min) / (max - min || 1);
            const color = getColorForValue(t, colormap);

            colors[idx * 3] = color.r;
            colors[idx * 3 + 1] = color.g;
            colors[idx * 3 + 2] = color.b;
        }

        // Create indices for triangles
        const indices: number[] = [];
        for (let j = 0; j < ny - 1; j++) {
            for (let i = 0; i < nx - 1; i++) {
                const a = j * nx + i;
                const b = j * nx + (i + 1);
                const c = (j + 1) * nx + i;
                const d = (j + 1) * nx + (i + 1);

                indices.push(a, b, d);
                indices.push(a, d, c);
            }
        }

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geo.setIndex(indices);

        return { geometry: geo, minVal: min, maxVal: max };
    }, [result, field, colormap]);

    return (
        <group rotation={[-Math.PI / 2, 0, 0]}>
            <OrbitControls enableRotate={true} enablePan={true} enableZoom={true} />
            <ambientLight intensity={0.8} />

            {/* Upper half */}
            <mesh geometry={geometry}>
                <meshBasicMaterial vertexColors side={THREE.DoubleSide} />
            </mesh>

            {/* Mirror for lower half (axisymmetric) */}
            <mesh geometry={geometry} scale={[1, -1, 1]}>
                <meshBasicMaterial vertexColors side={THREE.DoubleSide} />
            </mesh>

            {/* Centerline */}
            <line>
                <bufferGeometry>
                    <bufferAttribute
                        attach="attributes-position"
                        args={[new Float32Array([-10, 0, 0, 10, 0, 0]), 3]}
                        count={2}
                    />
                </bufferGeometry>
                <lineBasicMaterial color="#ffffff" opacity={0.5} transparent />
            </line>
        </group>
    );
}

// Color bar component
function ColorBar({ min, max, field, colormap }: { min: number; max: number; field: FieldType; colormap: string }) {
    const gradientStops = useMemo(() => {
        const stops = [];
        for (let i = 0; i <= 10; i++) {
            const t = i / 10;
            const color = getColorForValue(t, colormap);
            stops.push(`rgb(${Math.round(color.r * 255)}, ${Math.round(color.g * 255)}, ${Math.round(color.b * 255)})`);
        }
        return stops.join(', ');
    }, [colormap]);

    const config = FIELD_CONFIG[field];

    return (
        <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-2">
            <div className="flex flex-col justify-between h-48 text-xs text-gray-300">
                <span>{max.toExponential(2)}</span>
                <span>{((max + min) / 2).toExponential(2)}</span>
                <span>{min.toExponential(2)}</span>
            </div>
            <div
                className="w-4 h-48 rounded"
                style={{ background: `linear-gradient(to bottom, ${gradientStops})` }}
            />
            <div className="text-xs text-gray-400 rotate-90 origin-left translate-x-6">
                {config.name} {config.unit && `(${config.unit})`}
            </div>
        </div>
    );
}

export default function CFDPage() {
    const [params, setParams] = useState<CFDRequest>({
        r_throat: 0.02,
        r_chamber: 0.04,
        r_exit: 0.06,
        l_chamber: 0.1,
        l_nozzle: 0.15,
        p_chamber: 1_000_000,
        t_chamber: 3000,
        gamma: 1.2,
        molar_mass: 0.025,
        nx: 80,
        ny: 30,
        max_iter: 3000,
        tolerance: 1e-5,
    });

    const [result, setResult] = useState<CFDResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [selectedField, setSelectedField] = useState<FieldType>("mach");

    const runSimulation = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 120000); // 2 min timeout

            const response = await fetch("http://localhost:8000/api/cfd/solve", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(params),
                signal: controller.signal,
            });

            clearTimeout(timeout);

            if (!response.ok) {
                const text = await response.text();
                throw new Error(`HTTP ${response.status}: ${text || 'Erreur serveur'}`);
            }

            const text = await response.text();
            if (!text) {
                throw new Error("Réponse vide du serveur. Vérifiez que le backend Rust est lancé.");
            }

            try {
                const data: CFDResult = JSON.parse(text);
                setResult(data);
            } catch (parseErr) {
                throw new Error(`Erreur parsing JSON: ${text.substring(0, 100)}...`);
            }
        } catch (err) {
            if (err instanceof Error) {
                if (err.name === 'AbortError') {
                    setError("Timeout: la simulation a pris trop de temps");
                } else if (err.message.includes('fetch')) {
                    setError("Impossible de contacter le serveur. Lancez: cargo run dans rocket_server/");
                } else {
                    setError(err.message);
                }
            } else {
                setError("Erreur inconnue");
            }
        } finally {
            setLoading(false);
        }
    }, [params]);

    const fieldData = result ? result[selectedField] : [];
    const minVal = fieldData.length > 0 ? Math.min(...fieldData) : 0;
    const maxVal = fieldData.length > 0 ? Math.max(...fieldData) : 1;

    return (
        <AppLayout>
            <div className="flex h-screen overflow-hidden w-full">
                {/* Controls Panel */}
                <div className="w-80 bg-[#12121a] border-r border-[#27272a] flex flex-col flex-shrink-0 overflow-y-auto">
                    <div className="p-4 border-b border-[#27272a]">
                        <h1 className="text-xl font-bold text-white mb-1">🌊 CFD 2D</h1>
                        <p className="text-xs text-gray-500">Simulation Euler Axisymétrique</p>
                    </div>

                    {/* Geometry */}
                    <div className="p-4 border-b border-[#27272a]">
                        <h3 className="text-xs text-gray-500 uppercase font-bold mb-3">Géométrie</h3>
                        <div className="space-y-3">
                            {[
                                { key: "r_throat", label: "Rayon Col", unit: "mm", scale: 1000, min: 5, max: 50 },
                                { key: "r_chamber", label: "Rayon Chambre", unit: "mm", scale: 1000, min: 10, max: 100 },
                                { key: "r_exit", label: "Rayon Sortie", unit: "mm", scale: 1000, min: 20, max: 150 },
                                { key: "l_chamber", label: "Longueur Chambre", unit: "mm", scale: 1000, min: 50, max: 300 },
                                { key: "l_nozzle", label: "Longueur Tuyère", unit: "mm", scale: 1000, min: 50, max: 400 },
                            ].map(({ key, label, unit, scale, min, max }) => (
                                <div key={key}>
                                    <div className="flex justify-between text-xs mb-1">
                                        <span className="text-gray-300">{label}</span>
                                        <span className="text-cyan-400">
                                            {((params as any)[key] * scale).toFixed(0)} {unit}
                                        </span>
                                    </div>
                                    <input
                                        type="range"
                                        min={min}
                                        max={max}
                                        step={1}
                                        value={(params as any)[key] * scale}
                                        onChange={(e) => setParams(p => ({ ...p, [key]: parseFloat(e.target.value) / scale }))}
                                        className="w-full accent-cyan-500"
                                    />
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Conditions */}
                    <div className="p-4 border-b border-[#27272a]">
                        <h3 className="text-xs text-gray-500 uppercase font-bold mb-3">Conditions</h3>
                        <div className="space-y-3">
                            <div>
                                <div className="flex justify-between text-xs mb-1">
                                    <span className="text-gray-300">Pression Chambre</span>
                                    <span className="text-orange-400">{(params.p_chamber / 1e5).toFixed(1)} bar</span>
                                </div>
                                <input
                                    type="range"
                                    min={5}
                                    max={100}
                                    step={1}
                                    value={params.p_chamber / 1e5}
                                    onChange={(e) => setParams(p => ({ ...p, p_chamber: parseFloat(e.target.value) * 1e5 }))}
                                    className="w-full accent-orange-500"
                                />
                            </div>
                            <div>
                                <div className="flex justify-between text-xs mb-1">
                                    <span className="text-gray-300">Température Chambre</span>
                                    <span className="text-red-400">{params.t_chamber} K</span>
                                </div>
                                <input
                                    type="range"
                                    min={2000}
                                    max={4000}
                                    step={100}
                                    value={params.t_chamber}
                                    onChange={(e) => setParams(p => ({ ...p, t_chamber: parseFloat(e.target.value) }))}
                                    className="w-full accent-red-500"
                                />
                            </div>
                            <div>
                                <div className="flex justify-between text-xs mb-1">
                                    <span className="text-gray-300">Gamma (γ)</span>
                                    <span className="text-purple-400">{params.gamma.toFixed(2)}</span>
                                </div>
                                <input
                                    type="range"
                                    min={1.1}
                                    max={1.4}
                                    step={0.01}
                                    value={params.gamma}
                                    onChange={(e) => setParams(p => ({ ...p, gamma: parseFloat(e.target.value) }))}
                                    className="w-full accent-purple-500"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Solver settings */}
                    <div className="p-4 border-b border-[#27272a]">
                        <h3 className="text-xs text-gray-500 uppercase font-bold mb-3">Solveur</h3>
                        <div className="grid grid-cols-2 gap-2 text-xs">
                            <div>
                                <label className="text-gray-400">Grille X</label>
                                <input
                                    type="number"
                                    value={params.nx}
                                    min={20}
                                    max={200}
                                    onChange={(e) => setParams(p => ({ ...p, nx: parseInt(e.target.value) || 50 }))}
                                    className="w-full mt-1 px-2 py-1 bg-[#1a1a25] border border-[#27272a] rounded text-white"
                                />
                            </div>
                            <div>
                                <label className="text-gray-400">Grille Y</label>
                                <input
                                    type="number"
                                    value={params.ny}
                                    min={10}
                                    max={100}
                                    onChange={(e) => setParams(p => ({ ...p, ny: parseInt(e.target.value) || 20 }))}
                                    className="w-full mt-1 px-2 py-1 bg-[#1a1a25] border border-[#27272a] rounded text-white"
                                />
                            </div>
                            <div className="col-span-2">
                                <label className="text-gray-400">Max Iterations</label>
                                <input
                                    type="number"
                                    value={params.max_iter}
                                    min={100}
                                    max={10000}
                                    step={100}
                                    onChange={(e) => setParams(p => ({ ...p, max_iter: parseInt(e.target.value) || 1000 }))}
                                    className="w-full mt-1 px-2 py-1 bg-[#1a1a25] border border-[#27272a] rounded text-white"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Run button */}
                    <div className="p-4">
                        <button
                            onClick={runSimulation}
                            disabled={loading}
                            className={`w-full py-3 rounded-lg font-bold text-white transition-all ${loading
                                ? "bg-gray-600 cursor-wait"
                                : "bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 shadow-lg shadow-cyan-500/30"
                                }`}
                        >
                            {loading ? (
                                <span className="flex items-center justify-center gap-2">
                                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                    </svg>
                                    Calcul en cours...
                                </span>
                            ) : (
                                "🚀 Lancer Simulation"
                            )}
                        </button>
                    </div>

                    {/* Results summary */}
                    {result && (
                        <div className="p-4 bg-[#0d0d12] border-t border-[#27272a]">
                            <h3 className="text-xs text-gray-500 uppercase font-bold mb-2">Résultats</h3>
                            <div className="grid grid-cols-2 gap-2 text-xs">
                                <div className="bg-[#1a1a25] p-2 rounded">
                                    <span className="text-gray-400">Convergé</span>
                                    <div className={`font-bold ${result.converged ? "text-green-400" : "text-red-400"}`}>
                                        {result.converged ? "✓ Oui" : "✗ Non"}
                                    </div>
                                </div>
                                <div className="bg-[#1a1a25] p-2 rounded">
                                    <span className="text-gray-400">Itérations</span>
                                    <div className="font-bold text-cyan-400">{result.iterations}</div>
                                </div>
                                <div className="bg-[#1a1a25] p-2 rounded">
                                    <span className="text-gray-400">Mach Max</span>
                                    <div className="font-bold text-orange-400">
                                        {Math.max(...result.mach).toFixed(2)}
                                    </div>
                                </div>
                                <div className="bg-[#1a1a25] p-2 rounded">
                                    <span className="text-gray-400">P Min</span>
                                    <div className="font-bold text-purple-400">
                                        {(Math.min(...result.pressure) / 1e5).toFixed(2)} bar
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {error && (
                        <div className="p-4 bg-red-900/30 border-t border-red-500/50">
                            <p className="text-red-400 text-sm">❌ {error}</p>
                        </div>
                    )}
                </div>

                {/* Visualization Area */}
                <div className="flex-1 bg-[#0a0a0f] relative overflow-hidden flex flex-col">
                    {/* Field selector */}
                    <div className="absolute top-4 left-4 z-10 flex gap-2">
                        {(Object.keys(FIELD_CONFIG) as FieldType[]).map((f) => (
                            <button
                                key={f}
                                onClick={() => setSelectedField(f)}
                                className={`px-3 py-1 rounded text-xs font-bold transition-all ${selectedField === f
                                    ? "bg-cyan-600 text-white"
                                    : "bg-[#1a1a25] text-gray-400 hover:bg-[#27272a]"
                                    }`}
                            >
                                {FIELD_CONFIG[f].name}
                            </button>
                        ))}
                    </div>

                    {/* Canvas */}
                    <div className="flex-1">
                        {result ? (
                            <>
                                <Canvas camera={{ position: [0, 0, 15], fov: 50 }}>
                                    <CFDHeatmap
                                        result={result}
                                        field={selectedField}
                                        colormap={FIELD_CONFIG[selectedField].colormap}
                                    />
                                </Canvas>
                                <ColorBar
                                    min={minVal}
                                    max={maxVal}
                                    field={selectedField}
                                    colormap={FIELD_CONFIG[selectedField].colormap}
                                />
                            </>
                        ) : (
                            <div className="flex items-center justify-center h-full text-gray-500">
                                <div className="text-center">
                                    <div className="text-6xl mb-4">🌊</div>
                                    <p className="text-lg">Lancez une simulation pour voir les résultats</p>
                                    <p className="text-sm text-gray-600 mt-2">
                                        Le solveur CFD 2D calcule l'écoulement dans la tuyère
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Convergence plot */}
                    {result && result.residual_history.length > 0 && (
                        <div className="absolute bottom-4 left-4 w-64 h-32 bg-[#12121a]/90 rounded-lg p-2 border border-[#27272a]">
                            <h4 className="text-xs text-gray-500 mb-1">Convergence</h4>
                            <svg viewBox="0 0 200 80" className="w-full h-full">
                                {/* Grid lines */}
                                <line x1="20" y1="10" x2="20" y2="70" stroke="#27272a" strokeWidth="0.5" />
                                <line x1="20" y1="70" x2="195" y2="70" stroke="#27272a" strokeWidth="0.5" />

                                {/* Residual curve */}
                                <polyline
                                    fill="none"
                                    stroke="#00d4ff"
                                    strokeWidth="1.5"
                                    points={result.residual_history
                                        .filter((_, i) => i % Math.ceil(result.residual_history.length / 100) === 0)
                                        .map((r, i, arr) => {
                                            const x = 20 + (i / arr.length) * 175;
                                            const logR = Math.log10(Math.max(r, 1e-12));
                                            const minLog = -12;
                                            const maxLog = 0;
                                            const y = 70 - ((logR - minLog) / (maxLog - minLog)) * 60;
                                            return `${x},${y}`;
                                        })
                                        .join(' ')}
                                />
                            </svg>
                        </div>
                    )}
                </div>
            </div>
        </AppLayout>
    );
}
