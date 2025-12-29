"use client";

import { useState, useEffect } from "react";
import AppLayout from "@/components/AppLayout";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function CoolingPage() {
    const [geometryData, setGeometryData] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const [params, setParams] = useState({
        n_channels: 48,
        channel_width: 3,
        channel_depth: 3,
        wall_thickness: 1,
        coolant_mdot: 5,
        coolant_p_inlet: 60,
        coolant_t_inlet: 300,
    });

    const generateGeometry = async () => {
        setLoading(true);
        try {
            const res = await fetch("http://localhost:8000/api/geometry/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    r_throat: 0.03,
                    l_chamber: 0.15,
                    l_nozzle: 0.20,
                    contraction_ratio: 3.0,
                    expansion_ratio: 40.0,
                    theta_conv: 30.0,
                    theta_div: 15.0,
                    nozzle_type: "conical"
                })
            });
            const data = await res.json();
            setGeometryData(data);
        } catch (e) {
            console.error("Geometry generation failed:", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        generateGeometry();
    }, []);

    const chartData = geometryData ?
        geometryData.x.map((x: number, i: number) => ({
            x: (x * 1000).toFixed(0),
            r: geometryData.r[i] * 1000,
            r_neg: -geometryData.r[i] * 1000,
        })) : [];

    return (
        <AppLayout>
            <div className="p-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Système de Refroidissement</h1>
                    <p className="text-[#71717a]">Configuration des canaux de refroidissement régénératif</p>
                </div>

                <div className="grid grid-cols-12 gap-6">
                    {/* Config Panel */}
                    <div className="col-span-12 lg:col-span-4 space-y-6">
                        <div className="card">
                            <h3 className="card-header">⚙️ Paramètres Canaux</h3>
                            <div className="space-y-4">
                                <div className="form-group">
                                    <label className="input-label">Nombre de canaux</label>
                                    <input
                                        type="number"
                                        value={params.n_channels}
                                        onChange={(e) => setParams({ ...params, n_channels: parseInt(e.target.value) })}
                                        className="input-field"
                                    />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="form-group">
                                        <label className="input-label">Largeur (mm)</label>
                                        <input
                                            type="number"
                                            step="0.1"
                                            value={params.channel_width}
                                            onChange={(e) => setParams({ ...params, channel_width: parseFloat(e.target.value) })}
                                            className="input-field"
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label className="input-label">Profondeur (mm)</label>
                                        <input
                                            type="number"
                                            step="0.1"
                                            value={params.channel_depth}
                                            onChange={(e) => setParams({ ...params, channel_depth: parseFloat(e.target.value) })}
                                            className="input-field"
                                        />
                                    </div>
                                </div>
                                <div className="form-group">
                                    <label className="input-label">Épaisseur paroi (mm)</label>
                                    <input
                                        type="number"
                                        step="0.1"
                                        value={params.wall_thickness}
                                        onChange={(e) => setParams({ ...params, wall_thickness: parseFloat(e.target.value) })}
                                        className="input-field"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="card">
                            <h3 className="card-header">💧 Conditions Coolant</h3>
                            <div className="space-y-4">
                                <div className="form-group">
                                    <label className="input-label">Débit (kg/s)</label>
                                    <input
                                        type="number"
                                        step="0.1"
                                        value={params.coolant_mdot}
                                        onChange={(e) => setParams({ ...params, coolant_mdot: parseFloat(e.target.value) })}
                                        className="input-field"
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="input-label">P entrée (bar)</label>
                                    <input
                                        type="number"
                                        value={params.coolant_p_inlet}
                                        onChange={(e) => setParams({ ...params, coolant_p_inlet: parseFloat(e.target.value) })}
                                        className="input-field"
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="input-label">T entrée (K)</label>
                                    <input
                                        type="number"
                                        value={params.coolant_t_inlet}
                                        onChange={(e) => setParams({ ...params, coolant_t_inlet: parseFloat(e.target.value) })}
                                        className="input-field"
                                    />
                                </div>
                            </div>
                        </div>

                        <button onClick={generateGeometry} disabled={loading} className="btn-primary w-full">
                            {loading ? "⏳ Génération..." : "🔄 Régénérer Géométrie"}
                        </button>
                    </div>

                    {/* Visualization */}
                    <div className="col-span-12 lg:col-span-8 space-y-6">
                        {/* Stats */}
                        <div className="grid grid-cols-3 gap-4">
                            <div className="stat-card">
                                <p className="text-xs text-[#00d4ff] uppercase tracking-wider mb-1">Section canal</p>
                                <p className="stat-value">{(params.channel_width * params.channel_depth).toFixed(1)}<span className="stat-unit">mm²</span></p>
                            </div>
                            <div className="stat-card">
                                <p className="text-xs text-[#8b5cf6] uppercase tracking-wider mb-1">Périmètre mouillé</p>
                                <p className="stat-value">{(2 * (params.channel_width + params.channel_depth)).toFixed(1)}<span className="stat-unit">mm</span></p>
                            </div>
                            <div className="stat-card">
                                <p className="text-xs text-[#10b981] uppercase tracking-wider mb-1">Dh</p>
                                <p className="stat-value">{(4 * params.channel_width * params.channel_depth / (2 * (params.channel_width + params.channel_depth))).toFixed(2)}<span className="stat-unit">mm</span></p>
                            </div>
                        </div>

                        {/* Geometry Chart */}
                        <div className="card">
                            <h3 className="card-header">📐 Profil Géométrique</h3>
                            <div style={{ height: 400 }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                                        <XAxis
                                            dataKey="x"
                                            stroke="#71717a"
                                            label={{ value: 'Position (mm)', position: 'insideBottom', offset: -10, fill: '#71717a' }}
                                        />
                                        <YAxis
                                            stroke="#71717a"
                                            label={{ value: 'Rayon (mm)', angle: -90, position: 'insideLeft', fill: '#71717a' }}
                                        />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#15151f', borderColor: '#27272a', borderRadius: '8px' }}
                                        />
                                        <Area type="monotone" dataKey="r" stroke="#00d4ff" fill="#00d4ff" fillOpacity={0.3} />
                                        <Area type="monotone" dataKey="r_neg" stroke="#00d4ff" fill="#00d4ff" fillOpacity={0.3} />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
