"use client";

import { useState, useEffect } from "react";
import AppLayout from "@/components/AppLayout";

interface MotorConfig {
  name: string;
  oxidizer: string;
  fuel: string;
  of_ratio: number;
  pc: number;
  mdot: number;
  lstar: number;
  contraction_ratio: number;
  pe: number;
  theta_n: number;
  theta_e: number;
  material_name: string;
  wall_thickness: number;
  wall_k: number;
  twall_max: number;
}

export default function Home() {
  const [materials, setMaterials] = useState<any>(null);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const [config, setConfig] = useState<MotorConfig>({
    name: "Moteur_Propane",
    oxidizer: "O2",
    fuel: "C3H8",
    of_ratio: 2.8,
    pc: 12.0,
    mdot: 0.5,
    lstar: 1.0,
    contraction_ratio: 3.5,
    pe: 1.013,
    theta_n: 25.0,
    theta_e: 8.0,
    material_name: "Cuivre-Zirconium (CuZr)",
    wall_thickness: 2.0,
    wall_k: 340.0,
    twall_max: 1000.0,
  });

  useEffect(() => {
    loadMaterials();
  }, []);

  const loadMaterials = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/materials");
      const data = await res.json();
      setMaterials(data.materials);
    } catch (e) {
      console.error("Materials load failed:", e);
    }
  };

  const calculateFull = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/calculate/full", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config)
      });
      const data = await res.json();
      setResults(data);
    } catch (e) {
      console.error("Calculation failed:", e);
    } finally {
      setLoading(false);
    }
  };

  const updateConfig = (key: keyof MotorConfig, value: any) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  return (
    <AppLayout>
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Rocket Design Studio</h1>
          <p className="text-[#71717a]">Configuration et analyse complète du moteur-fusée</p>
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Left Panel - Configuration */}
          <div className="col-span-12 lg:col-span-4 xl:col-span-3 space-y-6">
            {/* Quick Actions */}
            <div className="card">
              <button
                onClick={calculateFull}
                disabled={loading}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <span className="animate-spin">⏳</span>
                    Calcul en cours...
                  </>
                ) : (
                  <>
                    <span>🔥</span>
                    CALCULER TOUT
                  </>
                )}
              </button>
            </div>

            {/* Motor Name */}
            <div className="card">
              <h3 className="card-header">
                <span>🏷️</span> Identification
              </h3>
              <div className="form-group">
                <label className="input-label">Nom du moteur</label>
                <input
                  type="text"
                  value={config.name}
                  onChange={(e) => updateConfig("name", e.target.value)}
                  className="input-field"
                />
              </div>
            </div>

            {/* Propellants */}
            <div className="card">
              <h3 className="card-header">
                <span>⚗️</span> Propergols
              </h3>
              <div className="space-y-4">
                <div className="form-group">
                  <label className="input-label">Oxydant</label>
                  <input
                    type="text"
                    value={config.oxidizer}
                    onChange={(e) => updateConfig("oxidizer", e.target.value)}
                    className="input-field"
                  />
                </div>
                <div className="form-group">
                  <label className="input-label">Carburant</label>
                  <input
                    type="text"
                    value={config.fuel}
                    onChange={(e) => updateConfig("fuel", e.target.value)}
                    className="input-field"
                  />
                </div>
                <div className="form-group">
                  <label className="input-label">Ratio O/F</label>
                  <input
                    type="number"
                    step="0.1"
                    value={config.of_ratio}
                    onChange={(e) => updateConfig("of_ratio", parseFloat(e.target.value))}
                    className="input-field"
                  />
                </div>
              </div>
            </div>

            {/* Chamber */}
            <div className="card">
              <h3 className="card-header">
                <span>🔴</span> Chambre
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="form-group">
                  <label className="input-label">Pc (bar)</label>
                  <input
                    type="number"
                    value={config.pc}
                    onChange={(e) => updateConfig("pc", parseFloat(e.target.value))}
                    className="input-field"
                  />
                </div>
                <div className="form-group">
                  <label className="input-label">Débit (kg/s)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={config.mdot}
                    onChange={(e) => updateConfig("mdot", parseFloat(e.target.value))}
                    className="input-field"
                  />
                </div>
                <div className="form-group">
                  <label className="input-label">L* (m)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={config.lstar}
                    onChange={(e) => updateConfig("lstar", parseFloat(e.target.value))}
                    className="input-field"
                  />
                </div>
                <div className="form-group">
                  <label className="input-label">Contraction (Ac/At)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={config.contraction_ratio}
                    onChange={(e) => updateConfig("contraction_ratio", parseFloat(e.target.value))}
                    className="input-field"
                  />
                </div>
              </div>
            </div>

            {/* Material */}
            <div className="card">
              <h3 className="card-header">
                <span>🧱</span> Matériau
              </h3>
              <div className="space-y-4">
                {materials && (
                  <div className="form-group">
                    <label className="input-label">Sélection</label>
                    <select
                      value={config.material_name}
                      onChange={(e) => {
                        const mat = materials[e.target.value];
                        updateConfig("material_name", e.target.value);
                        if (mat) {
                          updateConfig("wall_k", mat.k);
                          updateConfig("twall_max", mat.T_max);
                        }
                      }}
                      className="input-field"
                    >
                      {Object.keys(materials).map(name => (
                        <option key={name} value={name}>{name}</option>
                      ))}
                    </select>
                  </div>
                )}
                <div className="grid grid-cols-2 gap-4">
                  <div className="form-group">
                    <label className="input-label">Épaisseur (mm)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={config.wall_thickness}
                      onChange={(e) => updateConfig("wall_thickness", parseFloat(e.target.value))}
                      className="input-field"
                    />
                  </div>
                  <div className="form-group">
                    <label className="input-label">k (W/m·K)</label>
                    <input
                      type="number"
                      value={config.wall_k}
                      onChange={(e) => updateConfig("wall_k", parseFloat(e.target.value))}
                      className="input-field"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Panel - Results */}
          <div className="col-span-12 lg:col-span-8 xl:col-span-9">
            {results ? (
              <div className="space-y-6">
                {/* Performance Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="stat-card glow-cyan">
                    <div className="absolute top-0 right-0 w-20 h-20 bg-[#00d4ff]/5 rounded-full -translate-y-1/2 translate-x-1/2"></div>
                    <p className="text-xs text-[#00d4ff] font-medium uppercase tracking-wider mb-1">Isp (vide)</p>
                    <p className="stat-value">{results.isp_vac?.toFixed(1)}<span className="stat-unit">s</span></p>
                  </div>
                  <div className="stat-card glow-purple">
                    <div className="absolute top-0 right-0 w-20 h-20 bg-[#8b5cf6]/5 rounded-full -translate-y-1/2 translate-x-1/2"></div>
                    <p className="text-xs text-[#8b5cf6] font-medium uppercase tracking-wider mb-1">Poussée</p>
                    <p className="stat-value">{(results.thrust_vac / 1000)?.toFixed(2)}<span className="stat-unit">kN</span></p>
                  </div>
                  <div className="stat-card">
                    <p className="text-xs text-[#f59e0b] font-medium uppercase tracking-wider mb-1">c*</p>
                    <p className="stat-value">{results.c_star?.toFixed(0)}<span className="stat-unit">m/s</span></p>
                  </div>
                  <div className="stat-card">
                    <p className="text-xs text-[#ec4899] font-medium uppercase tracking-wider mb-1">T chambre</p>
                    <p className="stat-value">{results.t_chamber?.toFixed(0)}<span className="stat-unit">K</span></p>
                  </div>
                </div>

                {/* Geometry */}
                <div className="card">
                  <h3 className="card-header">
                    <span>📐</span> Géométrie
                  </h3>
                  <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
                    {[
                      { label: "R col", value: (results.r_throat * 1000)?.toFixed(1), unit: "mm" },
                      { label: "R chambre", value: (results.r_chamber * 1000)?.toFixed(1), unit: "mm" },
                      { label: "R sortie", value: (results.r_exit * 1000)?.toFixed(1), unit: "mm" },
                      { label: "L chambre", value: (results.l_chamber * 1000)?.toFixed(0), unit: "mm" },
                      { label: "L tuyère", value: (results.l_nozzle * 1000)?.toFixed(0), unit: "mm" },
                      { label: "ε", value: results.expansion_ratio?.toFixed(1), unit: "" },
                    ].map((item, i) => (
                      <div key={i} className="bg-[#1a1a25] rounded-lg p-4 text-center">
                        <p className="text-xs text-[#71717a] mb-1">{item.label}</p>
                        <p className="text-xl font-bold text-white">{item.value}</p>
                        <p className="text-xs text-[#a1a1aa]">{item.unit}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Thermal */}
                <div className="card">
                  <h3 className="card-header">
                    <span>🌡️</span> Thermique
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    {[
                      { label: "Flux max", value: results.max_heat_flux?.toFixed(2), unit: "MW/m²", color: "text-[#f59e0b]" },
                      { label: "T paroi max", value: results.max_wall_temp?.toFixed(0), unit: "K", color: "text-[#ef4444]" },
                      { label: "T coolant out", value: results.coolant_temp_out?.toFixed(0), unit: "K", color: "text-[#00d4ff]" },
                      { label: "ΔP coolant", value: results.coolant_pressure_drop?.toFixed(1), unit: "bar", color: "text-white" },
                    ].map((item, i) => (
                      <div key={i} className="bg-[#1a1a25] rounded-lg p-4">
                        <p className="text-xs text-[#71717a] mb-1">{item.label}</p>
                        <p className={`text-2xl font-bold ${item.color}`}>{item.value}</p>
                        <p className="text-xs text-[#a1a1aa]">{item.unit}</p>
                      </div>
                    ))}
                  </div>
                  <div className={`rounded-lg p-4 flex items-center gap-3 ${results.cooling_status === "OK" ? "bg-[#10b981]/10 border border-[#10b981]/30" :
                      results.cooling_status === "WARNING" ? "bg-[#f59e0b]/10 border border-[#f59e0b]/30" :
                        "bg-[#ef4444]/10 border border-[#ef4444]/30"
                    }`}>
                    <span className="text-2xl">
                      {results.cooling_status === "OK" ? "✅" : results.cooling_status === "WARNING" ? "⚠️" : "❌"}
                    </span>
                    <div>
                      <p className={`font-semibold ${results.cooling_status === "OK" ? "text-[#10b981]" :
                          results.cooling_status === "WARNING" ? "text-[#f59e0b]" :
                            "text-[#ef4444]"
                        }`}>
                        Refroidissement {results.cooling_status === "OK" ? "OK" : results.cooling_status === "WARNING" ? "Limite" : "Critique"}
                      </p>
                      <p className="text-sm text-[#71717a]">
                        Marge thermique : {((config.twall_max - results.max_wall_temp) / config.twall_max * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                </div>

                {/* CEA Details */}
                <div className="card">
                  <h3 className="card-header">
                    <span>🔬</span> Détails CEA
                  </h3>
                  <div className="grid grid-cols-4 gap-4">
                    {[
                      { label: "γ", value: results.gamma?.toFixed(3) },
                      { label: "MW", value: results.mw?.toFixed(2), unit: "g/mol" },
                      { label: "CF (vide)", value: results.cf_vac?.toFixed(3) },
                      { label: "Isp (SL)", value: results.isp_sl?.toFixed(1), unit: "s" },
                    ].map((item, i) => (
                      <div key={i} className="bg-[#1a1a25] rounded-lg p-4 text-center">
                        <p className="text-xs text-[#71717a] mb-1">{item.label}</p>
                        <p className="text-xl font-bold text-white">{item.value}</p>
                        {item.unit && <p className="text-xs text-[#a1a1aa]">{item.unit}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              /* Empty State */
              <div className="card h-full flex flex-col items-center justify-center text-center py-20">
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-[#00d4ff]/20 to-[#8b5cf6]/20 flex items-center justify-center mb-6">
                  <span className="text-5xl">🚀</span>
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">Prêt à concevoir</h2>
                <p className="text-[#71717a] mb-8 max-w-md">
                  Configurez les paramètres du moteur dans le panneau de gauche, puis cliquez sur "Calculer Tout" pour lancer l'analyse complète.
                </p>
                <div className="flex flex-wrap gap-3 justify-center text-sm text-[#a1a1aa]">
                  <span className="badge badge-success">✓ Calculs CEA</span>
                  <span className="badge badge-success">✓ Génération géométrie</span>
                  <span className="badge badge-success">✓ Analyse thermique</span>
                  <span className="badge badge-success">✓ Performance</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
