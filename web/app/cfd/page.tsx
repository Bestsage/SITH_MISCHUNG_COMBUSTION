"use client";

import { useState, useRef, useMemo } from "react";
import AppLayout from "@/components/AppLayout";
import { useCalculation } from "@/contexts/CalculationContext";
import { Canvas } from "@react-three/fiber";
import * as THREE from "three";

// Types matching Rust backend
interface CFDResult {
    converged: boolean;
    iterations: number;
    mach: number[];
    pressure: number[];
    temperature: number[];
    velocity_x: number[];
    density: number[];
    x: number[];
    r: number[];
    nx: number;
    ny: number;
    residual_history?: number[];
}

type FieldType = "mach" | "pressure" | "temperature" | "velocity_x" | "density";

const FIELD_CONFIG: Record<FieldType, { name: string; unit: string; colormap: string }> = {
    mach: { name: "Nombre de Mach", unit: "", colormap: "plasma" },
    pressure: { name: "Pression", unit: "Pa", colormap: "viridis" },
    temperature: { name: "Température", unit: "K", colormap: "inferno" },
    velocity_x: { name: "Vitesse Axiale", unit: "m/s", colormap: "coolwarm" },
    density: { name: "Densité", unit: "kg/m³", colormap: "magma" },
};

// Robust Color Mapping
function getColorForValue(t: number, colormap: string): THREE.Color {
    const color = new THREE.Color();
    // Clamp t to [0, 1] and handle NaN
    t = Math.max(0, Math.min(1, Number.isFinite(t) ? t : 0));

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
            if (t < 0.5) color.setHSL(0.6, 0.8, 0.4 + (0.5 - t) * 0.4);
            else color.setHSL(0.0, 0.8, 0.4 + (t - 0.5) * 0.4);
            break;
        case "magma":
            color.setHSL(0.85 - t * 0.15, 0.9, 0.1 + t * 0.6);
            break;
        default:
            color.setHSL(0.7 - t * 0.7, 1, 0.5);
    }
    return color;
}

// Robust Heatmap Component
function CFDHeatmap({ result, field, colormap }: { result: CFDResult; field: FieldType; colormap: string }) {
    const { positions, colors } = useMemo(() => {
        const nx = result.nx;
        const ny = result.ny;
        const fieldData = result[field];

        if (!fieldData || fieldData.length === 0) {
            return { positions: new Float32Array(0), colors: new Float32Array(0) };
        }

        // 1. Calculate Min/Max robustly
        let min = Infinity, max = -Infinity;
        let hasValid = false;

        for (const v of fieldData) {
            if (Number.isFinite(v)) {
                if (v < min) min = v;
                if (v > max) max = v;
                hasValid = true;
            }
        }

        // Fallback for full invalid data
        if (!hasValid) { min = 0; max = 1; }
        if (max <= min) max = min + 1e-6; // Prevent div by zero

        // 2. Generate Geometry
        const numPoints = result.x.length; // result.x is flattened
        const positions = new Float32Array(numPoints * 3);
        const colors = new Float32Array(numPoints * 3);

        const max_x = Math.max(...result.x) || 1;
        const scale = 20 / max_x; // Fit to view

        for (let i = 0; i < numPoints; i++) {
            // Position
            positions[i * 3] = result.x[i] * scale - 10;
            positions[i * 3 + 1] = result.r[i] * scale;
            positions[i * 3 + 2] = 0;

            // Color
            let val = fieldData[i];
            // Replace NaN/Inf with min value
            if (!Number.isFinite(val)) val = min;

            const t = (val - min) / (max - min);
            const color = getColorForValue(t, colormap);

            colors[i * 3] = color.r;
            colors[i * 3 + 1] = color.g;
            colors[i * 3 + 2] = color.b;
        }

        return { positions, colors };
    }, [result, field, colormap]);

    if (positions.length === 0) return null;

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    return (
        <points>
            <bufferGeometry attach="geometry" {...geometry} />
            <pointsMaterial attach="material" vertexColors size={0.15} sizeAttenuation={true} />
        </points>
    );
}

// Simple Residual Plot (SVG)
function ResidualPlot({ history }: { history: number[] }) {
    if (!history || history.length < 2) return <div className="text-gray-500 text-xs italic">Pas de données de convergence</div>;

    const width = 100;
    const height = 50;
    const padding = 5;

    // Log scale for residuals
    const logValues = history.map(v => Math.log10(Math.max(v, 1e-10)));
    const min = Math.min(...logValues);
    const max = Math.max(...logValues);
    const range = max - min || 1;

    const points = logValues.map((val, i) => {
        const x = padding + (i / (history.length - 1)) * (width - 2 * padding);
        const y = height - (padding + ((val - min) / range) * (height - 2 * padding));
        return `${x},${y}`;
    }).join(" ");

    return (
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full">
            <polyline points={points} fill="none" stroke="#06b6d4" strokeWidth="1.5" />
            {/* Grid line at target residual 1e-5 (-5 log) */}
            {/* <line x1={0} y1={height/2} x2={width} y2={height/2} stroke="#333" strokeDasharray="2,2" /> */}
        </svg>
    );
}

export default function CFDPage() {
    const { config: mainConfig } = useCalculation();
    const [status, setStatus] = useState<"idle" | "running" | "completed" | "error">("idle");
    const [logs, setLogs] = useState<string[]>([]);
    const [result, setResult] = useState<CFDResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [field, setField] = useState<FieldType>("mach");

    const abortControllerRef = useRef<AbortController | null>(null);
    const OPENFOAM_API = process.env.NEXT_PUBLIC_OPENFOAM_URL || "/api/cfd";

    const addLog = (message: string) => {
        setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
    };

    const runSimulation = async () => {
        if (status === "running") return;

        setStatus("running");
        setLogs([]);
        setResult(null);
        setError(null);

        addLog("🚀 Initialisation de la simulation...");

        if (abortControllerRef.current) abortControllerRef.current.abort();
        abortControllerRef.current = new AbortController();

        try {
            const simParams = {
                r_throat: 0.025,
                r_chamber: 0.05,
                r_exit: 0.075,
                l_chamber: 0.1,
                l_nozzle: 0.2,
                p_chamber: mainConfig.pc * 1e5,
                p_ambient: mainConfig.pe * 1e5,
                t_chamber: 3000,
                gamma: 1.2,
                molar_mass: 0.02,
                nx: 100,
                ny: 50,
                max_iter: 5000,
                mode: 1,
                solver: "openfoam"
            };

            addLog(`📝 Paramètres: Pc=${(simParams.p_chamber / 1e5).toFixed(1)}bar, Tc=${simParams.t_chamber}K`);
            addLog("📡 Envoi de la demande au serveur...");

            const startResponse = await fetch(`${OPENFOAM_API}/run`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(simParams),
                signal: abortControllerRef.current.signal,
            });

            if (!startResponse.ok) {
                const text = await startResponse.text();
                throw new Error(`Erreur démarrage (${startResponse.status}): ${text}`);
            }

            const jobInfo = await startResponse.json();
            const jobId = jobInfo.job_id;
            addLog(`✅ Job créé: ID ${jobId}`);

            let completed = false;
            let attempts = 0;
            const maxAttempts = 600;

            while (!completed && attempts < maxAttempts) {
                await new Promise(r => setTimeout(r, 2000));
                attempts++;

                const statusRes = await fetch(`${OPENFOAM_API}/status/${jobId}`, {
                    signal: abortControllerRef.current.signal
                });

                if (!statusRes.ok) throw new Error("Erreur vérification status");

                const statusData = await statusRes.json();

                if (statusData.status === "running") {
                    if (attempts % 5 === 0) {
                        addLog(`⏳ En cours... ${(statusData.progress * 100).toFixed(1)}%`);
                    }
                } else if (statusData.status === "completed") {
                    completed = true;
                    addLog("🏁 Simulation terminée avec succès !");
                } else if (statusData.status === "failed") {
                    throw new Error(`Simulation échouée: ${statusData.message}`);
                }
            }

            if (!completed) throw new Error("Timeout: La simulation prend trop de temps.");

            addLog("📥 Téléchargement des résultats...");
            const resultRes = await fetch(`${OPENFOAM_API}/result/${jobId}`, {
                signal: abortControllerRef.current.signal
            });

            if (!resultRes.ok) throw new Error("Erreur récupération résultats");

            const resultData = await resultRes.json();
            setResult(resultData);
            setStatus("completed");
            addLog("✨ Résultats chargés !");

        } catch (err: any) {
            if (err.name === 'AbortError') {
                addLog("🛑 Simulation annulée.");
                setStatus("idle");
            } else {
                console.error(err);
                setError(err.message || "Erreur inconnue");
                addLog(`❌ Erreur: ${err.message}`);
                setStatus("error");
            }
        }
    };

    return (
        <AppLayout>
            <div className="flex flex-col h-screen bg-[#0a0a0f] text-white p-6 gap-6">
                <header className="flex justify-between items-end">
                    <div>
                        <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-600">
                            OpenFOAM Simulation Runner
                        </h1>
                        <p className="text-gray-400 text-sm">Interface de diagnostic simplifiée & Visualisation</p>
                    </div>
                    {/* Controls */}
                    <div className="flex gap-4 items-center">
                        <button
                            onClick={runSimulation}
                            disabled={status === "running"}
                            className={`px-6 py-2 rounded font-bold transition-all ${status === "running"
                                    ? "bg-gray-700 cursor-not-allowed text-gray-400"
                                    : "bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/20"
                                }`}
                        >
                            {status === "running" ? "Simulation en cours..." : "🚀 Lancer Simulation"}
                        </button>
                    </div>
                </header>

                {/* Main Content Area */}
                <div className="flex flex-1 gap-6 min-h-0">
                    {/* Left: Logs & Details */}
                    <div className="w-1/3 flex flex-col gap-6">
                        {/* Logs Console */}
                        <div className="flex-1 bg-[#1a1a25] rounded-lg border border-[#27272a] p-4 flex flex-col font-mono text-xs shadow-inner">
                            <h2 className="text-gray-400 font-bold mb-2 uppercase border-b border-[#27272a] pb-2">Logs de Simulation</h2>
                            <div className="flex-1 overflow-y-auto space-y-1">
                                {logs.length === 0 && <span className="text-gray-600 italic">En attente de démarrage...</span>}
                                {logs.map((log, i) => (
                                    <div key={i} className="text-gray-300 border-b border-[#27272a]/30 pb-0.5">{log}</div>
                                ))}
                            </div>
                        </div>

                        {/* Quick Stats */}
                        {result && (
                            <div className="bg-[#1a1a25] rounded-lg border border-[#27272a] p-4 shrink-0">
                                <h2 className="text-gray-400 font-bold mb-3 uppercase text-xs">Performance</h2>
                                <div className="grid grid-cols-2 gap-3 mb-4">
                                    <div className="bg-[#0a0a0f] p-2 rounded">
                                        <div className="text-gray-500 text-[10px] uppercase">Mach Max</div>
                                        <div className="text-purple-400 font-bold text-lg">{Math.max(...(result.mach || [0])).toFixed(2)}</div>
                                    </div>
                                    <div className="bg-[#0a0a0f] p-2 rounded">
                                        <div className="text-gray-500 text-[10px] uppercase">Pression Min</div>
                                        <div className="text-orange-400 font-bold text-lg">{(Math.min(...(result.pressure || [0])) / 1e5).toFixed(2)} bar</div>
                                    </div>
                                </div>

                                <h2 className="text-gray-400 font-bold mb-1 uppercase text-xs">Convergence</h2>
                                <div className="h-16 w-full bg-[#0a0a0f] rounded relative">
                                    <ResidualPlot history={result.residual_history || []} />
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Right: Visualization */}
                    <div className="flex-1 bg-[#1a1a25] rounded-lg border border-[#27272a] p-4 flex flex-col relative overflow-hidden">
                        <div className="flex justify-between items-center mb-4 z-10">
                            <h2 className="text-gray-400 font-bold uppercase">Visualisation 2D</h2>

                            {/* Field Selector */}
                            <div className="flex bg-[#0a0a0f] rounded p-1 border border-[#27272a]">
                                {(Object.keys(FIELD_CONFIG) as FieldType[]).map((f) => (
                                    <button
                                        key={f}
                                        onClick={() => setField(f)}
                                        className={`px-3 py-1 rounded text-xs font-bold transition-all ${field === f ? "bg-cyan-600 text-white" : "text-gray-400 hover:text-white"
                                            }`}
                                    >
                                        {FIELD_CONFIG[f].name}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="flex-1 bg-[#0a0a0f] rounded border border-[#27272a] relative">
                            {result ? (
                                <>
                                    <Canvas orthographic camera={{ zoom: 25, position: [0, 0, 50] }}>
                                        <color attach="background" args={["#0a0a0f"]} />
                                        <CFDHeatmap
                                            result={result}
                                            field={field}
                                            colormap={FIELD_CONFIG[field].colormap}
                                        />
                                    </Canvas>

                                    {/* Legend Overlay */}
                                    <div className="absolute bottom-4 right-4 bg-black/80 p-2 rounded border border-gray-800 backdrop-blur-sm">
                                        <div className="text-gray-300 text-xs font-bold mb-1">{FIELD_CONFIG[field].unit || "Sans unité"}</div>
                                        <div className="w-32 h-3 bg-gradient-to-r from-blue-900 to-yellow-500 rounded-sm opacity-80"></div>
                                        <div className="flex justify-between text-[10px] text-gray-500 mt-1 font-mono">
                                            <span>Min</span>
                                            <span>Max</span>
                                        </div>
                                    </div>
                                </>
                            ) : (
                                <div className="flex items-center justify-center h-full text-gray-600 italic">
                                    En attente de résultats...
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
