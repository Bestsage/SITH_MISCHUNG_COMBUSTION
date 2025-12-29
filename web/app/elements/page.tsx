"use client";

import { useState, useEffect } from "react";
import AppLayout from "@/components/AppLayout";

interface PropellantItem {
    name: string;
    type: string;
    card: string;
}

export default function ElementsPage() {
    const [activeTab, setActiveTab] = useState<"fuels" | "oxidizers">("fuels");
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedElement, setSelectedElement] = useState<PropellantItem | null>(null);
    const [loading, setLoading] = useState(true);
    const [fuels, setFuels] = useState<PropellantItem[]>([]);
    const [oxidizers, setOxidizers] = useState<PropellantItem[]>([]);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadPropellants();
    }, []);

    const loadPropellants = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch("http://localhost:8001/propellants");
            const data = await res.json();
            if (data.error) {
                setError(data.error);
            } else {
                setFuels(data.fuels || []);
                setOxidizers(data.oxidizers || []);
            }
        } catch (e) {
            setError("Impossible de charger les propergols. Le service CEA est-il en marche sur le port 8001?");
            console.error("Load propellants failed:", e);
        } finally {
            setLoading(false);
        }
    };

    const currentList = activeTab === "fuels" ? fuels : oxidizers;

    const filteredList = currentList.filter(item =>
        item.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <AppLayout>
            <div className="h-[calc(100vh-64px)] flex overflow-hidden">
                {/* Left Panel - List */}
                <div className="w-80 h-full bg-[#12121a] border-r border-[#27272a] flex flex-col flex-shrink-0">
                    <div className="p-4 border-b border-[#27272a]">
                        <h1 className="text-lg font-bold text-white mb-3">⚗️ Éléments CEA</h1>

                        {/* Search */}
                        <input
                            type="text"
                            placeholder="🔍 Rechercher..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="input-field w-full text-sm mb-3"
                        />

                        {/* Tabs */}
                        <div className="flex gap-2">
                            <button
                                onClick={() => { setActiveTab("fuels"); setSelectedElement(null); }}
                                className={`flex-1 py-2 px-3 text-sm font-medium rounded transition-all ${activeTab === "fuels"
                                    ? "bg-[#3b82f6]/20 text-[#3b82f6]"
                                    : "text-[#71717a] hover:text-white hover:bg-[#1a1a25]"
                                    }`}
                            >
                                🔵 Fuels ({fuels.length})
                            </button>
                            <button
                                onClick={() => { setActiveTab("oxidizers"); setSelectedElement(null); }}
                                className={`flex-1 py-2 px-3 text-sm font-medium rounded transition-all ${activeTab === "oxidizers"
                                    ? "bg-[#ef4444]/20 text-[#ef4444]"
                                    : "text-[#71717a] hover:text-white hover:bg-[#1a1a25]"
                                    }`}
                            >
                                🔴 Oxid ({oxidizers.length})
                            </button>
                        </div>
                    </div>

                    {/* Element List */}
                    <div className="flex-1 overflow-y-auto">
                        {loading ? (
                            <div className="p-4 text-center text-[#71717a]">
                                <span className="animate-spin inline-block mr-2">⏳</span>
                                Chargement...
                            </div>
                        ) : error ? (
                            <div className="p-4 text-center">
                                <p className="text-[#ef4444] text-sm mb-2">⚠️ Erreur</p>
                                <p className="text-[#71717a] text-xs">{error}</p>
                                <button onClick={loadPropellants} className="btn-secondary mt-3 text-xs">
                                    🔄 Réessayer
                                </button>
                            </div>
                        ) : filteredList.length === 0 ? (
                            <div className="p-4 text-center text-[#71717a] text-sm">
                                Aucun résultat
                            </div>
                        ) : (
                            filteredList.map((item) => (
                                <button
                                    key={item.name}
                                    onClick={() => setSelectedElement(item)}
                                    className={`w-full text-left px-4 py-3 border-b border-[#27272a]/50 hover:bg-[#1a1a25] transition-colors ${selectedElement?.name === item.name ? "bg-[#1a1a25] border-l-2 border-l-[#00d4ff]" : ""
                                        }`}
                                >
                                    <div className="flex items-center gap-2">
                                        <span className={`w-2 h-2 rounded-full ${item.type === "fuel" ? "bg-[#3b82f6]" : "bg-[#ef4444]"}`}></span>
                                        <span className="font-mono text-sm text-white font-bold">{item.name}</span>
                                    </div>
                                </button>
                            ))
                        )}
                    </div>

                    {/* Stats */}
                    <div className="p-3 border-t border-[#27272a] text-xs text-[#71717a]">
                        {fuels.length} Fuels • {oxidizers.length} Oxidizers
                    </div>
                </div>

                {/* Right Panel - Details */}
                <div className="flex-1 h-full overflow-y-auto p-6">
                    {selectedElement ? (
                        <div className="max-w-2xl mx-auto space-y-6">
                            {/* Header */}
                            <div className="flex items-center gap-4">
                                <div className={`w-16 h-16 rounded-xl flex items-center justify-center text-2xl font-bold ${selectedElement.type === "oxidizer" ? "bg-[#ef4444]/20 text-[#ef4444]" : "bg-[#3b82f6]/20 text-[#3b82f6]"
                                    }`}>
                                    {selectedElement.type === "fuel" ? "🔵" : "🔴"}
                                </div>
                                <div>
                                    <h2 className="text-2xl font-bold text-white font-mono">{selectedElement.name}</h2>
                                    <p className="text-[#71717a] capitalize">{selectedElement.type}</p>
                                </div>
                            </div>

                            {/* CEA Card */}
                            <div className="card">
                                <h3 className="card-header">📋 CEA Card</h3>
                                <pre className="bg-[#0a0a0f] p-4 rounded-lg text-xs font-mono text-[#00d4ff] overflow-x-auto whitespace-pre-wrap">
                                    {selectedElement.card || "No card data available"}
                                </pre>
                            </div>

                            {/* Usage Example */}
                            <div className="card">
                                <h3 className="card-header">💡 Utilisation CEA</h3>
                                <pre className="bg-[#0a0a0f] p-4 rounded-lg text-sm font-mono text-white overflow-x-auto">
                                    {`from rocketcea.cea_obj import CEA_Obj

cea = CEA_Obj(
    ${selectedElement.type === "fuel" ? "fuelName" : "oxName"}="${selectedElement.name}",
    ${selectedElement.type === "fuel" ? "oxName" : "fuelName"}="LOX"
)

Isp = cea.get_Isp(Pc=25.0, MR=2.5, eps=40.0)`}
                                </pre>
                            </div>

                            {/* Common Combinations */}
                            <div className="card bg-gradient-to-r from-[#00d4ff]/5 to-transparent border-[#00d4ff]/20">
                                <h3 className="card-header">⚡ Combinaisons Typiques</h3>
                                {selectedElement.type === "fuel" ? (
                                    <div className="grid grid-cols-3 gap-2 text-sm">
                                        <div className="bg-[#1a1a25] rounded p-2 text-center">
                                            <p className="text-[#ef4444]">+ O2(L)</p>
                                            <p className="text-[#71717a] text-xs">Standard</p>
                                        </div>
                                        <div className="bg-[#1a1a25] rounded p-2 text-center">
                                            <p className="text-[#ef4444]">+ N2O4</p>
                                            <p className="text-[#71717a] text-xs">Hypergolic</p>
                                        </div>
                                        <div className="bg-[#1a1a25] rounded p-2 text-center">
                                            <p className="text-[#ef4444]">+ H2O2</p>
                                            <p className="text-[#71717a] text-xs">Green</p>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="grid grid-cols-3 gap-2 text-sm">
                                        <div className="bg-[#1a1a25] rounded p-2 text-center">
                                            <p className="text-[#3b82f6]">+ RP-1</p>
                                            <p className="text-[#71717a] text-xs">Kerolox</p>
                                        </div>
                                        <div className="bg-[#1a1a25] rounded p-2 text-center">
                                            <p className="text-[#3b82f6]">+ CH4</p>
                                            <p className="text-[#71717a] text-xs">Methalox</p>
                                        </div>
                                        <div className="bg-[#1a1a25] rounded p-2 text-center">
                                            <p className="text-[#3b82f6]">+ H2</p>
                                            <p className="text-[#71717a] text-xs">Hydrolox</p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex items-center justify-center">
                            <div className="text-center">
                                <span className="text-6xl mb-4 block">⚗️</span>
                                <h3 className="text-xl font-bold text-white mb-2">Base de Données CEA</h3>
                                <p className="text-[#71717a] mb-4">Sélectionnez un propergol pour voir ses données CEA</p>
                                <div className="text-sm text-[#52525b]">
                                    {fuels.length} fuels • {oxidizers.length} oxidizers
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </AppLayout>
    );
}
