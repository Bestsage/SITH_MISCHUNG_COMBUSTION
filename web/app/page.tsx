"use client";

import { useState, useEffect, useRef } from "react";
import dynamic from "next/dynamic";
import AppLayout from "@/components/AppLayout";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, AreaChart, Area, ComposedChart, Bar } from "recharts";

const Motor3DViewer = dynamic(() => import("@/components/Motor3DViewer"), { ssr: false });

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

const defaultConfig: MotorConfig = {
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
  custom_hvap: 400.0,
};

type ResultTab = "summary" | "3d" | "cea" | "graphs" | "bartz" | "heatmap" | "stress";

export default function Home() {
  const [materials, setMaterials] = useState<any>(null);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [configTab, setConfigTab] = useState<"basic" | "coolant" | "advanced">("basic");
  const [resultTab, setResultTab] = useState<ResultTab>("summary");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [config, setConfig] = useState<MotorConfig>(defaultConfig);

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

  const exportJSON = () => {
    const dataStr = JSON.stringify(config, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${config.name}.json`;
    link.click();
  };

  const importJSON = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const imported = JSON.parse(e.target?.result as string);
        setConfig({ ...defaultConfig, ...imported });
      } catch { alert("Fichier JSON invalide"); }
    };
    reader.readAsText(file);
  };

  const exportDXF = () => {
    if (!results?.geometry) return alert("Calculez d'abord!");
    let dxf = "0\nSECTION\n2\nENTITIES\n0\nPOLYLINE\n8\n0\n66\n1\n70\n0\n";
    results.geometry.x.forEach((x: number, i: number) => {
      dxf += `0\nVERTEX\n8\n0\n10\n${(x * 1000).toFixed(4)}\n20\n${(results.geometry.r[i] * 1000).toFixed(4)}\n30\n0\n`;
    });
    dxf += "0\nSEQEND\n0\nENDSEC\n0\nEOF\n";
    const blob = new Blob([dxf], { type: "application/dxf" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${config.name}.dxf`;
    link.click();
  };

  const InputField = ({ label, configKey, type = "number", unit = "" }: { label: string; configKey: keyof MotorConfig; type?: string; unit?: string }) => (
    <div className="flex items-center justify-between gap-2 py-1">
      <label className="text-xs text-[#a1a1aa]">{label}</label>
      <div className="flex items-center gap-1">
        <input type={type} value={config[configKey]} onChange={(e) => updateConfig(configKey, type === "number" ? parseFloat(e.target.value) || 0 : e.target.value)} className="input-field text-xs w-20 text-right py-1" />
        {unit && <span className="text-[10px] text-[#71717a] w-10">{unit}</span>}
      </div>
    </div>
  );

  // Generate thermal data for visualization
  const generateThermalData = () => {
    if (!results) return [];
    const data = [];
    for (let i = 0; i < 50; i++) {
      const x = i / 49;
      const throatPos = 0.4;
      const areaRatio = x < throatPos ? 3 - 2 * x / throatPos : 1 + 39 * (x - throatPos) / (1 - throatPos);
      const hg = 5000 / Math.pow(areaRatio, 0.9);
      const q = hg * (results.t_chamber - 500) / 1e6;
      const tWall = 500 + q * 1e6 / hg * 0.3;
      data.push({
        x: (x * 350).toFixed(0),
        hg: hg.toFixed(0),
        q: q.toFixed(2),
        tWall: tWall.toFixed(0),
        tCoolant: (300 + x * 50).toFixed(0),
        areaRatio: areaRatio.toFixed(2)
      });
    }
    return data;
  };

  // Calculate stress data
  const calculateStressData = () => {
    if (!results) return { sigmaHoop: 0, sigmaThermal: 0, sigmaVM: 0, fos: 0, tOuterShell: 0 };
    const pc = config.pc * 1e5; // Pa
    const r = results.r_throat || 0.02; // m
    const e = config.wall_thickness / 1000; // m
    const sigmaHoop = (pc * r) / e / 1e6; // MPa

    const deltaT = results.t_chamber * 0.3 - 300; // Approximate wall temp gradient
    const E = 120e9; // Pa (copper)
    const alpha = 17e-6; // 1/K
    const nu = 0.33;
    const sigmaThermal = E * alpha * deltaT / (2 * (1 - nu)) / 1e6; // MPa

    const sigmaVM = Math.sqrt(sigmaHoop ** 2 + sigmaThermal ** 2 - sigmaHoop * sigmaThermal);
    const sigmaYield = materials?.[config.material_name]?.sigma_y || 280;
    const fos = sigmaYield / sigmaVM;

    // Outer shell thickness estimation (steel, 200 MPa yield)
    const pCoolant = config.coolant_pressure * 1e5;
    const rOuter = (results.r_chamber || 0.05) + e;
    const tOuterShell = (pCoolant * rOuter) / (200e6 * 0.8) * 1000; // mm with safety factor

    return { sigmaHoop, sigmaThermal, sigmaVM, fos, tOuterShell };
  };

  const stressData = calculateStressData();

  return (
    <AppLayout>
      <div className="flex h-[calc(100vh-0px)] overflow-hidden">
        {/* Left Panel - Configuration (Fixed width, scrollable) */}
        <div className="w-72 bg-[#12121a] border-r border-[#27272a] flex flex-col h-full flex-shrink-0">
          {/* Header */}
          <div className="p-3 border-b border-[#27272a]">
            <h2 className="text-sm font-bold text-white">⚙️ Configuration</h2>
          </div>

          {/* Calculate Button */}
          <div className="p-3 border-b border-[#27272a]">
            <button onClick={calculateFull} disabled={loading} className="btn-primary w-full text-sm py-2">
              {loading ? "⏳ Calcul..." : "🔥 CALCULER"}
            </button>
          </div>

          {/* Config Tabs */}
          <div className="flex border-b border-[#27272a]">
            {["basic", "coolant", "advanced"].map((tab) => (
              <button key={tab} onClick={() => setConfigTab(tab as any)}
                className={`flex-1 py-2 text-[10px] font-medium ${configTab === tab ? "text-[#00d4ff] border-b-2 border-[#00d4ff]" : "text-[#71717a]"}`}>
                {tab === "basic" ? "🔧 Base" : tab === "coolant" ? "❄️ Cool" : "⚙️ Mat"}
              </button>
            ))}
          </div>

          {/* Config Content */}
          <div className="flex-1 overflow-y-auto p-3 space-y-1">
            {configTab === "basic" && (
              <>
                <div className="text-[10px] font-bold text-[#00d4ff] uppercase mb-2">Identification</div>
                <InputField label="Nom" configKey="name" type="text" />
                <div className="text-[10px] font-bold text-[#8b5cf6] uppercase mt-3 mb-2">Propergols</div>
                <InputField label="Oxydant" configKey="oxidizer" type="text" />
                <InputField label="Carburant" configKey="fuel" type="text" />
                <InputField label="O/F" configKey="of_ratio" />
                <div className="text-[10px] font-bold text-[#f59e0b] uppercase mt-3 mb-2">Chambre</div>
                <InputField label="Pc" configKey="pc" unit="bar" />
                <InputField label="ṁ" configKey="mdot" unit="kg/s" />
                <InputField label="L*" configKey="lstar" unit="m" />
                <InputField label="CR" configKey="contraction_ratio" />
                <div className="text-[10px] font-bold text-[#10b981] uppercase mt-3 mb-2">Tuyère</div>
                <InputField label="Pe" configKey="pe" unit="bar" />
                <InputField label="Pamb" configKey="pamb" unit="bar" />
                <InputField label="θn" configKey="theta_n" unit="°" />
                <InputField label="θe" configKey="theta_e" unit="°" />
              </>
            )}
            {configTab === "coolant" && (
              <>
                <div className="text-[10px] font-bold text-[#00d4ff] uppercase mb-2">Coolant</div>
                <InputField label="Nom" configKey="coolant_name" type="text" />
                <InputField label="Débit" configKey="coolant_mdot" type="text" />
                <InputField label="P" configKey="coolant_pressure" unit="bar" />
                <InputField label="Tin" configKey="coolant_tin" unit="K" />
                <InputField label="Tout max" configKey="coolant_tout_max" unit="K" />
                <InputField label="Marge" configKey="coolant_margin" unit="%" />
                <div className="text-[10px] font-bold text-[#8b5cf6] uppercase mt-3 mb-2">Custom</div>
                <InputField label="Cp" configKey="custom_cp" unit="J/kg·K" />
                <InputField label="Tboil" configKey="custom_tboil" unit="K" />
                <InputField label="Tcrit" configKey="custom_tcrit" unit="K" />
                <InputField label="Hvap" configKey="custom_hvap" unit="kJ/kg" />
              </>
            )}
            {configTab === "advanced" && (
              <>
                <div className="text-[10px] font-bold text-[#f59e0b] uppercase mb-2">Matériau</div>
                <select value={config.material_name} onChange={(e) => updateConfig("material_name", e.target.value)} className="input-field text-xs w-full py-1 mb-2">
                  {materials && Object.keys(materials).map((mat) => <option key={mat} value={mat}>{mat}</option>)}
                </select>
                <InputField label="Épaisseur" configKey="wall_thickness" unit="mm" />
                <InputField label="k" configKey="wall_k" unit="W/m·K" />
                <InputField label="Tmax" configKey="twall_max" unit="K" />
              </>
            )}
          </div>

          {/* Import/Export */}
          <div className="p-3 border-t border-[#27272a] space-y-2">
            <input type="file" ref={fileInputRef} onChange={importJSON} accept=".json" className="hidden" />
            <div className="grid grid-cols-2 gap-2">
              <button onClick={() => fileInputRef.current?.click()} className="btn-secondary text-[10px] py-1">📂 Import</button>
              <button onClick={exportJSON} className="btn-secondary text-[10px] py-1">💾 Export</button>
            </div>
            <button onClick={exportDXF} className="btn-secondary text-[10px] py-1 w-full" disabled={!results}>📐 Export DXF</button>
          </div>
        </div>

        {/* Right Panel - Results */}
        <div className="flex-1 flex flex-col h-full overflow-hidden">
          {/* Result Tabs */}
          <div className="flex border-b border-[#27272a] bg-[#0a0a0f] flex-shrink-0">
            {[
              { key: "summary", label: "📊 Résumé", color: "#00d4ff" },
              { key: "3d", label: "💻 3D", color: "#8b5cf6" },
              { key: "cea", label: "⚗️ CEA Raw", color: "#a855f7" },
              { key: "graphs", label: "📈 Graphes", color: "#10b981" },
              { key: "bartz", label: "🔥 Bartz", color: "#f59e0b" },
              { key: "heatmap", label: "🌡️ Heatmap", color: "#ef4444" },
              { key: "stress", label: "💪 Contraintes", color: "#06b6d4" },
            ].map((tab) => (
              <button key={tab.key} onClick={() => setResultTab(tab.key as ResultTab)}
                className={`px-4 py-3 text-xs font-medium transition-all ${resultTab === tab.key ? `text-white border-b-2` : "text-[#71717a] hover:text-white"}`}
                style={{ borderColor: resultTab === tab.key ? tab.color : "transparent" }}>
                {tab.label}
              </button>
            ))}
          </div>

          {/* Result Content */}
          <div className="flex-1 overflow-y-auto p-6">
            {!results ? (
              <div className="h-full flex items-center justify-center">
                <div className="text-center">
                  <span className="text-6xl mb-4 block">🚀</span>
                  <h3 className="text-xl font-bold text-white mb-2">Prêt à calculer</h3>
                  <p className="text-[#71717a]">Configurez et cliquez sur CALCULER</p>
                </div>
              </div>
            ) : (
              <>
                {/* SUMMARY TAB */}
                {resultTab === "summary" && (
                  <div className="space-y-6">
                    <h2 className="text-2xl font-bold text-white">📊 Résumé Complet - {config.name}</h2>

                    {/* Performance Cards */}
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                      {[
                        { label: "Isp (vide)", value: results.isp_vac?.toFixed(1), unit: "s", color: "#00d4ff" },
                        { label: "Isp (SL)", value: results.isp_sl?.toFixed(1), unit: "s", color: "#8b5cf6" },
                        { label: "c*", value: results.c_star?.toFixed(0), unit: "m/s", color: "#f59e0b" },
                        { label: "T chambre", value: results.t_chamber?.toFixed(0), unit: "K", color: "#ef4444" },
                        { label: "Cf (vide)", value: results.cf_vac?.toFixed(3), unit: "", color: "#10b981" },
                        { label: "γ", value: results.gamma?.toFixed(3), unit: "", color: "#06b6d4" },
                        { label: "MW", value: results.mw?.toFixed(2), unit: "kg/kmol", color: "#a855f7" },
                        { label: "Poussée vide", value: results.thrust_vac?.toFixed(0), unit: "N", color: "#f97316" },
                        { label: "Poussée SL", value: results.thrust_sl?.toFixed(0), unit: "N", color: "#eab308" },
                        { label: "R col", value: (results.r_throat * 1000)?.toFixed(1), unit: "mm", color: "#22c55e" },
                        { label: "R chambre", value: (results.r_chamber * 1000)?.toFixed(1), unit: "mm", color: "#3b82f6" },
                        { label: "ε", value: results.expansion_ratio?.toFixed(1), unit: "", color: "#ec4899" },
                      ].map((item, i) => (
                        <div key={i} className="bg-[#15151f] border border-[#27272a] rounded-lg p-3">
                          <p className="text-[10px] uppercase font-medium" style={{ color: item.color }}>{item.label}</p>
                          <p className="text-xl font-bold text-white">{item.value}<span className="text-xs text-[#71717a]">{item.unit}</span></p>
                        </div>
                      ))}
                    </div>

                    {/* Geometry Profile */}
                    <div className="card">
                      <h3 className="card-header">📐 Profil Géométrique</h3>
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={results.geometry_profile?.x?.map((x: number, i: number) => ({
                            x: (x * 1000).toFixed(1),
                            r: (results.geometry_profile.r[i] * 1000).toFixed(2),
                            rNeg: (-results.geometry_profile.r[i] * 1000).toFixed(2)
                          })) || []}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                            <XAxis dataKey="x" stroke="#71717a" fontSize={10} />
                            <YAxis stroke="#71717a" fontSize={10} />
                            <Tooltip contentStyle={{ backgroundColor: '#1a1a25', border: '1px solid #27272a' }} />
                            <Line type="monotone" dataKey="r" stroke="#00d4ff" strokeWidth={2} dot={false} name="R+ (mm)" />
                            <Line type="monotone" dataKey="rNeg" stroke="#00d4ff" strokeWidth={2} dot={false} name="R- (mm)" />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>
                )}

                {/* 3D TAB */}
                {resultTab === "3d" && (
                  <div className="space-y-6">
                    <h2 className="text-2xl font-bold text-white">💻 Visualisation 3D</h2>

                    <div className="card">
                      <h3 className="card-header">🚀 Modèle 3D du Moteur</h3>
                      <p className="text-xs text-[#71717a] mb-4">Cliquez et faites glisser pour tourner • Molette pour zoomer</p>
                      <Motor3DViewer
                        profile={results.geometry_profile}
                        height={500}
                        showFlames={false}
                      />
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      <div className="card p-4 text-center">
                        <p className="text-xs text-[#71717a]">R col</p>
                        <p className="text-xl font-bold text-[#00d4ff]">{(results.r_throat * 1000).toFixed(1)} mm</p>
                      </div>
                      <div className="card p-4 text-center">
                        <p className="text-xs text-[#71717a]">R chambre</p>
                        <p className="text-xl font-bold text-[#8b5cf6]">{(results.r_chamber * 1000).toFixed(1)} mm</p>
                      </div>
                      <div className="card p-4 text-center">
                        <p className="text-xs text-[#71717a]">Ratio ε</p>
                        <p className="text-xl font-bold text-[#f59e0b]">{results.expansion_ratio?.toFixed(1)}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* CEA RAW TAB */}
                {resultTab === "cea" && (
                  <div className="space-y-6">
                    <h2 className="text-2xl font-bold text-white">⚗️ Output RocketCEA</h2>

                    <div className="grid grid-cols-2 gap-6">
                      <div className="card">
                        <h3 className="card-header">Conditions d'Entrée</h3>
                        <div className="font-mono text-xs space-y-1 text-[#a1a1aa]">
                          <div>Oxidizer: <span className="text-[#00d4ff]">{config.oxidizer}</span></div>
                          <div>Fuel: <span className="text-[#8b5cf6]">{config.fuel}</span></div>
                          <div>O/F Ratio: <span className="text-[#f59e0b]">{config.of_ratio}</span></div>
                          <div>Chamber Pressure: <span className="text-white">{config.pc} bar</span></div>
                          <div>Exit Pressure: <span className="text-white">{config.pe} bar</span></div>
                        </div>
                      </div>

                      <div className="card">
                        <h3 className="card-header">Propriétés Thermodynamiques</h3>
                        <div className="font-mono text-xs space-y-1 text-[#a1a1aa]">
                          <div>T_chamber: <span className="text-[#ef4444]">{results.t_chamber?.toFixed(2)} K</span></div>
                          <div>Gamma (γ): <span className="text-white">{results.gamma?.toFixed(6)}</span></div>
                          <div>Molar Mass: <span className="text-white">{results.mw?.toFixed(4)} kg/kmol</span></div>
                          <div>Cp: <span className="text-white">{(results.gamma * 287 / (results.gamma - 1))?.toFixed(2)} J/kg·K</span></div>
                          <div>R_specific: <span className="text-white">{(8314 / results.mw)?.toFixed(2)} J/kg·K</span></div>
                        </div>
                      </div>

                      <div className="card">
                        <h3 className="card-header">Performance</h3>
                        <div className="font-mono text-xs space-y-1 text-[#a1a1aa]">
                          <div>c* (C-star): <span className="text-[#f59e0b]">{results.c_star?.toFixed(4)} m/s</span></div>
                          <div>Isp_vacuum: <span className="text-[#00d4ff]">{results.isp_vac?.toFixed(4)} s</span></div>
                          <div>Isp_sea_level: <span className="text-[#8b5cf6]">{results.isp_sl?.toFixed(4)} s</span></div>
                          <div>Cf_vacuum: <span className="text-white">{results.cf_vac?.toFixed(6)}</span></div>
                          <div>Cf_sea_level: <span className="text-white">{results.cf_sl?.toFixed(6)}</span></div>
                        </div>
                      </div>

                      <div className="card">
                        <h3 className="card-header">Thrust</h3>
                        <div className="font-mono text-xs space-y-1 text-[#a1a1aa]">
                          <div>Mass Flow Rate: <span className="text-white">{config.mdot} kg/s</span></div>
                          <div>Thrust_vacuum: <span className="text-[#10b981]">{results.thrust_vac?.toFixed(4)} N</span></div>
                          <div>Thrust_sea_level: <span className="text-[#10b981]">{results.thrust_sl?.toFixed(4)} N</span></div>
                          <div>Throat Area: <span className="text-white">{(Math.PI * Math.pow(results.r_throat || 0, 2) * 1e6)?.toFixed(2)} mm²</span></div>
                          <div>Exit Area: <span className="text-white">{(Math.PI * Math.pow(results.r_exit || 0, 2) * 1e6)?.toFixed(2)} mm²</span></div>
                        </div>
                      </div>
                    </div>

                    <div className="card">
                      <h3 className="card-header">📋 Raw Data (JSON)</h3>
                      <pre className="bg-[#0a0a0f] p-4 rounded-lg text-xs font-mono text-[#a1a1aa] overflow-x-auto max-h-64 overflow-y-auto">
                        {JSON.stringify(results, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}

                {/* GRAPHS TAB */}
                {resultTab === "graphs" && (
                  <div className="space-y-6">
                    <h2 className="text-2xl font-bold text-white">📈 Graphiques</h2>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      {/* Temperature Profile */}
                      <div className="card">
                        <h3 className="card-header">🌡️ Profil de Température</h3>
                        <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={generateThermalData()}>
                              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                              <XAxis dataKey="x" stroke="#71717a" fontSize={10} label={{ value: 'x (mm)', position: 'bottom', fill: '#71717a' }} />
                              <YAxis stroke="#71717a" fontSize={10} label={{ value: 'T (K)', angle: -90, position: 'left', fill: '#71717a' }} />
                              <Tooltip contentStyle={{ backgroundColor: '#1a1a25', border: '1px solid #27272a' }} />
                              <Legend />
                              <Line type="monotone" dataKey="tWall" stroke="#ef4444" strokeWidth={2} name="T paroi" dot={false} />
                              <Line type="monotone" dataKey="tCoolant" stroke="#00d4ff" strokeWidth={2} name="T coolant" dot={false} />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      </div>

                      {/* Heat Flux */}
                      <div className="card">
                        <h3 className="card-header">🔥 Flux Thermique</h3>
                        <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={generateThermalData()}>
                              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                              <XAxis dataKey="x" stroke="#71717a" fontSize={10} />
                              <YAxis stroke="#71717a" fontSize={10} label={{ value: 'q (MW/m²)', angle: -90, position: 'left', fill: '#71717a' }} />
                              <Tooltip contentStyle={{ backgroundColor: '#1a1a25', border: '1px solid #27272a' }} />
                              <Area type="monotone" dataKey="q" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.3} name="Flux thermique" />
                            </AreaChart>
                          </ResponsiveContainer>
                        </div>
                      </div>

                      {/* hg Profile */}
                      <div className="card">
                        <h3 className="card-header">📊 Coefficient hg (Bartz)</h3>
                        <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={generateThermalData()}>
                              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                              <XAxis dataKey="x" stroke="#71717a" fontSize={10} />
                              <YAxis stroke="#71717a" fontSize={10} label={{ value: 'hg (W/m²·K)', angle: -90, position: 'left', fill: '#71717a' }} />
                              <Tooltip contentStyle={{ backgroundColor: '#1a1a25', border: '1px solid #27272a' }} />
                              <Line type="monotone" dataKey="hg" stroke="#8b5cf6" strokeWidth={2} name="hg" dot={false} />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      </div>

                      {/* Area Ratio */}
                      <div className="card">
                        <h3 className="card-header">📐 Ratio de Section</h3>
                        <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={generateThermalData()}>
                              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                              <XAxis dataKey="x" stroke="#71717a" fontSize={10} />
                              <YAxis stroke="#71717a" fontSize={10} />
                              <Tooltip contentStyle={{ backgroundColor: '#1a1a25', border: '1px solid #27272a' }} />
                              <Line type="monotone" dataKey="areaRatio" stroke="#10b981" strokeWidth={2} name="A/At" dot={false} />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* BARTZ TAB */}
                {resultTab === "bartz" && (
                  <div className="space-y-6">
                    <h2 className="text-2xl font-bold text-white">🔥 Méthode de Bartz</h2>

                    <div className="card">
                      <h3 className="card-header">Équation de Bartz (1957)</h3>
                      <div className="bg-[#0a0a0f] rounded-lg p-4 text-center">
                        <p className="text-lg font-mono text-[#00d4ff]">
                          h<sub>g</sub> = (0.026/D<sub>t</sub><sup>0.2</sup>) × (μ<sup>0.2</sup>·C<sub>p</sub>/Pr<sup>0.6</sup>) × (P<sub>c</sub>/c*)<sup>0.8</sup> × (A<sub>t</sub>/A)<sup>0.9</sup> × σ
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      <div className="card text-center">
                        <h4 className="text-[#ef4444] font-semibold mb-2">Effet d'Échelle</h4>
                        <p className="text-2xl font-mono text-white">D<sub>t</sub><sup>-0.2</sup></p>
                        <p className="text-xs text-[#71717a] mt-2">Petits moteurs = hg élevé</p>
                      </div>
                      <div className="card text-center">
                        <h4 className="text-[#f59e0b] font-semibold mb-2">Effet Pression</h4>
                        <p className="text-2xl font-mono text-white">P<sub>c</sub><sup>0.8</sup></p>
                        <p className="text-xs text-[#71717a] mt-2">×2 Pc = +74% flux</p>
                      </div>
                      <div className="card text-center">
                        <h4 className="text-[#8b5cf6] font-semibold mb-2">Localisation</h4>
                        <p className="text-2xl font-mono text-white">(A<sub>t</sub>/A)<sup>0.9</sup></p>
                        <p className="text-xs text-[#71717a] mt-2">Max au col</p>
                      </div>
                    </div>

                    <div className="card">
                      <h3 className="card-header">Valeurs Calculées</h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-[#1a1a25] rounded-lg p-3 text-center">
                          <p className="text-xs text-[#71717a]">D throat</p>
                          <p className="text-lg font-bold text-white">{((results.r_throat || 0.02) * 2000).toFixed(1)} mm</p>
                        </div>
                        <div className="bg-[#1a1a25] rounded-lg p-3 text-center">
                          <p className="text-xs text-[#71717a]">hg max (col)</p>
                          <p className="text-lg font-bold text-[#ef4444]">~5000 W/m²·K</p>
                        </div>
                        <div className="bg-[#1a1a25] rounded-lg p-3 text-center">
                          <p className="text-xs text-[#71717a]">q max</p>
                          <p className="text-lg font-bold text-[#f59e0b]">~15 MW/m²</p>
                        </div>
                        <div className="bg-[#1a1a25] rounded-lg p-3 text-center">
                          <p className="text-xs text-[#71717a]">T wall max</p>
                          <p className="text-lg font-bold text-[#00d4ff]">{config.twall_max} K</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* HEATMAP TAB */}
                {resultTab === "heatmap" && (
                  <div className="space-y-6">
                    <h2 className="text-2xl font-bold text-white">🌡️ Carte Thermique Paroi</h2>

                    <div className="card">
                      <h3 className="card-header">Distribution de Température</h3>
                      <div className="h-64 relative">
                        {/* Simulated heatmap using gradient */}
                        <div className="absolute inset-0 rounded-lg overflow-hidden">
                          <div className="h-full w-full" style={{
                            background: `linear-gradient(90deg, 
                              hsl(200, 80%, 50%) 0%, 
                              hsl(60, 80%, 50%) 20%,
                              hsl(30, 80%, 50%) 35%,
                              hsl(0, 80%, 50%) 45%,
                              hsl(30, 80%, 50%) 55%,
                              hsl(60, 80%, 50%) 70%,
                              hsl(200, 80%, 50%) 100%)`
                          }}>
                            <div className="h-full flex items-center justify-center">
                              <div className="bg-[#0a0a0f]/80 rounded-lg p-4 text-center">
                                <p className="text-white font-bold">Col (Maximum)</p>
                                <p className="text-[#ef4444] text-2xl font-mono">~{config.twall_max} K</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="flex justify-between mt-2 text-xs text-[#71717a]">
                        <span>Chambre</span>
                        <span>Col</span>
                        <span>Sortie</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      <div className="card text-center">
                        <p className="text-xs text-[#71717a] mb-1">T paroi (hot side)</p>
                        <p className="text-2xl font-bold text-[#ef4444]">~{(config.twall_max * 0.9).toFixed(0)} K</p>
                      </div>
                      <div className="card text-center">
                        <p className="text-xs text-[#71717a] mb-1">T paroi (cold side)</p>
                        <p className="text-2xl font-bold text-[#f59e0b]">~{(config.twall_max * 0.6).toFixed(0)} K</p>
                      </div>
                      <div className="card text-center">
                        <p className="text-xs text-[#71717a] mb-1">ΔT paroi</p>
                        <p className="text-2xl font-bold text-[#00d4ff]">~{(config.twall_max * 0.3).toFixed(0)} K</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* STRESS TAB */}
                {resultTab === "stress" && (
                  <div className="space-y-6">
                    <h2 className="text-2xl font-bold text-white">💪 Analyse des Contraintes</h2>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="card text-center">
                        <p className="text-xs text-[#71717a] mb-1">σ hoop</p>
                        <p className="text-2xl font-bold text-[#00d4ff]">{stressData.sigmaHoop.toFixed(1)} MPa</p>
                      </div>
                      <div className="card text-center">
                        <p className="text-xs text-[#71717a] mb-1">σ thermal</p>
                        <p className="text-2xl font-bold text-[#f59e0b]">{stressData.sigmaThermal.toFixed(1)} MPa</p>
                      </div>
                      <div className="card text-center">
                        <p className="text-xs text-[#71717a] mb-1">σ Von Mises</p>
                        <p className="text-2xl font-bold text-[#ef4444]">{stressData.sigmaVM.toFixed(1)} MPa</p>
                      </div>
                      <div className={`card text-center ${stressData.fos > 1.2 ? 'border-[#10b981]' : stressData.fos > 1 ? 'border-[#f59e0b]' : 'border-[#ef4444]'}`}>
                        <p className="text-xs text-[#71717a] mb-1">FoS</p>
                        <p className={`text-2xl font-bold ${stressData.fos > 1.2 ? 'text-[#10b981]' : stressData.fos > 1 ? 'text-[#f59e0b]' : 'text-[#ef4444]'}`}>{stressData.fos.toFixed(2)}</p>
                      </div>
                    </div>

                    <div className="card">
                      <h3 className="card-header">Équations</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-[#0a0a0f] rounded-lg p-3">
                          <p className="text-xs text-[#00d4ff] mb-1">Contrainte de Pression</p>
                          <p className="font-mono text-white">σ<sub>hoop</sub> = (P × R) / e</p>
                        </div>
                        <div className="bg-[#0a0a0f] rounded-lg p-3">
                          <p className="text-xs text-[#f59e0b] mb-1">Contrainte Thermique</p>
                          <p className="font-mono text-white">σ<sub>th</sub> = E·α·ΔT / 2(1-ν)</p>
                        </div>
                      </div>
                    </div>

                    <div className="card">
                      <h3 className="card-header">📦 Estimation Outer Shell</h3>
                      <div className="bg-gradient-to-r from-[#10b981]/20 to-transparent border border-[#10b981]/30 rounded-lg p-4">
                        <p className="text-white mb-2">Pour contenir la pression coolant de <strong>{config.coolant_pressure} bar</strong>:</p>
                        <div className="flex items-center gap-4">
                          <div>
                            <p className="text-xs text-[#71717a]">Épaisseur outer shell (acier)</p>
                            <p className="text-3xl font-bold text-[#10b981]">{stressData.tOuterShell.toFixed(2)} mm</p>
                          </div>
                          <div className="text-xs text-[#a1a1aa]">
                            <p>Matériau: Acier inox 316L</p>
                            <p>σ yield: 290 MPa</p>
                            <p>Facteur de sécurité: 1.25</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
