"use client";

import { useState } from "react";
import AppLayout from "@/components/AppLayout";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function CoolingPage() {
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<any>(null);

    const [params, setParams] = useState({
        // Geometry
        r_throat: 0.025,      // m (25mm)
        l_chamber: 0.15,      // m
        l_nozzle: 0.20,       // m
        // Channels
        n_channels: 48,
        channel_width: 2.5,   // mm
        channel_depth: 3.0,   // mm
        wall_thickness: 1.5,  // mm
        // Conditions
        pc: 25,               // bar
        t_chamber: 3300,      // K
        coolant_mdot: 0.4,    // kg/s total
        coolant_p_inlet: 35,  // bar
        coolant_t_inlet: 300, // K
        k_wall: 340,          // W/m·K (cuivre)
    });

    const runSolver = async () => {
        setLoading(true);
        try {
            const res = await fetch("http://localhost:8000/api/solve", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    geometry: {
                        r_throat: params.r_throat,
                        l_chamber: params.l_chamber,
                        l_nozzle: params.l_nozzle,
                        n_channels: params.n_channels,
                        channel_width: params.channel_width / 1000,  // Convert mm to m
                        channel_depth: params.channel_depth / 1000,
                        wall_thickness: params.wall_thickness / 1000,
                    },
                    conditions: {
                        p_inlet: params.coolant_p_inlet * 1e5,  // bar to Pa
                        t_inlet: params.coolant_t_inlet,
                        m_dot: params.coolant_mdot,
                        pc: params.pc * 1e5,
                        mr: 2.8,
                        k_wall: params.k_wall,
                    }
                })
            });
            const data = await res.json();
            if (data.status === "success") {
                setResults(data.data);
            }
        } catch (e) {
            console.error("Solver failed:", e);
        } finally {
            setLoading(false);
        }
    };

    // Calculate hydraulics
    const w = params.channel_width / 1000;  // m
    const h = params.channel_depth / 1000;  // m
    const A_channel = w * h;
    const P_wet = 2 * (w + h);
    const D_h = 4 * A_channel / P_wet * 1000;  // mm
    const m_dot_channel = params.coolant_mdot / params.n_channels;
    const rho_cool = 800;  // kg/m³ (RP-1)
    const v_cool = m_dot_channel / (rho_cool * A_channel);

    // Chart data
    const chartData = results ? results.x.map((x: number, i: number) => ({
        x: (x * 1000).toFixed(0),
        t_wall: results.t_wall[i]?.toFixed(0) || 0,
        t_coolant: results.t_coolant[i]?.toFixed(0) || 0,
        q_flux: results.q_flux[i]?.toFixed(2) || 0,
    })) : [];

    return (
        <AppLayout>
            <div className="p-6 h-full overflow-y-auto">
                <div className="mb-6">
                    <h1 className="text-2xl font-bold text-white">❄️ Analyse de Refroidissement</h1>
                    <p className="text-sm text-[#71717a]">Simulation thermique des canaux régénératifs</p>
                </div>

                <div className="grid grid-cols-12 gap-6">
                    {/* Config Panel */}
                    <div className="col-span-12 lg:col-span-3 space-y-4">
                        <div className="card">
                            <h3 className="card-header">📐 Géométrie</h3>
                            <div className="space-y-3">
                                {[
                                    { label: "R col", key: "r_throat", unit: "m", step: 0.001 },
                                    { label: "L chambre", key: "l_chamber", unit: "m", step: 0.01 },
                                    { label: "L tuyère", key: "l_nozzle", unit: "m", step: 0.01 },
                                ].map(({ label, key, unit, step }) => (
                                    <div key={key} className="flex items-center justify-between">
                                        <label className="text-xs text-[#a1a1aa]">{label}</label>
                                        <div className="flex items-center gap-1">
                                            <input
                                                type="number"
                                                step={step}
                                                value={(params as any)[key]}
                                                onChange={(e) => setParams({ ...params, [key]: parseFloat(e.target.value) })}
                                                className="input-field w-20 text-xs text-right py-1"
                                            />
                                            <span className="text-[10px] text-[#71717a] w-6">{unit}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="card">
                            <h3 className="card-header">🔧 Canaux</h3>
                            <div className="space-y-3">
                                {[
                                    { label: "N canaux", key: "n_channels", unit: "", step: 1 },
                                    { label: "Largeur", key: "channel_width", unit: "mm", step: 0.1 },
                                    { label: "Profondeur", key: "channel_depth", unit: "mm", step: 0.1 },
                                    { label: "Épaisseur paroi", key: "wall_thickness", unit: "mm", step: 0.1 },
                                    { label: "k paroi", key: "k_wall", unit: "W/m·K", step: 1 },
                                ].map(({ label, key, unit, step }) => (
                                    <div key={key} className="flex items-center justify-between">
                                        <label className="text-xs text-[#a1a1aa]">{label}</label>
                                        <div className="flex items-center gap-1">
                                            <input
                                                type="number"
                                                step={step}
                                                value={(params as any)[key]}
                                                onChange={(e) => setParams({ ...params, [key]: parseFloat(e.target.value) })}
                                                className="input-field w-16 text-xs text-right py-1"
                                            />
                                            <span className="text-[10px] text-[#71717a] w-12">{unit}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="card">
                            <h3 className="card-header">💧 Coolant</h3>
                            <div className="space-y-3">
                                {[
                                    { label: "Débit total", key: "coolant_mdot", unit: "kg/s", step: 0.01 },
                                    { label: "P entrée", key: "coolant_p_inlet", unit: "bar", step: 1 },
                                    { label: "T entrée", key: "coolant_t_inlet", unit: "K", step: 1 },
                                    { label: "Pc chambre", key: "pc", unit: "bar", step: 1 },
                                ].map(({ label, key, unit, step }) => (
                                    <div key={key} className="flex items-center justify-between">
                                        <label className="text-xs text-[#a1a1aa]">{label}</label>
                                        <div className="flex items-center gap-1">
                                            <input
                                                type="number"
                                                step={step}
                                                value={(params as any)[key]}
                                                onChange={(e) => setParams({ ...params, [key]: parseFloat(e.target.value) })}
                                                className="input-field w-16 text-xs text-right py-1"
                                            />
                                            <span className="text-[10px] text-[#71717a] w-10">{unit}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <button onClick={runSolver} disabled={loading} className="btn-primary w-full">
                            {loading ? "⏳ Calcul..." : "🔥 CALCULER THERMIQUE"}
                        </button>
                    </div>

                    {/* Results */}
                    <div className="col-span-12 lg:col-span-9 space-y-4">
                        {/* Hydraulics Stats */}
                        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                            <div className="card p-3 text-center">
                                <p className="text-[10px] text-[#71717a] uppercase">Section canal</p>
                                <p className="text-lg font-bold text-white">{(A_channel * 1e6).toFixed(2)}<span className="text-xs text-[#71717a]">mm²</span></p>
                            </div>
                            <div className="card p-3 text-center">
                                <p className="text-[10px] text-[#71717a] uppercase">Dh</p>
                                <p className="text-lg font-bold text-[#00d4ff]">{D_h.toFixed(2)}<span className="text-xs text-[#71717a]">mm</span></p>
                            </div>
                            <div className="card p-3 text-center">
                                <p className="text-[10px] text-[#71717a] uppercase">v coolant</p>
                                <p className="text-lg font-bold text-[#8b5cf6]">{v_cool.toFixed(1)}<span className="text-xs text-[#71717a]">m/s</span></p>
                            </div>
                            <div className="card p-3 text-center">
                                <p className="text-[10px] text-[#71717a] uppercase">Reynolds</p>
                                <p className="text-lg font-bold text-[#f59e0b]">{results?.reynolds?.toFixed(0) || "-"}</p>
                            </div>
                            <div className="card p-3 text-center">
                                <p className="text-[10px] text-[#71717a] uppercase">ΔP total</p>
                                <p className="text-lg font-bold text-[#ef4444]">{results?.delta_p?.toFixed(2) || "-"}<span className="text-xs text-[#71717a]">bar</span></p>
                            </div>
                        </div>

                        {results ? (
                            <>
                                {/* Summary Cards */}
                                <div className="grid grid-cols-4 gap-3">
                                    <div className="card p-4 border-l-4 border-[#ef4444]">
                                        <p className="text-xs text-[#71717a]">T paroi max</p>
                                        <p className="text-2xl font-bold text-[#ef4444]">{results.max_t_wall?.toFixed(0)} K</p>
                                    </div>
                                    <div className="card p-4 border-l-4 border-[#f59e0b]">
                                        <p className="text-xs text-[#71717a]">q flux max</p>
                                        <p className="text-2xl font-bold text-[#f59e0b]">{results.max_q_flux?.toFixed(2)} MW/m²</p>
                                    </div>
                                    <div className="card p-4 border-l-4 border-[#00d4ff]">
                                        <p className="text-xs text-[#71717a]">T coolant out</p>
                                        <p className="text-2xl font-bold text-[#00d4ff]">{results.t_out?.toFixed(0)} K</p>
                                    </div>
                                    <div className="card p-4 border-l-4 border-[#10b981]">
                                        <p className="text-xs text-[#71717a]">h coolant</p>
                                        <p className="text-2xl font-bold text-[#10b981]">{results.h_coolant?.toFixed(0)} W/m²·K</p>
                                    </div>
                                </div>

                                {/* Temperature Chart */}
                                <div className="card">
                                    <h3 className="card-header">🌡️ Profil de Température</h3>
                                    <div className="h-64">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <LineChart data={chartData}>
                                                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                                                <XAxis dataKey="x" stroke="#71717a" fontSize={10} label={{ value: 'x (mm)', position: 'bottom', fill: '#71717a' }} />
                                                <YAxis stroke="#71717a" fontSize={10} label={{ value: 'T (K)', angle: -90, position: 'left', fill: '#71717a' }} />
                                                <Tooltip contentStyle={{ backgroundColor: '#1a1a25', border: '1px solid #27272a' }} />
                                                <Legend />
                                                <Line type="monotone" dataKey="t_wall" stroke="#ef4444" strokeWidth={2} name="T paroi" dot={false} />
                                                <Line type="monotone" dataKey="t_coolant" stroke="#00d4ff" strokeWidth={2} name="T coolant" dot={false} />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>

                                {/* Heat Flux Chart */}
                                <div className="card">
                                    <h3 className="card-header">🔥 Flux Thermique</h3>
                                    <div className="h-48">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <LineChart data={chartData}>
                                                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                                                <XAxis dataKey="x" stroke="#71717a" fontSize={10} />
                                                <YAxis stroke="#71717a" fontSize={10} label={{ value: 'q (MW/m²)', angle: -90, position: 'left', fill: '#71717a' }} />
                                                <Tooltip contentStyle={{ backgroundColor: '#1a1a25', border: '1px solid #27272a' }} />
                                                <Line type="monotone" dataKey="q_flux" stroke="#f59e0b" strokeWidth={2} name="Flux thermique" dot={false} />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <div className="card h-64 flex items-center justify-center">
                                <div className="text-center">
                                    <span className="text-4xl mb-3 block">❄️</span>
                                    <p className="text-white font-medium">Prêt à simuler</p>
                                    <p className="text-xs text-[#71717a]">Cliquez sur CALCULER pour lancer la simulation thermique</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
