"use client";

import { useState } from "react";
import AppLayout from "@/components/AppLayout";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface MotorDefinition {
  name: string;
  oxidizer: string;
  fuel: string;
  of_ratio: number;
  pc: number;
  mdot: number;
  lstar: number;
  contraction_ratio: number;
  pe: number;
  pamb: number;
  theta_n: number;
  theta_e: number;
  material_name: string;
  wall_thickness: number;
  wall_k: number;
  twall_max: number;
  coolant_name: string;
  coolant_mdot: string;
  coolant_pressure: number;
  coolant_tin: number;
  coolant_tout_max: number;
  coolant_margin: number;
  custom_cp: number;
  custom_tboil: number;
  custom_tcrit: number;
  custom_hvap: number;
}

export default function Home() {
  const [materials, setMaterials] = useState<any>(null);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const [motor, setMotor] = useState<MotorDefinition>({
    name: "Moteur_Propane",
    oxidizer: "O2",
    fuel: "C3H8",
    of_ratio: 2.8,
    pc: 12.0,
    mdot: 0.5,
    lstar: 1.0,
    contraction_ratio: 3.5,
    pe: 1.013,
    pamb: 1.013,
    theta_n: 25.0,
    theta_e: 8.0,
    material_name: "Cuivre-Zirconium (CuZr)",
    wall_thickness: 2.0,
    wall_k: 340.0,
    twall_max: 1000.0,
    coolant_name: "Auto",
    coolant_mdot: "Auto",
    coolant_pressure: 15.0,
    coolant_tin: 293.0,
    coolant_tout_max: 350.0,
    coolant_margin: 20.0,
    custom_cp: 2500.0,
    custom_tboil: 350.0,
    custom_tcrit: 500.0,
    custom_hvap: 400.0
  });

  const loadMaterials = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/materials");
      const data = await res.json();
      setMaterials(data.materials);
    } catch (e) {
      console.error("Failed to load materials:", e);
    }
  };

  const calculateFull = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/calculate/full", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(motor)
      });
      const data = await res.json();
      setResults(data);
    } catch (e) {
      console.error("Calculation failed:", e);
      alert("Erreur - Vérifiez que les services sont démarrés");
    } finally {
      setLoading(false);
    }
  };

  const updateMotor = (key: keyof MotorDefinition, value: any) => {
    setMotor(prev => ({ ...prev, [key]: value }));
  };

  return (
    <AppLayout>
      <div className="max-w-[2000px] mx-auto p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-4xl font-bold text-white mb-2">ROCKET DESIGN STUDIO</h1>
          <p className="text-slate-400">Configuration complète du moteur-fusée</p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
          {/* LEFT SIDEBAR - INPUTS */}
          <div className="xl:col-span-1 space-y-4">
            <div className="bg-slate-900 border border-slate-700 p-4 rounded-xl">
              <h2 className="text-lg font-bold text-white mb-4">⚙️ Paramètres</h2>

              {/* Quick Actions */}
              <div className="space-y-2 mb-4">
                <button onClick={loadMaterials} className="w-full bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-bold">
                  📦 Charger Matériaux
                </button>
                <button onClick={calculateFull} disabled={loading} className="w-full bg-green-600 hover:bg-green-500 disabled:opacity-50 text-white px-4 py-3 rounded-lg font-bold">
                  {loading ? "⏳ Calcul..." : "🔥 CALCULER TOUT"}
                </button>
              </div>

              {/* Identification */}
              <div className="mb-4">
                <label className="block text-xs text-slate-400 mb-1">Nom du Moteur</label>
                <input type="text" value={motor.name} onChange={(e) => updateMotor("name", e.target.value)}
                  className="w-full bg-slate-800 text-white px-3 py-2 rounded-lg border border-slate-700 text-sm" />
              </div>

              {/* Propellants */}
              <div className="mb-4">
                <h3 className="text-sm font-bold text-cyan-400 mb-2">Propergols (CEA)</h3>
                <div className="space-y-2">
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Oxydant</label>
                    <input type="text" value={motor.oxidizer} onChange={(e) => updateMotor("oxidizer", e.target.value)}
                      className="w-full bg-slate-800 text-white px-3 py-2 rounded-lg border border-slate-700 text-sm" />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Carburant</label>
                    <input type="text" value={motor.fuel} onChange={(e) => updateMotor("fuel", e.target.value)}
                      className="w-full bg-slate-800 text-white px-3 py-2 rounded-lg border border-slate-700 text-sm" />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Ratio O/F</label>
                    <input type="number" step="0.1" value={motor.of_ratio} onChange={(e) => updateMotor("of_ratio", parseFloat(e.target.value))}
                      className="w-full bg-slate-800 text-white px-3 py-2 rounded-lg border border-slate-700 text-sm" />
                  </div>
                </div>
              </div>

              {/* Chamber */}
              <div className="mb-4">
                <h3 className="text-sm font-bold text-orange-400 mb-2">Chambre</h3>
                <div className="space-y-2">
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Pc (bar)</label>
                    <input type="number" value={motor.pc} onChange={(e) => updateMotor("pc", parseFloat(e.target.value))}
                      className="w-full bg-slate-800 text-white px-3 py-2 rounded-lg border border-slate-700 text-sm" />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Débit (kg/s)</label>
                    <input type="number" step="0.1" value={motor.mdot} onChange={(e) => updateMotor("mdot", parseFloat(e.target.value))}
                      className="w-full bg-slate-800 text-white px-3 py-2 rounded-lg border border-slate-700 text-sm" />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">L* (m)</label>
                    <input type="number" step="0.1" value={motor.lstar} onChange={(e) => updateMotor("lstar", parseFloat(e.target.value))}
                      className="w-full bg-slate-800 text-white px-3 py-2 rounded-lg border border-slate-700 text-sm" />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Contraction Ratio</label>
                    <input type="number" step="0.1" value={motor.contraction_ratio} onChange={(e) => updateMotor("contraction_ratio", parseFloat(e.target.value))}
                      className="w-full bg-slate-800 text-white px-3 py-2 rounded-lg border border-slate-700 text-sm" />
                  </div>
                </div>
              </div>

              {/* Nozzle */}
              <div className="mb-4">
                <h3 className="text-sm font-bold text-purple-400 mb-2">Tuyère</h3>
                <div className="space-y-2">
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Pe (bar)</label>
                    <input type="number" step="0.01" value={motor.pe} onChange={(e) => updateMotor("pe", parseFloat(e.target.value))}
                      className="w-full bg-slate-800 text-white px-3 py-2 rounded-lg border border-slate-700 text-sm" />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Angle entrée (°)</label>
                    <input type="number" value={motor.theta_n} onChange={(e) => updateMotor("theta_n", parseFloat(e.target.value))}
                      className="w-full bg-slate-800 text-white px-3 py-2 rounded-lg border border-slate-700 text-sm" />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Angle sortie (°)</label>
                    <input type="number" value={motor.theta_e} onChange={(e) => updateMotor("theta_e", parseFloat(e.target.value))}
                      className="w-full bg-slate-800 text-white px-3 py-2 rounded-lg border border-slate-700 text-sm" />
                  </div>
                </div>
              </div>

              {/* Material */}
              <div className="mb-4">
                <h3 className="text-sm font-bold text-pink-400 mb-2">Matériau</h3>
                {materials && (
                  <select value={motor.material_name} onChange={(e) => {
                    const mat = materials[e.target.value];
                    updateMotor("material_name", e.target.value);
                    if (mat) {
                      updateMotor("wall_k", mat.k);
                      updateMotor("twall_max", mat.T_max);
                    }
                  }}
                    className="w-full bg-slate-800 text-white px-3 py-2 rounded-lg border border-slate-700 text-sm mb-2">
                    {Object.keys(materials).map(name => (
                      <option key={name} value={name}>{name}</option>
                    ))}
                  </select>
                )}
                <div className="space-y-2">
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Épaisseur (mm)</label>
                    <input type="number" step="0.1" value={motor.wall_thickness} onChange={(e) => updateMotor("wall_thickness", parseFloat(e.target.value))}
                      className="w-full bg-slate-800 text-white px-3 py-2 rounded-lg border border-slate-700 text-sm" />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">k (W/m-K)</label>
                    <input type="number" value={motor.wall_k} onChange={(e) => updateMotor("wall_k", parseFloat(e.target.value))}
                      className="w-full bg-slate-800 text-white px-3 py-2 rounded-lg border border-slate-700 text-sm" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* MAIN CONTENT - SUMMARY */}
          <div className="xl:col-span-3">
            {results ? (
              <div className="bg-slate-900 border border-slate-700 p-6 rounded-xl">
                <h2 className="text-2xl font-bold text-white mb-6">📊 RÉSUMÉ - {motor.name}</h2>

                {/* Performance Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/20 border border-blue-700/50 p-4 rounded-xl">
                    <div className="text-xs text-blue-400 mb-1">Isp (vide)</div>
                    <div className="text-3xl font-bold text-white">{results.isp_vac?.toFixed(1)}</div>
                    <div className="text-xs text-slate-400">secondes</div>
                  </div>
                  <div className="bg-gradient-to-br from-green-900/30 to-green-800/20 border border-green-700/50 p-4 rounded-xl">
                    <div className="text-xs text-green-400 mb-1">Poussée (vide)</div>
                    <div className="text-3xl font-bold text-white">{(results.thrust_vac / 1000)?.toFixed(2)}</div>
                    <div className="text-xs text-slate-400">kN</div>
                  </div>
                  <div className="bg-gradient-to-br from-orange-900/30 to-orange-800/20 border border-orange-700/50 p-4 rounded-xl">
                    <div className="text-xs text-orange-400 mb-1">c*</div>
                    <div className="text-3xl font-bold text-white">{results.c_star?.toFixed(0)}</div>
                    <div className="text-xs text-slate-400">m/s</div>
                  </div>
                  <div className="bg-gradient-to-br from-purple-900/30 to-purple-800/20 border border-purple-700/50 p-4 rounded-xl">
                    <div className="text-xs text-purple-400 mb-1">T chambre</div>
                    <div className="text-3xl font-bold text-white">{results.t_chamber?.toFixed(0)}</div>
                    <div className="text-xs text-slate-400">K</div>
                  </div>
                </div>

                {/* Geometry Section */}
                <div className="mb-6">
                  <h3 className="text-xl font-bold text-cyan-400 mb-4">📐 Géométrie</h3>
                  <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
                    <div className="bg-slate-800 p-3 rounded-lg">
                      <div className="text-xs text-slate-400">R col</div>
                      <div className="text-lg font-bold text-white">{(results.r_throat * 1000)?.toFixed(1)}</div>
                      <div className="text-xs text-slate-500">mm</div>
                    </div>
                    <div className="bg-slate-800 p-3 rounded-lg">
                      <div className="text-xs text-slate-400">R chambre</div>
                      <div className="text-lg font-bold text-white">{(results.r_chamber * 1000)?.toFixed(1)}</div>
                      <div className="text-xs text-slate-500">mm</div>
                    </div>
                    <div className="bg-slate-800 p-3 rounded-lg">
                      <div className="text-xs text-slate-400">R sortie</div>
                      <div className="text-lg font-bold text-white">{(results.r_exit * 1000)?.toFixed(1)}</div>
                      <div className="text-xs text-slate-500">mm</div>
                    </div>
                    <div className="bg-slate-800 p-3 rounded-lg">
                      <div className="text-xs text-slate-400">L chambre</div>
                      <div className="text-lg font-bold text-white">{(results.l_chamber * 1000)?.toFixed(0)}</div>
                      <div className="text-xs text-slate-500">mm</div>
                    </div>
                    <div className="bg-slate-800 p-3 rounded-lg">
                      <div className="text-xs text-slate-400">L tuyère</div>
                      <div className="text-lg font-bold text-white">{(results.l_nozzle * 1000)?.toFixed(0)}</div>
                      <div className="text-xs text-slate-500">mm</div>
                    </div>
                    <div className="bg-slate-800 p-3 rounded-lg">
                      <div className="text-xs text-slate-400">ε</div>
                      <div className="text-lg font-bold text-white">{results.expansion_ratio?.toFixed(1)}</div>
                      <div className="text-xs text-slate-500">-</div>
                    </div>
                  </div>
                </div>

                {/* Thermal Section */}
                <div className="mb-6">
                  <h3 className="text-xl font-bold text-orange-400 mb-4">🔥 Thermique</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="bg-slate-800 p-3 rounded-lg">
                      <div className="text-xs text-slate-400">Flux max</div>
                      <div className="text-lg font-bold text-orange-400">{results.max_heat_flux?.toFixed(2)}</div>
                      <div className="text-xs text-slate-500">MW/m²</div>
                    </div>
                    <div className="bg-slate-800 p-3 rounded-lg">
                      <div className="text-xs text-slate-400">T paroi max</div>
                      <div className="text-lg font-bold text-white">{results.max_wall_temp?.toFixed(0)}</div>
                      <div className="text-xs text-slate-500">K</div>
                    </div>
                    <div className="bg-slate-800 p-3 rounded-lg">
                      <div className="text-xs text-slate-400">T coolant out</div>
                      <div className="text-lg font-bold text-white">{results.coolant_temp_out?.toFixed(0)}</div>
                      <div className="text-xs text-slate-500">K</div>
                    </div>
                    <div className="bg-slate-800 p-3 rounded-lg">
                      <div className="text-xs text-slate-400">ΔP coolant</div>
                      <div className="text-lg font-bold text-white">{results.coolant_pressure_drop?.toFixed(1)}</div>
                      <div className="text-xs text-slate-500">bar</div>
                    </div>
                  </div>
                  <div className={`mt-3 p-3 rounded-lg ${results.cooling_status === "OK" ? "bg-green-900/30 border border-green-700" :
                      results.cooling_status === "WARNING" ? "bg-yellow-900/30 border border-yellow-700" :
                        "bg-red-900/30 border border-red-700"
                    }`}>
                    <div className="font-bold">
                      {results.cooling_status === "OK" && "✅ Refroidissement OK"}
                      {results.cooling_status === "WARNING" && "⚠️ Refroidissement Limite"}
                      {results.cooling_status === "CRITICAL" && "❌ Refroidissement Critique"}
                    </div>
                  </div>
                </div>

                {/* CEA Details */}
                <div>
                  <h3 className="text-xl font-bold text-purple-400 mb-4">🔬 Détails CEA</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="bg-slate-800 p-3 rounded-lg">
                      <div className="text-xs text-slate-400">γ</div>
                      <div className="text-lg font-bold text-white">{results.gamma?.toFixed(3)}</div>
                    </div>
                    <div className="bg-slate-800 p-3 rounded-lg">
                      <div className="text-xs text-slate-400">MW</div>
                      <div className="text-lg font-bold text-white">{results.mw?.toFixed(2)}</div>
                      <div className="text-xs text-slate-500">g/mol</div>
                    </div>
                    <div className="bg-slate-800 p-3 rounded-lg">
                      <div className="text-xs text-slate-400">CF (vide)</div>
                      <div className="text-lg font-bold text-white">{results.cf_vac?.toFixed(3)}</div>
                    </div>
                    <div className="bg-slate-800 p-3 rounded-lg">
                      <div className="text-xs text-slate-400">Isp (SL)</div>
                      <div className="text-lg font-bold text-white">{results.isp_sl?.toFixed(1)}</div>
                      <div className="text-xs text-slate-500">s</div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900 border border-slate-700 p-12 rounded-xl text-center">
                <div className="text-6xl mb-4">🚀</div>
                <h2 className="text-2xl font-bold text-white mb-2">Prêt à calculer</h2>
                <p className="text-slate-400 mb-6">Configurez les paramètres et cliquez sur "CALCULER TOUT"</p>
                <div className="text-sm text-slate-500">
                  <div>✓ Calculs CEA complets</div>
                  <div>✓ Génération géométrie</div>
                  <div>✓ Analyse thermique</div>
                  <div>✓ Calculs de performance</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
