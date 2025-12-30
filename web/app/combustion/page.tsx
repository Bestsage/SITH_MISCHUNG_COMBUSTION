"use client";

import { useState } from "react";
import AppLayout from "@/components/AppLayout";

export default function CombustionPage() {
    const [ceaParams, setCeaParams] = useState({
        fuel: "RP-1",
        oxidizer: "LOX",
        of_ratio: 2.5,
        pc: 50.0,
        expansion_ratio: 40.0,
    });
    const [results, setResults] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const calculateCEA = async () => {
        setLoading(true);
        try {
            const res = await fetch("http://localhost:8000/api/cea/calculate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(ceaParams)
            });
            const data = await res.json();
            setResults(data);
        } catch (e) {
            console.error("CEA calculation failed:", e);
        } finally {
            setLoading(false);
        }
    };

    const propellantPresets = [
        { name: "LOX/RP-1", ox: "LOX", fuel: "RP-1", of: 2.5 },
        { name: "LOX/LH2", ox: "LOX", fuel: "LH2", of: 6.0 },
        { name: "LOX/CH4", ox: "LOX", fuel: "CH4", of: 3.5 },
        { name: "N2O4/UDMH", ox: "N2O4", fuel: "UDMH", of: 2.6 },
        { name: "H2O2/RP-1", ox: "H2O2(L)", fuel: "RP-1", of: 7.0 },
        { name: "LOX/Propane", ox: "LOX", fuel: "C3H8", of: 2.8 },
    ];

    return (
        <AppLayout>
            <div className="p-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Combustion & NASA CEA</h1>
                    <p className="text-[#71717a]">Calculs thermochimiques avec le code NASA CEA</p>
                </div>

                <div className="grid grid-cols-12 gap-6">
                    {/* Input Panel */}
                    <div className="col-span-12 lg:col-span-4 space-y-6">
                        {/* Presets */}
                        <div className="card">
                            <h3 className="card-header">🚀 Presets Propergols</h3>
                            <div className="grid grid-cols-2 gap-2">
                                {propellantPresets.map((preset) => (
                                    <button
                                        key={preset.name}
                                        onClick={() => setCeaParams({
                                            ...ceaParams,
                                            oxidizer: preset.ox,
                                            fuel: preset.fuel,
                                            of_ratio: preset.of
                                        })}
                                        className={`btn-secondary text-xs py-2 ${ceaParams.oxidizer === preset.ox && ceaParams.fuel === preset.fuel
                                                ? 'border-[#00d4ff] text-[#00d4ff]' : ''
                                            }`}
                                    >
                                        {preset.name}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Custom Input */}
                        <div className="card">
                            <h3 className="card-header">⚗️ Paramètres CEA</h3>
                            <div className="space-y-4">
                                <div className="form-group">
                                    <label className="input-label">Oxydant (nom CEA)</label>
                                    <input
                                        type="text"
                                        value={ceaParams.oxidizer}
                                        onChange={(e) => setCeaParams({ ...ceaParams, oxidizer: e.target.value })}
                                        className="input-field"
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="input-label">Carburant (nom CEA)</label>
                                    <input
                                        type="text"
                                        value={ceaParams.fuel}
                                        onChange={(e) => setCeaParams({ ...ceaParams, fuel: e.target.value })}
                                        className="input-field"
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="input-label">Ratio O/F</label>
                                    <input
                                        type="number"
                                        step="0.1"
                                        value={ceaParams.of_ratio}
                                        onChange={(e) => setCeaParams({ ...ceaParams, of_ratio: parseFloat(e.target.value) })}
                                        className="input-field"
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="input-label">Pression chambre (bar)</label>
                                    <input
                                        type="number"
                                        value={ceaParams.pc}
                                        onChange={(e) => setCeaParams({ ...ceaParams, pc: parseFloat(e.target.value) })}
                                        className="input-field"
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="input-label">Ratio d'expansion (ε)</label>
                                    <input
                                        type="number"
                                        value={ceaParams.expansion_ratio}
                                        onChange={(e) => setCeaParams({ ...ceaParams, expansion_ratio: parseFloat(e.target.value) })}
                                        className="input-field"
                                    />
                                </div>
                            </div>
                        </div>

                        <button onClick={calculateCEA} disabled={loading} className="btn-primary w-full">
                            {loading ? "⏳ Calcul CEA..." : "🔬 Calculer CEA"}
                        </button>
                    </div>

                    {/* Results */}
                    <div className="col-span-12 lg:col-span-8">
                        {results ? (
                            <div className="space-y-6">
                                {/* Main Performance */}
                                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                    <div className="stat-card glow-cyan">
                                        <p className="text-xs text-[#00d4ff] uppercase tracking-wider mb-1">Isp (vide)</p>
                                        <p className="stat-value">{results.isp_vac?.toFixed(1)}<span className="stat-unit">s</span></p>
                                    </div>
                                    <div className="stat-card">
                                        <p className="text-xs text-[#8b5cf6] uppercase tracking-wider mb-1">Isp (SL)</p>
                                        <p className="stat-value">{results.isp_sl?.toFixed(1)}<span className="stat-unit">s</span></p>
                                    </div>
                                    <div className="stat-card">
                                        <p className="text-xs text-[#f59e0b] uppercase tracking-wider mb-1">c*</p>
                                        <p className="stat-value">{results.c_star?.toFixed(0)}<span className="stat-unit">m/s</span></p>
                                    </div>
                                    <div className="stat-card">
                                        <p className="text-xs text-[#ef4444] uppercase tracking-wider mb-1">T chambre</p>
                                        <p className="stat-value">{results.t_chamber?.toFixed(0)}<span className="stat-unit">K</span></p>
                                    </div>
                                    <div className="stat-card">
                                        <p className="text-xs text-[#10b981] uppercase tracking-wider mb-1">γ</p>
                                        <p className="stat-value">{results.gamma?.toFixed(3)}</p>
                                    </div>
                                    <div className="stat-card">
                                        <p className="text-xs text-[#ec4899] uppercase tracking-wider mb-1">MW</p>
                                        <p className="stat-value">{results.mw?.toFixed(2)}<span className="stat-unit">g/mol</span></p>
                                    </div>
                                </div>

                                {/* Details */}
                                <div className="card">
                                    <h3 className="card-header">📊 Détails</h3>
                                    <div className="grid grid-cols-2 gap-6">
                                        <div className="data-grid">
                                            <div className="data-row">
                                                <span className="data-label">Oxydant</span>
                                                <span className="data-value">{ceaParams.oxidizer}</span>
                                            </div>
                                            <div className="data-row">
                                                <span className="data-label">Carburant</span>
                                                <span className="data-value">{ceaParams.fuel}</span>
                                            </div>
                                            <div className="data-row">
                                                <span className="data-label">O/F ratio</span>
                                                <span className="data-value">{ceaParams.of_ratio}</span>
                                            </div>
                                            <div className="data-row">
                                                <span className="data-label">Pc</span>
                                                <span className="data-value">{ceaParams.pc} bar</span>
                                            </div>
                                        </div>
                                        <div className="data-grid">
                                            <div className="data-row">
                                                <span className="data-label">ε</span>
                                                <span className="data-value">{ceaParams.expansion_ratio}</span>
                                            </div>
                                            <div className="data-row">
                                                <span className="data-label">Isp vacuum</span>
                                                <span className="data-value">{results.isp_vac?.toFixed(1)} s</span>
                                            </div>
                                            <div className="data-row">
                                                <span className="data-label">Isp sea level</span>
                                                <span className="data-value">{results.isp_sl?.toFixed(1)} s</span>
                                            </div>
                                            <div className="data-row">
                                                <span className="data-label">Efficiency</span>
                                                <span className="data-value">{((results.isp_vac / 450) * 100).toFixed(1)}%</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="card h-full flex items-center justify-center text-center py-20">
                                <div>
                                    <span className="text-5xl mb-4 block">🔬</span>
                                    <h3 className="text-xl font-bold text-white mb-2">Prêt pour CEA</h3>
                                    <p className="text-[#71717a]">Sélectionnez un preset ou configurez les paramètres, puis cliquez sur "Calculer CEA"</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
