"use client";

import { useState, useRef, useMemo } from "react";
import AppLayout from "@/components/AppLayout";
import { useCalculation } from "@/contexts/CalculationContext";
import { Canvas } from "@react-three/fiber";
import * as THREE from "three";
import { trackActivity } from "@/lib/activity";

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

// Robust Heatmap Component with Mesh Support
function CFDHeatmap({ result, field, colormap }: { result: CFDResult; field: FieldType; colormap: string }) {
    const { positions, colors, indices, isMesh } = useMemo(() => {
        const nx = result.nx;
        const ny = result.ny;
        const fieldData = result[field];

        if (!fieldData || fieldData.length === 0) {
            return { positions: new Float32Array(0), colors: new Float32Array(0), indices: null, isMesh: false };
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

        if (!hasValid) { min = 0; max = 1; }
        if (max <= min) max = min + 1e-6;

        // 2. Generate Geometry
        const numPoints = result.x.length;
        const positions = new Float32Array(numPoints * 3);
        const colors = new Float32Array(numPoints * 3);

        const max_x = Math.max(...result.x) || 1;
        const scale = 20 / max_x;

        for (let i = 0; i < numPoints; i++) {
            // Position
            positions[i * 3] = result.x[i] * scale - 10;
            positions[i * 3 + 1] = result.r[i] * scale;
            positions[i * 3 + 2] = 0;

            // Color
            let val = fieldData[i];
            if (!Number.isFinite(val)) val = min;

            const t = (val - min) / (max - min);
            const color = getColorForValue(t, colormap);

            colors[i * 3] = color.r;
            colors[i * 3 + 1] = color.g;
            colors[i * 3 + 2] = color.b;
        }

        // 3. Generate Indices for Mesh
        let indices = null;
        let isMesh = false;

        if (nx > 1 && ny > 1 && nx * ny === numPoints) {
            const indexArray = [];
            // Assume Row-Major ordering: p = i*ny + j (x-slow, y-fast)
            for (let i = 0; i < nx - 1; i++) {
                for (let j = 0; j < ny - 1; j++) {
                    const a = i * ny + j;
                    const b = i * ny + j + 1;
                    const c = (i + 1) * ny + j;
                    const d = (i + 1) * ny + j + 1;

                    // Two triangles: a-d-b and a-c-d
                    indexArray.push(a, d, b);
                    indexArray.push(a, c, d);
                }
            }
            indices = new Uint16Array(indexArray);
            isMesh = true;
        }

        return { positions, colors, indices, isMesh };
    }, [result, field, colormap]);

    if (positions.length === 0) return null;

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    if (isMesh && indices) {
        geometry.setIndex(new THREE.BufferAttribute(indices, 1));
        return (
            <mesh>
                <bufferGeometry attach="geometry" {...geometry} />
                <meshBasicMaterial attach="material" vertexColors side={THREE.DoubleSide} />
            </mesh>
        );
    }

    return (
        <points>
            <bufferGeometry attach="geometry" {...geometry} />
            <pointsMaterial attach="material" vertexColors size={0.3} sizeAttenuation={true} />
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
        </svg>
    );
}

export default function CFDPage() {
    const { config: mainConfig, results } = useCalculation();
    const [status, setStatus] = useState<"idle" | "running" | "completed" | "error">("idle");
    const [logs, setLogs] = useState<string[]>([]);
    const [result, setResult] = useState<CFDResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [field, setField] = useState<FieldType>("mach");
    const [currentJobId, setCurrentJobId] = useState<string | null>(null);
    const [currentParams, setCurrentParams] = useState<Record<string, unknown> | null>(null);
    const [saving, setSaving] = useState(false);
    const [saveName, setSaveName] = useState("");
    const [showSaveDialog, setShowSaveDialog] = useState(false);

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
            // Use geometry from main calculation context, fallback to defaults
            const simParams = {
                r_throat: results?.r_throat || 0.025,
                r_chamber: results?.r_chamber || 0.05,
                r_exit: results?.r_exit || 0.075,
                l_chamber: results?.l_chamber || 0.1,
                l_nozzle: results?.l_nozzle || 0.2,
                p_chamber: mainConfig.pc * 1e5,
                p_ambient: mainConfig.pe * 1e5,
                t_chamber: results?.t_chamber || 3000,
                gamma: results?.gamma || 1.2,
                molar_mass: (results?.mw || 20) / 1000, // mw is in g/mol, convert to kg/mol
                nx: 200,  // High resolution for solid mesh rendering
                ny: 100,
                max_iter: 5000,
                mode: 1,
                solver: "openfoam"
            };

            addLog(`📝 Géométrie: Rt=${(simParams.r_throat * 1000).toFixed(1)}mm, Rc=${(simParams.r_chamber * 1000).toFixed(1)}mm, Re=${(simParams.r_exit * 1000).toFixed(1)}mm`);
            addLog(`📝 Longueurs: Lc=${(simParams.l_chamber * 1000).toFixed(0)}mm, Ln=${(simParams.l_nozzle * 1000).toFixed(0)}mm | Pc=${(simParams.p_chamber / 1e5).toFixed(1)}bar, Tc=${simParams.t_chamber.toFixed(0)}K`);
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
            setCurrentJobId(jobId);
            setCurrentParams(simParams);
            addLog(`✅ Job créé: ID ${jobId}`);

            let completed = false;
            let attempts = 0;
            const maxAttempts = 600;

            while (!completed && attempts < maxAttempts) {
                await new Promise(r => setTimeout(r, 2000));
                attempts++;

                const statusRes = await fetch(`${OPENFOAM_API}/status?jobId=${jobId}`, {
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
            const resultRes = await fetch(`${OPENFOAM_API}/result?jobId=${jobId}`, {
                signal: abortControllerRef.current.signal
            });

            if (!resultRes.ok) throw new Error("Erreur récupération résultats");

            const resultData = await resultRes.json();
            setResult(resultData);
            setStatus("completed");
            addLog("✨ Résultats chargés !");
            
            // Track the CFD analysis
            trackActivity("cfd_run", {
                jobId,
                converged: resultData.converged,
                iterations: resultData.iterations
            });

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

    const saveSimulation = async () => {
        if (!result || !saveName.trim()) return;
        
        setSaving(true);
        try {
            const response = await fetch("/api/cfd/save", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: saveName.trim(),
                    description: `Simulation OpenFOAM - ${currentJobId}`,
                    jobId: currentJobId,
                    params: currentParams,
                    result: result
                })
            });
            
            if (response.ok) {
                addLog("💾 Simulation sauvegardée avec succès !");
                setShowSaveDialog(false);
                setSaveName("");
            } else {
                const data = await response.json();
                addLog(`❌ Erreur sauvegarde: ${data.error}`);
            }
        } catch (err: any) {
            addLog(`❌ Erreur sauvegarde: ${err.message}`);
        } finally {
            setSaving(false);
        }
    };

    const exportResults = () => {
        if (!result) return;
        
        const exportData = {
            jobId: currentJobId,
            params: currentParams,
            result: result,
            exportedAt: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cfd-simulation-${currentJobId || 'export'}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        addLog("📁 Résultats exportés en JSON !");
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
                        {result && (
                            <>
                                <button
                                    onClick={() => setShowSaveDialog(true)}
                                    className="px-4 py-2 rounded font-bold bg-green-600 hover:bg-green-500 text-white transition-all"
                                >
                                    💾 Sauvegarder
                                </button>
                                <button
                                    onClick={exportResults}
                                    className="px-4 py-2 rounded font-bold bg-purple-600 hover:bg-purple-500 text-white transition-all"
                                >
                                    📁 Exporter JSON
                                </button>
                            </>
                        )}
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

                {/* Save Dialog */}
                {showSaveDialog && (
                    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                        <div className="bg-[#1a1a25] rounded-lg border border-[#27272a] p-6 w-96">
                            <h3 className="text-lg font-bold mb-4">💾 Sauvegarder la Simulation</h3>
                            <input
                                type="text"
                                value={saveName}
                                onChange={(e) => setSaveName(e.target.value)}
                                placeholder="Nom de la simulation..."
                                className="w-full px-4 py-2 bg-[#0a0a0f] border border-[#27272a] rounded mb-4 text-white"
                                autoFocus
                            />
                            <div className="flex gap-3 justify-end">
                                <button
                                    onClick={() => setShowSaveDialog(false)}
                                    className="px-4 py-2 rounded bg-gray-700 hover:bg-gray-600 text-white"
                                >
                                    Annuler
                                </button>
                                <button
                                    onClick={saveSimulation}
                                    disabled={!saveName.trim() || saving}
                                    className="px-4 py-2 rounded bg-green-600 hover:bg-green-500 text-white disabled:opacity-50"
                                >
                                    {saving ? "Sauvegarde..." : "Sauvegarder"}
                                </button>
                            </div>
                        </div>
                    </div>
                )}

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
