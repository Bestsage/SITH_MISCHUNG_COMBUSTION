"use client";

import { useState, useRef, useEffect } from "react";
import AppLayout from "@/components/AppLayout";
import { useCalculation } from "@/contexts/CalculationContext";

// Types matching Rust backend
interface CFDResult {
    converged: boolean;
    iterations: number;
    mach: number[];
    pressure: number[];
    temperature: number[];
    x: number[];
    r: number[];
    residual_history?: number[];
}

export default function CFDPage() {
    const { params: mainConfig } = useCalculation();
    const [status, setStatus] = useState<"idle" | "running" | "completed" | "error">("idle");
    const [logs, setLogs] = useState<string[]>([]);
    const [result, setResult] = useState<CFDResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const abortControllerRef = useRef<AbortController | null>(null);

    // Direct access to OpenFOAM container (bypassing potentially slow Next.js proxy if needed/configured)
    // Using the one from env or falling back to relative path which goes through Next.js rewrite
    const OPENFOAM_API = process.env.NEXT_PUBLIC_OPENFOAM_URL || "/api/cfd";

    const addLog = (message: string) => {
        setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
    };

    const runSimulation = async () => {
        if (status === "running") return;

        setStatus("running");
        setLogs([]); // Clear previous logs
        setResult(null);
        setError(null);

        addLog("🚀 Initialisation de la simulation...");

        // Cancel previous request if any
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
        }
        abortControllerRef.current = new AbortController();

        try {
            // 1. Prepare parameters from context
            const simParams = {
                r_throat: 0.025, // Default or from context if available
                r_chamber: 0.05,
                r_exit: 0.075,
                l_chamber: 0.1,
                l_nozzle: 0.2,
                p_chamber: mainConfig.pc * 1e5, // bar -> Pa
                p_ambient: mainConfig.pe * 1e5, // bar -> Pa
                t_chamber: 3000,
                gamma: 1.2,
                molar_mass: 0.02,
                nx: 100,
                ny: 50,
                max_iter: 5000,
                mode: 1, // Quick mode by default
                solver: "openfoam"
            };

            addLog(`📝 Paramètres: Pc=${(simParams.p_chamber / 1e5).toFixed(1)}bar, Tc=${simParams.t_chamber}K`);
            addLog("📡 Envoi de la demande au serveur...");

            // 2. Start Simulation
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

            // 3. Poll Status
            let completed = false;
            let attempts = 0;
            const maxAttempts = 600; // 20 minutes (2s interval)

            while (!completed && attempts < maxAttempts) {
                await new Promise(r => setTimeout(r, 2000));
                attempts++;

                const statusRes = await fetch(`${OPENFOAM_API}/status/${jobId}`, {
                    signal: abortControllerRef.current.signal
                });

                if (!statusRes.ok) throw new Error("Erreur vérification status");

                const statusData = await statusRes.json();

                // Show progress
                if (statusData.status === "running") {
                    const progress = (statusData.progress * 100).toFixed(1);
                    // Only log every 10% or so to avoid spamming? Or just update last log line?
                    // For now, simple log
                    if (attempts % 5 === 0) { // Log every 10s
                        addLog(`⏳ En cours... ${progress}% (${statusData.message})`);
                    }
                } else if (statusData.status === "completed") {
                    completed = true;
                    addLog("🏁 Simulation terminée avec succès !");
                } else if (statusData.status === "failed") {
                    throw new Error(`Simulation échouée: ${statusData.message}`);
                }
            }

            if (!completed) throw new Error("Timeout: La simulation prend trop de temps.");

            // 4. Get Results
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
                <header>
                    <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-600">
                        OpenFOAM Simulation Runner
                    </h1>
                    <p className="text-gray-400 text-sm">Interface de diagnostic simplifiée</p>
                </header>

                {/* Controls */}
                <div className="flex gap-4 items-center">
                    <button
                        onClick={runSimulation}
                        disabled={status === "running"}
                        className={`px-6 py-3 rounded font-bold transition-all ${status === "running"
                                ? "bg-gray-700 cursor-not-allowed text-gray-400"
                                : "bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/20"
                            }`}
                    >
                        {status === "running" ? "Simulation en cours..." : "🚀 Lancer Simulation"}
                    </button>

                    {status === "running" && (
                        <div className="animate-spin h-5 w-5 border-2 border-cyan-500 border-t-transparent rounded-full"></div>
                    )}
                </div>

                {/* Main Content Area */}
                <div className="flex flex-1 gap-6 min-h-0">
                    {/* Logs Console */}
                    <div className="flex-1 bg-[#1a1a25] rounded-lg border border-[#27272a] p-4 flex flex-col font-mono text-xs">
                        <h2 className="text-gray-400 font-bold mb-2 uppercase border-b border-[#27272a] pb-2">Logs de Simulation</h2>
                        <div className="flex-1 overflow-y-auto space-y-1">
                            {logs.length === 0 && <span className="text-gray-600 italic">En attente de démarrage...</span>}
                            {logs.map((log, i) => (
                                <div key={i} className="text-gray-300 border-b border-[#27272a]/30 pb-0.5">{log}</div>
                            ))}
                        </div>
                    </div>

                    {/* Results Panel */}
                    <div className="w-96 bg-[#1a1a25] rounded-lg border border-[#27272a] p-4 flex flex-col">
                        <h2 className="text-gray-400 font-bold mb-2 uppercase border-b border-[#27272a] pb-2">Résultats</h2>

                        {error && (
                            <div className="p-3 bg-red-900/30 border border-red-500/50 rounded text-red-300 text-sm mb-4">
                                {error}
                            </div>
                        )}

                        {result ? (
                            <div className="space-y-4 text-sm">
                                <div className="grid grid-cols-2 gap-2">
                                    <div className="p-2 bg-[#0a0a0f] rounded">
                                        <div className="text-gray-500 text-xs">Itérations</div>
                                        <div className="text-cyan-400 font-bold">{result.iterations}</div>
                                    </div>
                                    <div className="p-2 bg-[#0a0a0f] rounded">
                                        <div className="text-gray-500 text-xs">Convergé</div>
                                        <div className={result.converged ? "text-green-400 font-bold" : "text-orange-400 font-bold"}>
                                            {result.converged ? "OUI" : "NON"}
                                        </div>
                                    </div>
                                </div>

                                <div className="p-3 bg-[#0a0a0f] rounded border border-[#27272a]">
                                    <h3 className="text-gray-400 text-xs uppercase mb-2">Données Max / Min</h3>
                                    <ul className="space-y-1">
                                        <li className="flex justify-between">
                                            <span>Mach Max:</span>
                                            <span className="text-purple-400">{Math.max(...(result.mach || [0])).toFixed(2)}</span>
                                        </li>
                                        <li className="flex justify-between">
                                            <span>Pression Min:</span>
                                            <span className="text-orange-400">{(Math.min(...(result.pressure || [0])) / 1e5).toFixed(2)} bar</span>
                                        </li>
                                        <li className="flex justify-between">
                                            <span>Temp Max:</span>
                                            <span className="text-red-400">{Math.max(...(result.temperature || [0])).toFixed(0)} K</span>
                                        </li>
                                    </ul>
                                </div>

                                <div className="text-xs text-gray-500 mt-4 text-center">
                                    Les données brutes sont disponibles dans la console du navigateur.
                                </div>
                            </div>
                        ) : (
                            <div className="flex-1 flex items-center justify-center text-gray-600 text-sm italic">
                                Aucun résultat disponible
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
