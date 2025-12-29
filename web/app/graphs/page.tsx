"use client";

import { useState, useMemo } from "react";
import dynamic from "next/dynamic";
import AppLayout from "@/components/AppLayout";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, AreaChart, Area, ScatterChart, Scatter, ZAxis } from "recharts";

const Motor3DViewer = dynamic(() => import("@/components/Motor3DViewer"), { ssr: false });

type PlotType = "isp_of" | "isp_pc" | "thrust_mdot" | "cf_eps" | "tc_of" | "twall_x" | "hg_x" | "stress_pc" | "geometry" | "3d";

const plotDefinitions: { key: PlotType; label: string; xAxis: string; yAxis: string; color: string }[] = [
    { key: "isp_of", label: "Isp vs O/F", xAxis: "O/F Ratio", yAxis: "Isp (s)", color: "#00d4ff" },
    { key: "isp_pc", label: "Isp vs Pc", xAxis: "Pc (bar)", yAxis: "Isp (s)", color: "#8b5cf6" },
    { key: "thrust_mdot", label: "Poussée vs Débit", xAxis: "ṁ (kg/s)", yAxis: "F (N)", color: "#10b981" },
    { key: "cf_eps", label: "Cf vs ε", xAxis: "Ratio d'expansion", yAxis: "Cf", color: "#f59e0b" },
    { key: "tc_of", label: "T chambre vs O/F", xAxis: "O/F Ratio", yAxis: "Tc (K)", color: "#ef4444" },
    { key: "twall_x", label: "T paroi vs Position", xAxis: "x (mm)", yAxis: "Twall (K)", color: "#ec4899" },
    { key: "hg_x", label: "hg vs Position", xAxis: "x (mm)", yAxis: "hg (W/m²K)", color: "#06b6d4" },
    { key: "stress_pc", label: "Contrainte vs Pc", xAxis: "Pc (bar)", yAxis: "σ (MPa)", color: "#a855f7" },
    { key: "geometry", label: "Profil Géométrique", xAxis: "x (mm)", yAxis: "r (mm)", color: "#3b82f6" },
    { key: "3d", label: "Vue 3D", xAxis: "-", yAxis: "-", color: "#ffffff" },
];

export default function GraphsPage() {
    const [selectedPlot, setSelectedPlot] = useState<PlotType>("isp_of");

    // Parameters
    const [params, setParams] = useState({
        pc: 25,      // bar
        of_min: 1.5,
        of_max: 4.5,
        eps_min: 5,
        eps_max: 100,
        mdot: 0.5,
        tc: 3300,
        gamma: 1.2,
        mw: 24,
    });

    // Generate data based on selected plot
    const chartData = useMemo(() => {
        const data = [];

        switch (selectedPlot) {
            case "isp_of":
                for (let of = params.of_min; of <= params.of_max; of += 0.1) {
                    // Simplified Isp model (peak around stoichiometric)
                    const peak_of = 2.8;
                    const isp = 340 - 30 * Math.pow((of - peak_of) / 1.5, 2);
                    data.push({ x: of.toFixed(1), y: isp.toFixed(1), of });
                }
                break;

            case "isp_pc":
                for (let pc = 5; pc <= 100; pc += 5) {
                    // Isp increases with Pc (log relationship)
                    const isp = 300 + 30 * Math.log10(pc);
                    data.push({ x: pc, y: isp.toFixed(1) });
                }
                break;

            case "thrust_mdot":
                for (let mdot = 0.1; mdot <= 5; mdot += 0.1) {
                    const isp = 330;
                    const thrust = mdot * isp * 9.81;
                    data.push({ x: mdot.toFixed(1), y: thrust.toFixed(0) });
                }
                break;

            case "cf_eps":
                for (let eps = params.eps_min; eps <= params.eps_max; eps += 5) {
                    // Cf increases with expansion ratio
                    const gamma = params.gamma;
                    const pr = Math.pow(2 / (gamma + 1), gamma / (gamma - 1));
                    const cf = Math.sqrt(2 * gamma * gamma / (gamma - 1) * pr * (1 - Math.pow(1 / eps, (gamma - 1) / gamma)));
                    data.push({ x: eps, y: (cf + 0.95).toFixed(3) });
                }
                break;

            case "tc_of":
                for (let of = params.of_min; of <= params.of_max; of += 0.1) {
                    // Tc peaks near stoichiometric
                    const peak_of = 3.0;
                    const tc = 3300 - 200 * Math.pow((of - peak_of) / 1.5, 2);
                    data.push({ x: of.toFixed(1), y: tc.toFixed(0) });
                }
                break;

            case "twall_x":
                for (let x = 0; x <= 350; x += 5) {
                    // Temperature profile along nozzle
                    const throat_x = 150;
                    const areaRatio = x < throat_x ? 3 - 2 * x / throat_x : 1 + 40 * (x - throat_x) / 200;
                    const hg = 5000 / Math.pow(areaRatio, 0.9);
                    const twall = 500 + hg * (params.tc - 500) / 15000;
                    data.push({ x, y: twall.toFixed(0), hg: hg.toFixed(0) });
                }
                break;

            case "hg_x":
                for (let x = 0; x <= 350; x += 5) {
                    const throat_x = 150;
                    const areaRatio = x < throat_x ? 3 - 2 * x / throat_x : 1 + 40 * (x - throat_x) / 200;
                    const hg = 5000 / Math.pow(areaRatio, 0.9);
                    data.push({ x, y: hg.toFixed(0), ar: areaRatio.toFixed(2) });
                }
                break;

            case "stress_pc":
                for (let pc = 5; pc <= 100; pc += 5) {
                    const r = 0.025; // m
                    const e = 0.002; // m
                    const sigma = (pc * 1e5 * r) / e / 1e6;
                    data.push({ x: pc, y: sigma.toFixed(1) });
                }
                break;

            case "geometry":
                for (let i = 0; i <= 100; i++) {
                    const x = i * 3.5;
                    const t = i / 100;
                    let r = 0;
                    if (t < 0.4) {
                        r = 55;
                    } else if (t < 0.5) {
                        const s = (t - 0.4) / 0.1;
                        r = 55 - (55 - 25) * Math.sin(s * Math.PI / 2);
                    } else {
                        const s = (t - 0.5) / 0.5;
                        r = 25 + (110 - 25) * Math.sqrt(s);
                    }
                    data.push({ x: x.toFixed(0), r: r.toFixed(1), rNeg: (-r).toFixed(1) });
                }
                break;
        }

        return data;
    }, [selectedPlot, params]);

    const currentPlot = plotDefinitions.find(p => p.key === selectedPlot)!;

    return (
        <AppLayout>
            <div className="flex h-full overflow-hidden">
                {/* Left Panel - Plot Selection */}
                <div className="w-64 bg-[#12121a] border-r border-[#27272a] flex flex-col flex-shrink-0">
                    <div className="p-4 border-b border-[#27272a]">
                        <h1 className="text-lg font-bold text-white">📈 Graphiques</h1>
                        <p className="text-xs text-[#71717a]">Analyses paramétriques</p>
                    </div>

                    <div className="flex-1 overflow-y-auto">
                        <div className="p-2">
                            <p className="text-xs text-[#52525b] uppercase px-2 py-1">Performance</p>
                            {plotDefinitions.slice(0, 5).map((plot) => (
                                <button
                                    key={plot.key}
                                    onClick={() => setSelectedPlot(plot.key)}
                                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all mb-1 ${selectedPlot === plot.key ? "bg-[#1a1a25] text-white" : "text-[#a1a1aa] hover:bg-[#1a1a25]"
                                        }`}
                                >
                                    <span className="w-3 h-3 rounded-full inline-block mr-2" style={{ backgroundColor: plot.color }}></span>
                                    {plot.label}
                                </button>
                            ))}

                            <p className="text-xs text-[#52525b] uppercase px-2 py-1 mt-3">Thermique</p>
                            {plotDefinitions.slice(5, 8).map((plot) => (
                                <button
                                    key={plot.key}
                                    onClick={() => setSelectedPlot(plot.key)}
                                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all mb-1 ${selectedPlot === plot.key ? "bg-[#1a1a25] text-white" : "text-[#a1a1aa] hover:bg-[#1a1a25]"
                                        }`}
                                >
                                    <span className="w-3 h-3 rounded-full inline-block mr-2" style={{ backgroundColor: plot.color }}></span>
                                    {plot.label}
                                </button>
                            ))}

                            <p className="text-xs text-[#52525b] uppercase px-2 py-1 mt-3">Géométrie</p>
                            {plotDefinitions.slice(8).map((plot) => (
                                <button
                                    key={plot.key}
                                    onClick={() => setSelectedPlot(plot.key)}
                                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all mb-1 ${selectedPlot === plot.key ? "bg-[#1a1a25] text-white" : "text-[#a1a1aa] hover:bg-[#1a1a25]"
                                        }`}
                                >
                                    <span className="w-3 h-3 rounded-full inline-block mr-2" style={{ backgroundColor: plot.color }}></span>
                                    {plot.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Parameters */}
                    <div className="p-3 border-t border-[#27272a] space-y-2">
                        <p className="text-xs font-bold text-[#a1a1aa] uppercase">Paramètres</p>
                        <div className="grid grid-cols-2 gap-2 text-xs">
                            <div>
                                <label className="text-[#71717a]">Pc</label>
                                <input type="number" value={params.pc} onChange={(e) => setParams({ ...params, pc: parseFloat(e.target.value) })} className="input-field w-full py-1" />
                            </div>
                            <div>
                                <label className="text-[#71717a]">Tc</label>
                                <input type="number" value={params.tc} onChange={(e) => setParams({ ...params, tc: parseFloat(e.target.value) })} className="input-field w-full py-1" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Panel - Chart */}
                <div className="flex-1 p-6 overflow-y-auto">
                    <div className="max-w-4xl mx-auto">
                        <h2 className="text-2xl font-bold text-white mb-2">{currentPlot.label}</h2>
                        <p className="text-sm text-[#71717a] mb-6">{currentPlot.xAxis} → {currentPlot.yAxis}</p>

                        <div className="card">
                            <div className="h-[500px]">
                                {selectedPlot === "3d" ? (
                                    <Motor3DViewer height={480} />
                                ) : selectedPlot === "geometry" ? (
                                    <ResponsiveContainer width="100%" height="100%">
                                        <LineChart data={chartData}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                                            <XAxis dataKey="x" stroke="#71717a" label={{ value: "x (mm)", position: "bottom", fill: "#71717a" }} />
                                            <YAxis stroke="#71717a" />
                                            <Tooltip contentStyle={{ backgroundColor: '#1a1a25', border: '1px solid #27272a' }} />
                                            <Line type="monotone" dataKey="r" stroke={currentPlot.color} strokeWidth={2} dot={false} name="R+" />
                                            <Line type="monotone" dataKey="rNeg" stroke={currentPlot.color} strokeWidth={2} dot={false} name="R-" />
                                        </LineChart>
                                    </ResponsiveContainer>
                                ) : (
                                    <ResponsiveContainer width="100%" height="100%">
                                        <AreaChart data={chartData}>
                                            <defs>
                                                <linearGradient id={`gradient-${selectedPlot}`} x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="5%" stopColor={currentPlot.color} stopOpacity={0.3} />
                                                    <stop offset="95%" stopColor={currentPlot.color} stopOpacity={0} />
                                                </linearGradient>
                                            </defs>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                                            <XAxis dataKey="x" stroke="#71717a" label={{ value: currentPlot.xAxis, position: "bottom", fill: "#71717a" }} />
                                            <YAxis stroke="#71717a" label={{ value: currentPlot.yAxis, angle: -90, position: "left", fill: "#71717a" }} />
                                            <Tooltip contentStyle={{ backgroundColor: '#1a1a25', border: '1px solid #27272a' }} />
                                            <Area type="monotone" dataKey="y" stroke={currentPlot.color} strokeWidth={2} fill={`url(#gradient-${selectedPlot})`} name={currentPlot.yAxis} />
                                        </AreaChart>
                                    </ResponsiveContainer>
                                )}
                            </div>
                        </div>

                        {/* Data Summary */}
                        <div className="grid grid-cols-4 gap-4 mt-6">
                            <div className="card p-4 text-center">
                                <p className="text-xs text-[#71717a]">Min</p>
                                <p className="text-xl font-bold text-white">{chartData.length > 0 ? Math.min(...chartData.map(d => parseFloat(d.y || d.r || "0"))).toFixed(1) : "-"}</p>
                            </div>
                            <div className="card p-4 text-center">
                                <p className="text-xs text-[#71717a]">Max</p>
                                <p className="text-xl font-bold" style={{ color: currentPlot.color }}>{chartData.length > 0 ? Math.max(...chartData.map(d => parseFloat(d.y || d.r || "0"))).toFixed(1) : "-"}</p>
                            </div>
                            <div className="card p-4 text-center">
                                <p className="text-xs text-[#71717a]">Points</p>
                                <p className="text-xl font-bold text-white">{chartData.length}</p>
                            </div>
                            <div className="card p-4 text-center">
                                <p className="text-xs text-[#71717a]">Range X</p>
                                <p className="text-xl font-bold text-white">{chartData.length > 0 ? `${chartData[0].x} - ${chartData[chartData.length - 1].x}` : "-"}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
