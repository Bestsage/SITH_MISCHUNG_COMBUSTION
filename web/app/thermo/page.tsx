"use client";

import { useState, useEffect } from "react";
import AppLayout from "@/components/AppLayout";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function ThermoPage() {
    const [solverResults, setSolverResults] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const runSolver = async () => {
        setLoading(true);
        try {
            const res = await fetch("http://localhost:8000/api/solve", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    geometry: {
                        r_throat: 0.03,
                        l_chamber: 0.15,
                        l_nozzle: 0.20,
                        n_channels: 48,
                        channel_width: 0.003,
                        channel_depth: 0.003,
                        wall_thickness: 0.001
                    },
                    conditions: {
                        p_inlet: 60e5,
                        t_inlet: 300,
                        m_dot: 5.0,
                        pc: 50e5,
                        mr: 2.5,
                        k_wall: 340
                    }
                })
            });
            const data = await res.json();
            setSolverResults(data.data);
        } catch (e) {
            console.error("Solver failed:", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        runSolver();
    }, []);

    // Prepare chart data
    const chartData = solverResults ?
        solverResults.x.map((x: number, i: number) => ({
            x: (x * 1000).toFixed(0),
            T_wall: solverResults.t_wall[i],
            T_coolant: solverResults.t_coolant[i],
        })) : [];

    const pressureData = solverResults ?
        solverResults.x.map((x: number, i: number) => ({
            x: (x * 1000).toFixed(0),
            P_coolant: solverResults.p_coolant[i] / 1e5,
        })) : [];

    return (
        <AppLayout>
            <div className="p-8">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-white mb-2">Analyse Thermique</h1>
                        <p className="text-[#71717a]">Profils de température et pression le long du moteur</p>
                    </div>
                    <button onClick={runSolver} disabled={loading} className="btn-primary">
                        {loading ? "⏳ Calcul..." : "🔄 Recalculer"}
                    </button>
                </div>

                {solverResults ? (
                    <div className="space-y-6">
                        {/* Summary Stats */}
                        <div className="grid grid-cols-4 gap-4">
                            <div className="stat-card">
                                <p className="text-xs text-[#ef4444] uppercase tracking-wider mb-1">T paroi max</p>
                                <p className="stat-value">{solverResults.max_t_wall?.toFixed(0)}<span className="stat-unit">K</span></p>
                            </div>
                            <div className="stat-card">
                                <p className="text-xs text-[#00d4ff] uppercase tracking-wider mb-1">T coolant sortie</p>
                                <p className="stat-value">{solverResults.t_out?.toFixed(0)}<span className="stat-unit">K</span></p>
                            </div>
                            <div className="stat-card">
                                <p className="text-xs text-[#8b5cf6] uppercase tracking-wider mb-1">P sortie</p>
                                <p className="stat-value">{(solverResults.p_out / 1e5)?.toFixed(1)}<span className="stat-unit">bar</span></p>
                            </div>
                            <div className="stat-card">
                                <p className="text-xs text-[#f59e0b] uppercase tracking-wider mb-1">ΔT coolant</p>
                                <p className="stat-value">{(solverResults.t_out - 300)?.toFixed(0)}<span className="stat-unit">K</span></p>
                            </div>
                        </div>

                        {/* Temperature Chart */}
                        <div className="card">
                            <h3 className="card-header">🌡️ Profil de Température</h3>
                            <div style={{ height: 400 }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                                        <XAxis
                                            dataKey="x"
                                            stroke="#71717a"
                                            label={{ value: 'Position (mm)', position: 'insideBottom', offset: -10, fill: '#71717a' }}
                                        />
                                        <YAxis
                                            stroke="#71717a"
                                            label={{ value: 'Température (K)', angle: -90, position: 'insideLeft', fill: '#71717a' }}
                                        />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#15151f', borderColor: '#27272a', borderRadius: '8px' }}
                                            labelStyle={{ color: '#a1a1aa' }}
                                        />
                                        <Legend />
                                        <Line type="monotone" dataKey="T_wall" stroke="#ef4444" strokeWidth={2} name="Paroi" dot={false} />
                                        <Line type="monotone" dataKey="T_coolant" stroke="#00d4ff" strokeWidth={2} name="Coolant" dot={false} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Pressure Chart */}
                        <div className="card">
                            <h3 className="card-header">📊 Profil de Pression Coolant</h3>
                            <div style={{ height: 300 }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={pressureData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                                        <XAxis
                                            dataKey="x"
                                            stroke="#71717a"
                                            label={{ value: 'Position (mm)', position: 'insideBottom', offset: -10, fill: '#71717a' }}
                                        />
                                        <YAxis
                                            stroke="#71717a"
                                            label={{ value: 'Pression (bar)', angle: -90, position: 'insideLeft', fill: '#71717a' }}
                                        />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#15151f', borderColor: '#27272a', borderRadius: '8px' }}
                                        />
                                        <Line type="monotone" dataKey="P_coolant" stroke="#8b5cf6" strokeWidth={2} name="Pression" dot={false} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="card text-center py-20">
                        <span className="text-5xl mb-4 block animate-spin">⏳</span>
                        <p className="text-[#71717a]">Chargement des résultats thermiques...</p>
                    </div>
                )}
            </div>
        </AppLayout>
    );
}
