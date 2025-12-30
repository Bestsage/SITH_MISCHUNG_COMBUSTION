"use client";

import { useState, useRef, useEffect, useCallback, useMemo } from "react";
import AppLayout from "@/components/AppLayout";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Html } from "@react-three/drei";
import * as THREE from "three";
import { useCalculation } from "@/contexts/CalculationContext";

type ViewMode = "radiale" | "developpee" | "3d";
type Colormap = "inferno" | "viridis" | "plasma" | "magma" | "hot" | "coolwarm";

// Colormap definitions (simplified gradients)
const colormaps: Record<Colormap, string[]> = {
    inferno: ["#000004", "#420a68", "#932667", "#dd513a", "#fca50a", "#fcffa4"],
    viridis: ["#440154", "#414487", "#2a788e", "#22a884", "#7ad151", "#fde725"],
    plasma: ["#0d0887", "#6a00a8", "#b12a90", "#e16462", "#fca636", "#f0f921"],
    magma: ["#000004", "#3b0f70", "#8c2981", "#de4968", "#fe9f6d", "#fcfdbf"],
    hot: ["#000000", "#e60000", "#ffa500", "#ffff00", "#ffffff"],
    coolwarm: ["#3b4cc0", "#688aef", "#a8c5fc", "#f7f7f7", "#f7a789", "#e35e4f", "#b40426"],
};

function interpolateColor(colors: string[], t: number): string {
    const n = colors.length - 1;
    const i = Math.floor(t * n);
    const f = t * n - i;

    if (i >= n) return colors[n];
    if (i < 0) return colors[0];

    const c1 = colors[i];
    const c2 = colors[i + 1];

    const r1 = parseInt(c1.slice(1, 3), 16);
    const g1 = parseInt(c1.slice(3, 5), 16);
    const b1 = parseInt(c1.slice(5, 7), 16);
    const r2 = parseInt(c2.slice(1, 3), 16);
    const g2 = parseInt(c2.slice(3, 5), 16);
    const b2 = parseInt(c2.slice(5, 7), 16);

    const r = Math.round(r1 + (r2 - r1) * f);
    const g = Math.round(g1 + (g2 - g1) * f);
    const b = Math.round(b1 + (b2 - b1) * f);

    return `rgb(${r},${g},${b})`;
}

// RGB version for Three.js
function interpolateColorRGB(colors: string[], t: number): [number, number, number] {
    const n = colors.length - 1;
    const i = Math.floor(t * n);
    const f = t * n - i;

    if (i >= n) {
        const c = colors[n];
        return [parseInt(c.slice(1, 3), 16) / 255, parseInt(c.slice(3, 5), 16) / 255, parseInt(c.slice(5, 7), 16) / 255];
    }
    if (i < 0) {
        const c = colors[0];
        return [parseInt(c.slice(1, 3), 16) / 255, parseInt(c.slice(3, 5), 16) / 255, parseInt(c.slice(5, 7), 16) / 255];
    }

    const c1 = colors[i];
    const c2 = colors[i + 1];

    const r1 = parseInt(c1.slice(1, 3), 16) / 255;
    const g1 = parseInt(c1.slice(3, 5), 16) / 255;
    const b1 = parseInt(c1.slice(5, 7), 16) / 255;
    const r2 = parseInt(c2.slice(1, 3), 16) / 255;
    const g2 = parseInt(c2.slice(3, 5), 16) / 255;
    const b2 = parseInt(c2.slice(5, 7), 16) / 255;

    return [r1 + (r2 - r1) * f, g1 + (g2 - g1) * f, b1 + (b2 - b1) * f];
}

// 3D Thermal Surface Component - Uses actual geometry profile from backend
function ThermalSurface3D({ params, colormap, showCoolantChannels = true, nChannels = 12, profile }: {
    params: any,
    colormap: Colormap,
    showCoolantChannels?: boolean,
    nChannels?: number,
    profile?: { x: number[], r: number[] } | null
}) {
    const colors = colormaps[colormap];

    // Get radius from actual profile or use fallback
    const getRadius = useMemo(() => {
        if (profile && profile.x && profile.r && profile.x.length > 1) {
            // Use actual geometry profile from backend
            const xArr = profile.x;
            const rArr = profile.r;
            const xMax = xArr[xArr.length - 1];

            return (t: number) => {
                const xTarget = t * xMax;
                // Find the two points to interpolate between
                for (let i = 0; i < xArr.length - 1; i++) {
                    if (xTarget >= xArr[i] && xTarget <= xArr[i + 1]) {
                        const frac = (xTarget - xArr[i]) / (xArr[i + 1] - xArr[i]);
                        return rArr[i] + (rArr[i + 1] - rArr[i]) * frac;
                    }
                }
                return rArr[rArr.length - 1];
            };
        } else {
            // Fallback: hardcoded profile based on typical rocket motor
            return (t: number) => {
                const rThroat = 0.020;
                const contractionRatio = 3.5;
                const expansionRatio = 8.0;
                const rChamber = rThroat * Math.sqrt(contractionRatio);
                const rExit = rThroat * Math.sqrt(expansionRatio);

                // More realistic proportions: throat at ~40%
                const chamberEnd = 0.30;
                const throatStart = 0.38;
                const throatEnd = 0.42;

                if (t < chamberEnd) {
                    return rChamber;
                } else if (t < throatStart) {
                    const s = (t - chamberEnd) / (throatStart - chamberEnd);
                    const blend = (1.0 - Math.cos(s * Math.PI)) / 2.0;
                    return rChamber - (rChamber - rThroat) * blend;
                } else if (t < throatEnd) {
                    return rThroat;
                } else {
                    const s = (t - throatEnd) / (1.0 - throatEnd);
                    return rThroat + (rExit - rThroat) * Math.pow(2.0 * s - s * s, 0.85);
                }
            };
        }
    }, [profile]);

    const geometry = useMemo(() => {
        const lengthSegs = 60;
        const radialSegs = 48;

        const totalVerts = (lengthSegs + 1) * (radialSegs + 1);
        const positions = new Float32Array(totalVerts * 3);
        const vertColors = new Float32Array(totalVerts * 3);
        const indices: number[] = [];

        // Generate vertices
        for (let i = 0; i <= lengthSegs; i++) {
            const xFrac = i / lengthSegs;
            const x = (xFrac - 0.5) * 0.35;
            const radius = getRadius(xFrac);

            // Throat is at 0.60-0.62, so peak temperature at 0.61
            const throatPos = 0.61;
            const throatDist = Math.abs(xFrac - throatPos);
            const throatEffect = Math.exp(-throatDist * throatDist * 30);
            const baseTemp = params.t_cool + (params.t_hot - params.t_cool) * (0.3 + 0.7 * throatEffect);

            for (let j = 0; j <= radialSegs; j++) {
                const angle = (j / radialSegs) * Math.PI * 2;
                const idx = i * (radialSegs + 1) + j;

                positions[idx * 3] = x;
                positions[idx * 3 + 1] = Math.cos(angle) * radius;
                positions[idx * 3 + 2] = Math.sin(angle) * radius;

                const temp = baseTemp;
                const t_norm = (temp - params.t_cool) / (params.t_hot - params.t_cool);
                const [r, g, b] = interpolateColorRGB(colors, Math.max(0, Math.min(1, t_norm)));

                vertColors[idx * 3] = r;
                vertColors[idx * 3 + 1] = g;
                vertColors[idx * 3 + 2] = b;
            }
        }

        // Generate indices
        for (let i = 0; i < lengthSegs; i++) {
            for (let j = 0; j < radialSegs; j++) {
                const a = i * (radialSegs + 1) + j;
                const b = a + 1;
                const c = a + (radialSegs + 1);
                const d = c + 1;

                indices.push(a, c, b);
                indices.push(b, c, d);
            }
        }

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geo.setAttribute('color', new THREE.BufferAttribute(vertColors, 3));
        geo.setIndex(indices);
        geo.computeVertexNormals();

        return geo;
    }, [params, colors]);

    // Generate coolant channel positions
    const channelPositions = useMemo(() => {
        if (!showCoolantChannels) return [];

        const positions: Array<{ x: number, y: number, z: number, radius: number }> = [];
        const channelRadius = 0.004; // 4mm tubes
        const lengthSteps = 20;

        for (let c = 0; c < nChannels; c++) {
            const angle = (c / nChannels) * Math.PI * 2;

            for (let i = 0; i <= lengthSteps; i++) {
                const xFrac = i / lengthSteps;
                const x = (xFrac - 0.5) * 0.35;
                const nozzleRadius = getRadius(xFrac);
                const outerRadius = nozzleRadius + 0.008; // 8mm outside the wall

                positions.push({
                    x,
                    y: Math.cos(angle) * outerRadius,
                    z: Math.sin(angle) * outerRadius,
                    radius: channelRadius
                });
            }
        }
        return positions;
    }, [showCoolantChannels, nChannels]);

    return (
        <group>
            <OrbitControls autoRotate autoRotateSpeed={0.3} />
            <ambientLight intensity={0.4} />
            <pointLight position={[10, 10, 10]} intensity={1} />
            <pointLight position={[-10, -10, -10]} intensity={0.5} />

            {/* Thermal surface mesh */}
            <mesh geometry={geometry}>
                <meshStandardMaterial
                    vertexColors
                    side={THREE.DoubleSide}
                    roughness={0.6}
                    metalness={0.3}
                />
            </mesh>

            {/* Wireframe overlay */}
            <mesh geometry={geometry}>
                <meshBasicMaterial
                    color="#ffffff"
                    wireframe
                    transparent
                    opacity={0.05}
                />
            </mesh>

            {/* Coolant Channels - Cyan tubes */}
            {showCoolantChannels && channelPositions.map((pos, i) => (
                <mesh key={i} position={[pos.x, pos.y, pos.z]}>
                    <sphereGeometry args={[pos.radius, 6, 6]} />
                    <meshStandardMaterial
                        color="#00d4ff"
                        emissive="#00d4ff"
                        emissiveIntensity={0.2}
                        metalness={0.8}
                        roughness={0.2}
                    />
                </mesh>
            ))}

            {/* Axis labels - positions adjusted for new geometry */}
            <Html position={[0.17, 0, 0]} className="text-white text-xs font-bold">Sortie</Html>
            <Html position={[-0.17, 0, 0]} className="text-white text-xs font-bold">Chambre</Html>
            <Html position={[0.04, 0.04, 0]} className="text-[#ef4444] text-xs font-bold">Col</Html>

            {/* Temperature labels */}
            <Html position={[0, -0.12, 0]} className="text-xs bg-black/70 px-2 py-1 rounded">
                <div className="text-[#fca50a]">T max: {params.t_hot} K</div>
                <div className="text-[#00d4ff]">T min: {params.t_cool} K</div>
                {showCoolantChannels && <div className="text-[#00d4ff] text-[10px]">{nChannels} canaux</div>}
            </Html>
        </group>
    );
}

export default function ThermalPage() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [mode, setMode] = useState<ViewMode>("developpee");
    const [colormap, setColormap] = useState<Colormap>("inferno");
    const [resolution, setResolution] = useState(50);
    const [showIsotherms, setShowIsotherms] = useState(true);
    const [showMaterialLimits, setShowMaterialLimits] = useState(true);
    const [showFluxVectors, setShowFluxVectors] = useState(false);
    const [showCoolantChannels, setShowCoolantChannels] = useState(true);
    const [positionX, setPositionX] = useState(0);

    // Context for API calls
    const { results, solverResults, runSolver, loading, error } = useCalculation();

    // Thermal parameters - use calculated results if available
    const [params, setParams] = useState({
        t_gas: 3223,
        t_hot: 1225,
        t_cold: 1000,
        t_cool: 293,
        flux: 38.24,
        h_g: 19140,
        wall_thickness: 2.0,  // mm
        length: 350,  // mm
    });

    // Update params when solver results come in
    useEffect(() => {
        if (solverResults) {
            setParams(prev => ({
                ...prev,
                t_hot: solverResults.max_t_wall,
                t_cool: solverResults.t_out,
                flux: solverResults.max_q_flux,
            }));
        }
    }, [solverResults]);

    // Update params when main calculation results come in
    useEffect(() => {
        if (results) {
            setParams(prev => ({
                ...prev,
                t_gas: results.t_chamber,
                length: (results.l_chamber + results.l_nozzle) * 1000,  // m to mm
            }));
        }
    }, [results]);

    const drawHeatmap = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        const width = canvas.width;
        const height = canvas.height;
        const colors = colormaps[colormap];

        // Clear
        ctx.fillStyle = "#0a0a0f";
        ctx.fillRect(0, 0, width, height);

        if (mode === "radiale") {
            // Radial cross-section view (circular)
            const centerX = width / 2;
            const centerY = height / 2;
            const maxRadius = Math.min(width, height) * 0.45;
            const innerRadius = maxRadius * 0.6; // Gas side
            const outerRadius = maxRadius; // Coolant side

            // Draw circular heatmap
            const angularRes = 72; // Angular resolution
            const radialRes = 20; // Radial resolution

            for (let r = 0; r < radialRes; r++) {
                const rFrac = r / radialRes;
                const radius1 = innerRadius + rFrac * (outerRadius - innerRadius);
                const radius2 = innerRadius + (r + 1) / radialRes * (outerRadius - innerRadius);

                for (let a = 0; a < angularRes; a++) {
                    const angle1 = (a / angularRes) * Math.PI * 2;
                    const angle2 = ((a + 1) / angularRes) * Math.PI * 2;

                    // Temperature varies with radius (hot inside, cool outside)
                    // Also add some angular variation to simulate real conditions
                    const angularVar = 1 + 0.1 * Math.sin(a * 6 / angularRes * Math.PI * 2); const temp = params.t_hot - (params.t_hot - params.t_cool) * rFrac * angularVar;

                    const t_min = params.t_cool;
                    const t_max = params.t_hot;
                    const t_norm = (temp - t_min) / (t_max - t_min);

                    ctx.fillStyle = interpolateColor(colors, Math.max(0, Math.min(1, t_norm)));
                    ctx.beginPath();
                    ctx.arc(centerX, centerY, radius1, angle1, angle2);
                    ctx.arc(centerX, centerY, radius2, angle2, angle1, true);
                    ctx.closePath();
                    ctx.fill();
                }
            }

            // Draw circles for boundaries
            ctx.strokeStyle = "#00d4ff";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(centerX, centerY, innerRadius, 0, Math.PI * 2);
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(centerX, centerY, outerRadius, 0, Math.PI * 2);
            ctx.stroke();

            // Draw coolant channel markers
            if (showCoolantChannels) {
                const nChannels = 12;
                ctx.fillStyle = "rgba(0, 212, 255, 0.3)";
                ctx.strokeStyle = "#00d4ff";
                ctx.lineWidth = 1;
                for (let i = 0; i < nChannels; i++) {
                    const angle = (i / nChannels) * Math.PI * 2;
                    const x = centerX + Math.cos(angle) * (outerRadius + 15);
                    const y = centerY + Math.sin(angle) * (outerRadius + 15);
                    ctx.beginPath();
                    ctx.arc(x, y, 8, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.stroke();
                }
            }

            // Labels
            ctx.fillStyle = "#ffffff";
            ctx.font = "12px monospace";
            ctx.fillText("Côté gaz (intérieur)", centerX - 60, centerY);
            ctx.fillText("Position X: " + positionX.toFixed(0) + " mm", 10, 25);

            // Draw isotherms as concentric circles
            if (showIsotherms) {
                const isoTemps = [400, 600, 800, 1000, 1200];
                const t_min = params.t_cool;
                const t_max = params.t_hot;

                isoTemps.forEach((targetTemp) => {
                    if (targetTemp < t_min || targetTemp > t_max) return;

                    const t_norm = (targetTemp - t_min) / (t_max - t_min);
                    const isoRadius = outerRadius - t_norm * (outerRadius - innerRadius);

                    ctx.strokeStyle = `rgba(255, 255, 255, ${0.3 + t_norm * 0.4})`;
                    ctx.lineWidth = 1;
                    ctx.setLineDash([3, 3]);
                    ctx.beginPath();
                    ctx.arc(centerX, centerY, isoRadius, 0, Math.PI * 2);
                    ctx.stroke();
                    ctx.setLineDash([]);

                    // Label
                    ctx.fillStyle = "rgba(255, 255, 255, 0.6)";
                    ctx.font = "10px monospace";
                    ctx.fillText(`${targetTemp}K`, centerX + isoRadius + 5, centerY);
                });
            }

        } else {
            // Developpee mode (unrolled / flat view)
            const resX = resolution;
            const resY = Math.floor(resolution / 2);
            const cellW = width / resX;
            const cellH = height / resY;

            // Generate thermal gradient
            for (let j = 0; j < resY; j++) {
                for (let i = 0; i < resX; i++) {
                    const x = i / resX;  // 0 to 1 along length
                    const y = j / resY;  // 0 to 1 through thickness (0=coolant, 1=gas)

                    // Temperature varies: hot at throat (x~0.4), coolest at ends
                    const throatFactor = 1 - Math.abs(x - 0.4) * 1.5;
                    const throatEffect = Math.max(0, throatFactor);

                    // Temperature through wall thickness
                    const t_wall_hot = params.t_cold + (params.t_hot - params.t_cold) * throatEffect;
                    const t_wall_cold = params.t_cool + (t_wall_hot - params.t_cool) * 0.3;

                    // Linear interpolation through wall
                    const temp = t_wall_cold + (t_wall_hot - t_wall_cold) * y;

                    // Normalize to color range  
                    const t_min = params.t_cool;
                    const t_max = params.t_hot;
                    const t_norm = (temp - t_min) / (t_max - t_min);

                    ctx.fillStyle = interpolateColor(colors, Math.max(0, Math.min(1, t_norm)));
                    ctx.fillRect(i * cellW, (resY - 1 - j) * cellH, cellW + 1, cellH + 1);
                }
            }

            // Draw isotherms as smooth curves following the temperature field
            if (showIsotherms) {
                ctx.lineWidth = 1;

                // Temperature levels for isotherms
                const isoTemps = [400, 500, 600, 700, 800, 900, 1000, 1100, 1200];
                const t_min = params.t_cool;
                const t_max = params.t_hot;

                isoTemps.forEach((targetTemp) => {
                    if (targetTemp < t_min || targetTemp > t_max) return;

                    // Color based on temperature
                    const t_norm = (targetTemp - t_min) / (t_max - t_min);
                    ctx.strokeStyle = `rgba(255, 255, 255, ${0.3 + t_norm * 0.4})`;

                    ctx.beginPath();
                    let started = false;

                    // For each x position, find the y where temperature equals targetTemp
                    for (let i = 0; i <= resX; i++) {
                        const x_frac = i / resX;
                        const xPos = i * cellW;

                        // Calculate temperature profile at this x position
                        const throatDist = Math.abs(x_frac - 0.43);
                        const throatEffect = Math.exp(-throatDist * throatDist * 15);

                        const t_wall_hot = params.t_cold + (params.t_hot - params.t_cold) * (0.4 + 0.6 * throatEffect);
                        const t_wall_cold = params.t_cool + (t_wall_hot - params.t_cool) * 0.25;

                        const deltaT = t_wall_hot - t_wall_cold;
                        if (deltaT < 1) continue;

                        const y_norm = (targetTemp - t_wall_cold) / deltaT;

                        if (y_norm >= 0 && y_norm <= 1) {
                            const yPos = height * (1 - y_norm);

                            if (!started) {
                                ctx.moveTo(xPos, yPos);
                                started = true;
                            } else {
                                ctx.lineTo(xPos, yPos);
                            }
                        }
                    }
                    ctx.stroke();

                    // Draw temperature label at the end of the line
                    if (started) {
                        ctx.fillStyle = "rgba(255, 255, 255, 0.6)";
                        ctx.font = "10px monospace";
                        ctx.fillText(`${targetTemp}K`, width - 40, height * (1 - (targetTemp - t_min) / (t_max - t_min)));
                    }
                });
            }

            // Draw material limits (horizontal lines)
            if (showMaterialLimits) {
                ctx.strokeStyle = "#00d4ff";
                ctx.lineWidth = 2;
                ctx.setLineDash([5, 5]);

                ctx.beginPath();
                ctx.moveTo(0, 10);
                ctx.lineTo(width, 10);
                ctx.stroke();

                ctx.beginPath();
                ctx.moveTo(0, height - 10);
                ctx.lineTo(width, height - 10);
                ctx.stroke();

                ctx.setLineDash([]);
            }

            // Draw coolant channels
            if (showCoolantChannels) {
                ctx.strokeStyle = "#00d4ff";
                ctx.fillStyle = "rgba(0, 212, 255, 0.1)";
                ctx.lineWidth = 1;

                const nChannels = 12;
                const channelWidth = width / nChannels;

                for (let i = 0; i < nChannels; i++) {
                    const x = i * channelWidth + channelWidth * 0.2;
                    const w = channelWidth * 0.6;
                    ctx.fillRect(x, height - 30, w, 20);
                    ctx.strokeRect(x, height - 30, w, 20);
                }
            }

            // Draw position indicator
            const posXPixel = (positionX / params.length) * width;
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(posXPixel, 0);
            ctx.lineTo(posXPixel, height);
            ctx.stroke();

            // Labels
            ctx.fillStyle = "#ffffff";
            ctx.font = "12px monospace";
            ctx.fillText("Côté gaz", 10, 25);
            ctx.fillText("Côté coolant", 10, height - 35);
        }

    }, [mode, colormap, resolution, showIsotherms, showMaterialLimits, showFluxVectors, showCoolantChannels, positionX, params]);

    useEffect(() => {
        drawHeatmap();
    }, [drawHeatmap]);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (canvas) {
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            drawHeatmap();
        }
    }, [drawHeatmap]);

    return (
        <AppLayout>
            <div className="h-full flex flex-col overflow-hidden">
                {/* Header */}
                <div className="p-4 border-b border-[#27272a] flex-shrink-0">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-4">
                            <h1 className="text-xl font-bold text-[#00d4ff]">🔥 Carte Thermique 2D</h1>
                            {/* Solver Status */}
                            <div className="flex items-center gap-2">
                                {solverResults ? (
                                    <span className="text-xs px-2 py-1 bg-[#10b981]/20 text-[#10b981] rounded-full">
                                        ✓ Données réelles
                                    </span>
                                ) : (
                                    <span className="text-xs px-2 py-1 bg-[#f59e0b]/20 text-[#f59e0b] rounded-full">
                                        ~ Simulation
                                    </span>
                                )}
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={runSolver}
                                disabled={loading || !results}
                                className={`text-sm px-4 py-2 rounded-lg font-medium transition-all ${loading
                                    ? "bg-[#27272a] text-[#71717a] cursor-wait"
                                    : !results
                                        ? "bg-[#27272a] text-[#71717a] cursor-not-allowed"
                                        : "bg-[#8b5cf6] hover:bg-[#7c3aed] text-white"
                                    }`}
                            >
                                {loading ? "⏳ Calcul..." : "🧊 Lancer Solver"}
                            </button>
                            <button className="btn-secondary text-sm">💾</button>
                            <button className="btn-primary text-sm">Ouvrir Visualisation</button>
                        </div>
                    </div>
                    {error && (
                        <div className="text-xs text-[#ef4444] bg-[#ef4444]/10 px-3 py-2 rounded mb-2">
                            ⚠️ {error}
                        </div>
                    )}
                    {!results && (
                        <div className="text-xs text-[#f59e0b] bg-[#f59e0b]/10 px-3 py-2 rounded mb-2">
                            💡 Calculez d'abord le moteur sur la page principale pour activer le solver
                        </div>
                    )}

                    {/* Mode Selection */}
                    <div className="flex flex-wrap items-center gap-6 text-sm">
                        <div className="flex items-center gap-2">
                            <span className="text-[#71717a]">Mode:</span>
                            {(["radiale", "developpee", "3d"] as ViewMode[]).map((m) => (
                                <label key={m} className="flex items-center gap-1 cursor-pointer">
                                    <input
                                        type="radio"
                                        name="mode"
                                        checked={mode === m}
                                        onChange={() => setMode(m)}
                                        className="accent-[#00d4ff]"
                                    />
                                    <span className={mode === m ? "text-[#00d4ff]" : "text-[#a1a1aa]"}>
                                        {m === "radiale" ? "Coupe Radiale" : m === "developpee" ? "Développée" : "3D Surface"}
                                    </span>
                                </label>
                            ))}
                        </div>

                        <div className="flex items-center gap-2">
                            <span className="text-[#71717a]">Colormap:</span>
                            <select
                                value={colormap}
                                onChange={(e) => setColormap(e.target.value as Colormap)}
                                className="input-field py-1 px-2 text-sm"
                            >
                                {Object.keys(colormaps).map((cm) => (
                                    <option key={cm} value={cm}>{cm}</option>
                                ))}
                            </select>
                        </div>

                        <div className="flex items-center gap-2">
                            <span className="text-[#71717a]">Résolution:</span>
                            <input
                                type="number"
                                value={resolution}
                                onChange={(e) => setResolution(parseInt(e.target.value))}
                                className="input-field py-1 px-2 w-16 text-sm"
                                min={10}
                                max={200}
                            />
                        </div>
                    </div>

                    {/* Options */}
                    <div className="flex flex-wrap items-center gap-4 mt-3 text-sm">
                        {[
                            { label: "Isothermes", checked: showIsotherms, set: setShowIsotherms },
                            { label: "Limites matériau", checked: showMaterialLimits, set: setShowMaterialLimits },
                            { label: "Vecteurs flux", checked: showFluxVectors, set: setShowFluxVectors },
                            { label: "Canaux coolant", checked: showCoolantChannels, set: setShowCoolantChannels },
                        ].map((opt) => (
                            <label key={opt.label} className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={opt.checked}
                                    onChange={(e) => opt.set(e.target.checked)}
                                    className="w-4 h-4 rounded bg-[#1a1a25] border-[#27272a] accent-[#00d4ff]"
                                />
                                <span className="text-[#a1a1aa]">{opt.label}</span>
                            </label>
                        ))}

                        <div className="flex items-center gap-2 ml-4">
                            <span className="text-[#71717a]">Position X (mm):</span>
                            <input
                                type="range"
                                min={0}
                                max={params.length}
                                value={positionX}
                                onChange={(e) => setPositionX(parseInt(e.target.value))}
                                className="w-32 accent-[#00d4ff]"
                            />
                            <span className="text-[#00d4ff] font-mono">{positionX.toFixed(1)} mm</span>
                        </div>
                    </div>

                    {/* Thermal Values */}
                    <div className="flex flex-wrap gap-4 mt-3 text-xs font-mono">
                        <span className="text-[#ef4444]">T gaz: {params.t_gas.toFixed(0)} K</span>
                        <span className="text-[#f59e0b]">T hot: {params.t_hot.toFixed(0)} K</span>
                        <span className="text-[#eab308]">T cold: {params.t_cold.toFixed(0)} K</span>
                        <span className="text-[#00d4ff]">T cool: {params.t_cool.toFixed(0)} K</span>
                        <span className="text-white">Flux: {params.flux.toFixed(2)} MW/m²</span>
                        <span className="text-white">h_g: {params.h_g.toFixed(0)} W/m²K</span>
                    </div>

                    {/* Solver Results Panel */}
                    {solverResults && (
                        <div className="mt-3 p-3 bg-[#10b981]/10 border border-[#10b981]/30 rounded-lg">
                            <div className="text-xs font-semibold text-[#10b981] mb-2">📊 Résultats du Solver Thermique</div>
                            <div className="grid grid-cols-4 gap-3 text-xs font-mono">
                                <div>
                                    <span className="text-[#71717a]">Reynolds:</span>
                                    <span className="text-white ml-2">{solverResults.reynolds.toFixed(0)}</span>
                                </div>
                                <div>
                                    <span className="text-[#71717a]">h_coolant:</span>
                                    <span className="text-[#00d4ff] ml-2">{solverResults.h_coolant.toFixed(0)} W/m²K</span>
                                </div>
                                <div>
                                    <span className="text-[#71717a]">ΔP coolant:</span>
                                    <span className="text-[#f59e0b] ml-2">{solverResults.delta_p.toFixed(2)} bar</span>
                                </div>
                                <div>
                                    <span className="text-[#71717a]">T sortie:</span>
                                    <span className="text-[#8b5cf6] ml-2">{solverResults.t_out.toFixed(0)} K</span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Canvas / 3D View */}
                <div className="flex-1 flex overflow-hidden">
                    <div className="flex-1 relative p-4">
                        <div className="absolute inset-4 bg-[#0a0a0f] rounded-lg border border-[#27272a] overflow-hidden">
                            {mode === "3d" ? (
                                <>
                                    <Canvas camera={{ position: [0.4, 0.2, 0.4], fov: 45 }}>
                                        <ThermalSurface3D
                                            params={params}
                                            colormap={colormap}
                                            showCoolantChannels={showCoolantChannels}
                                            profile={results?.geometry_profile}
                                        />
                                    </Canvas>
                                    <div className="absolute bottom-4 right-4 text-xs text-[#71717a]">
                                        Drag to Rotate • Scroll to Zoom
                                    </div>
                                    <div className="absolute top-2 left-1/2 transform -translate-x-1/2 text-xs text-[#71717a]">
                                        Surface 3D - Tuyère avec température
                                    </div>
                                </>
                            ) : (
                                <>
                                    <canvas
                                        ref={canvasRef}
                                        className="w-full h-full"
                                        style={{ display: "block" }}
                                    />
                                    <div className="absolute top-2 left-1/2 transform -translate-x-1/2 text-xs text-[#71717a]">
                                        {mode === "radiale" ? "Coupe Radiale - Section transversale" : "Carte Thermique Développée - Température dans la paroi"}
                                    </div>
                                </>
                            )}
                        </div>
                    </div>

                    {/* Color Legend */}
                    <div className="w-20 p-4 flex flex-col items-center">
                        <div
                            className="w-6 flex-1 rounded"
                            style={{
                                background: `linear-gradient(to bottom, ${colormaps[colormap].slice().reverse().join(", ")})`
                            }}
                        />
                        <div className="mt-2 text-xs text-[#71717a] space-y-1 text-right w-full">
                            <div>{params.t_hot} K</div>
                            <div className="flex-1"></div>
                            <div>{params.t_cool} K</div>
                        </div>
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
