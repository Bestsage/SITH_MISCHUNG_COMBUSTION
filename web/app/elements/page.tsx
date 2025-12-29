"use client";

import { useState } from "react";
import AppLayout from "@/components/AppLayout";

// CEA Propellant database
const oxidizers = [
    { name: "O2", formula: "O2", description: "Oxygène Liquide (LOX)", tBoil: 90.2, density: 1141, enthalpy: 0, common: true },
    { name: "N2O", formula: "N2O", description: "Protoxyde d'azote", tBoil: 184.7, density: 1230, enthalpy: 82.05, common: true },
    { name: "N2O4", formula: "N2O4", description: "Tétroxyde de diazote", tBoil: 294.3, density: 1450, enthalpy: -19.56, common: true },
    { name: "H2O2", formula: "H2O2", description: "Peroxyde d'hydrogène", tBoil: 423.4, density: 1450, enthalpy: -187.8, common: true },
    { name: "ClF3", formula: "ClF3", description: "Trifluorure de chlore", tBoil: 284.9, density: 1770, enthalpy: -163.2, common: false },
    { name: "ClF5", formula: "ClF5", description: "Pentafluorure de chlore", tBoil: 260.2, density: 1900, enthalpy: -238.5, common: false },
    { name: "F2", formula: "F2", description: "Fluor liquide", tBoil: 85.0, density: 1505, enthalpy: 0, common: false },
    { name: "IRFNA", formula: "HNO3", description: "Acide nitrique fumant rouge", tBoil: 356.0, density: 1560, enthalpy: -174.1, common: true },
    { name: "MON25", formula: "N2O4+NO", description: "Mixed Oxides of Nitrogen", tBoil: 288.0, density: 1430, enthalpy: -10.0, common: true },
    { name: "N2O4", formula: "N2O4", description: "Aérozine (NTO)", tBoil: 294.3, density: 1443, enthalpy: -19.56, common: true },
];

const fuels = [
    { name: "H2", formula: "H2", description: "Hydrogène Liquide (LH2)", tBoil: 20.3, density: 71, enthalpy: 0, common: true },
    { name: "CH4", formula: "CH4", description: "Méthane (LNG)", tBoil: 111.7, density: 422, enthalpy: -74.9, common: true },
    { name: "C3H8", formula: "C3H8", description: "Propane", tBoil: 231.0, density: 493, enthalpy: -104.7, common: true },
    { name: "RP-1", formula: "C12H24", description: "Kérosène raffiné", tBoil: 489.0, density: 810, enthalpy: -24.7, common: true },
    { name: "C2H5OH", formula: "C2H5OH", description: "Éthanol", tBoil: 351.4, density: 789, enthalpy: -277.0, common: true },
    { name: "CH3OH", formula: "CH3OH", description: "Méthanol", tBoil: 337.8, density: 792, enthalpy: -239.2, common: true },
    { name: "MMH", formula: "CH3NHNH2", description: "Monométhylhydrazine", tBoil: 360.6, density: 878, enthalpy: 54.84, common: true },
    { name: "UDMH", formula: "(CH3)2NNH2", description: "Diméthylhydrazine asymétrique", tBoil: 336.0, density: 793, enthalpy: 83.3, common: true },
    { name: "N2H4", formula: "N2H4", description: "Hydrazine", tBoil: 386.7, density: 1021, enthalpy: 50.63, common: true },
    { name: "NH3", formula: "NH3", description: "Ammoniac", tBoil: 239.8, density: 682, enthalpy: -45.9, common: false },
    { name: "Aerozine-50", formula: "N2H4+UDMH", description: "50% Hydrazine + 50% UDMH", tBoil: 340.0, density: 903, enthalpy: 67.0, common: true },
];

const propellantCombos = [
    { ox: "O2", fuel: "H2", isp: 455, tc: 3300, ofOpt: 6.0, usage: "Delta IV, SLS, Ariane 5" },
    { ox: "O2", fuel: "CH4", isp: 365, tc: 3550, ofOpt: 3.6, usage: "Raptor, BE-4" },
    { ox: "O2", fuel: "RP-1", isp: 340, tc: 3600, ofOpt: 2.7, usage: "Falcon 9, Atlas V" },
    { ox: "O2", fuel: "C3H8", isp: 340, tc: 3500, ofOpt: 2.8, usage: "Amateur, Test" },
    { ox: "O2", fuel: "C2H5OH", isp: 310, tc: 3200, ofOpt: 1.8, usage: "V-2, Amateur" },
    { ox: "N2O4", fuel: "MMH", isp: 320, tc: 3300, ofOpt: 2.2, usage: "Proton, Dragon" },
    { ox: "N2O4", fuel: "UDMH", isp: 315, tc: 3250, ofOpt: 2.6, usage: "Proton, Long March" },
    { ox: "N2O4", fuel: "Aerozine-50", isp: 318, tc: 3280, ofOpt: 2.0, usage: "Titan, Apollo SPS" },
    { ox: "N2O", fuel: "C3H8", isp: 280, tc: 2800, ofOpt: 8.0, usage: "Hybrid, Amateur" },
    { ox: "H2O2", fuel: "RP-1", isp: 300, tc: 3000, ofOpt: 7.5, usage: "Black Arrow" },
];

export default function ElementsPage() {
    const [activeTab, setActiveTab] = useState<"oxidizers" | "fuels" | "combos">("oxidizers");
    const [searchQuery, setSearchQuery] = useState("");

    const filteredOxidizers = oxidizers.filter(o =>
        o.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        o.description.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const filteredFuels = fuels.filter(f =>
        f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        f.description.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <AppLayout>
            <div className="p-6 h-full overflow-y-auto">
                <div className="max-w-6xl mx-auto">
                    <div className="mb-6">
                        <h1 className="text-3xl font-bold text-white mb-2">⚗️ Base de Données Propergols</h1>
                        <p className="text-[#71717a]">Éléments CEA • Oxydants • Carburants • Combinaisons</p>
                    </div>

                    {/* Search */}
                    <div className="mb-6">
                        <input
                            type="text"
                            placeholder="🔍 Rechercher un propergol..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="input-field w-full max-w-md"
                        />
                    </div>

                    {/* Tabs */}
                    <div className="flex border-b border-[#27272a] mb-6">
                        {[
                            { key: "oxidizers", label: "🔴 Oxydants", count: oxidizers.length },
                            { key: "fuels", label: "🔵 Carburants", count: fuels.length },
                            { key: "combos", label: "⚡ Combinaisons", count: propellantCombos.length },
                        ].map((tab) => (
                            <button
                                key={tab.key}
                                onClick={() => setActiveTab(tab.key as any)}
                                className={`px-6 py-3 font-medium transition-all ${activeTab === tab.key
                                        ? "text-[#00d4ff] border-b-2 border-[#00d4ff]"
                                        : "text-[#71717a] hover:text-white"
                                    }`}
                            >
                                {tab.label} <span className="text-xs opacity-60">({tab.count})</span>
                            </button>
                        ))}
                    </div>

                    {/* Content */}
                    {activeTab === "oxidizers" && (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {filteredOxidizers.map((ox) => (
                                <div key={ox.name} className={`card ${ox.common ? 'border-[#ef4444]/30' : ''}`}>
                                    <div className="flex items-center gap-3 mb-3">
                                        <span className="text-2xl">🔴</span>
                                        <div>
                                            <h3 className="font-bold text-white">{ox.name}</h3>
                                            <p className="text-xs text-[#71717a]">{ox.formula}</p>
                                        </div>
                                        {ox.common && <span className="ml-auto text-xs bg-[#ef4444]/20 text-[#ef4444] px-2 py-1 rounded">Commun</span>}
                                    </div>
                                    <p className="text-sm text-[#a1a1aa] mb-3">{ox.description}</p>
                                    <div className="grid grid-cols-3 gap-2 text-center text-xs">
                                        <div className="bg-[#1a1a25] rounded p-2">
                                            <p className="text-[#71717a]">T ébull.</p>
                                            <p className="text-white font-mono">{ox.tBoil} K</p>
                                        </div>
                                        <div className="bg-[#1a1a25] rounded p-2">
                                            <p className="text-[#71717a]">ρ</p>
                                            <p className="text-white font-mono">{ox.density} kg/m³</p>
                                        </div>
                                        <div className="bg-[#1a1a25] rounded p-2">
                                            <p className="text-[#71717a]">ΔHf</p>
                                            <p className="text-white font-mono">{ox.enthalpy} kJ/mol</p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {activeTab === "fuels" && (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {filteredFuels.map((fuel) => (
                                <div key={fuel.name} className={`card ${fuel.common ? 'border-[#3b82f6]/30' : ''}`}>
                                    <div className="flex items-center gap-3 mb-3">
                                        <span className="text-2xl">🔵</span>
                                        <div>
                                            <h3 className="font-bold text-white">{fuel.name}</h3>
                                            <p className="text-xs text-[#71717a]">{fuel.formula}</p>
                                        </div>
                                        {fuel.common && <span className="ml-auto text-xs bg-[#3b82f6]/20 text-[#3b82f6] px-2 py-1 rounded">Commun</span>}
                                    </div>
                                    <p className="text-sm text-[#a1a1aa] mb-3">{fuel.description}</p>
                                    <div className="grid grid-cols-3 gap-2 text-center text-xs">
                                        <div className="bg-[#1a1a25] rounded p-2">
                                            <p className="text-[#71717a]">T ébull.</p>
                                            <p className="text-white font-mono">{fuel.tBoil} K</p>
                                        </div>
                                        <div className="bg-[#1a1a25] rounded p-2">
                                            <p className="text-[#71717a]">ρ</p>
                                            <p className="text-white font-mono">{fuel.density} kg/m³</p>
                                        </div>
                                        <div className="bg-[#1a1a25] rounded p-2">
                                            <p className="text-[#71717a]">ΔHf</p>
                                            <p className="text-white font-mono">{fuel.enthalpy} kJ/mol</p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {activeTab === "combos" && (
                        <div className="space-y-4">
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead>
                                        <tr className="border-b border-[#27272a]">
                                            <th className="px-4 py-3 text-left text-[#a1a1aa]">Oxydant</th>
                                            <th className="px-4 py-3 text-left text-[#a1a1aa]">Carburant</th>
                                            <th className="px-4 py-3 text-center text-[#a1a1aa]">Isp (s)</th>
                                            <th className="px-4 py-3 text-center text-[#a1a1aa]">Tc (K)</th>
                                            <th className="px-4 py-3 text-center text-[#a1a1aa]">O/F opt</th>
                                            <th className="px-4 py-3 text-left text-[#a1a1aa]">Utilisations</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {propellantCombos.map((combo, i) => (
                                            <tr key={i} className="border-b border-[#27272a]/50 hover:bg-[#1a1a25]">
                                                <td className="px-4 py-3">
                                                    <span className="text-[#ef4444] font-mono">{combo.ox}</span>
                                                </td>
                                                <td className="px-4 py-3">
                                                    <span className="text-[#3b82f6] font-mono">{combo.fuel}</span>
                                                </td>
                                                <td className="px-4 py-3 text-center">
                                                    <span className={`font-bold ${combo.isp >= 400 ? 'text-[#10b981]' : combo.isp >= 330 ? 'text-[#f59e0b]' : 'text-white'}`}>
                                                        {combo.isp}
                                                    </span>
                                                </td>
                                                <td className="px-4 py-3 text-center text-white font-mono">{combo.tc}</td>
                                                <td className="px-4 py-3 text-center text-[#8b5cf6] font-mono">{combo.ofOpt}</td>
                                                <td className="px-4 py-3 text-[#71717a] text-xs">{combo.usage}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </AppLayout>
    );
}
