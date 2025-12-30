"use client";

import { useState, useEffect } from "react";
import AppLayout from "@/components/AppLayout";

export default function MaterialsPage() {
    const [materials, setMaterials] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [selectedMaterial, setSelectedMaterial] = useState<string | null>(null);

    useEffect(() => {
        loadMaterials();
    }, []);

    const loadMaterials = async () => {
        try {
            const res = await fetch("http://localhost:8000/api/materials");
            const data = await res.json();
            setMaterials(data.materials);
        } catch (e) {
            console.error("Failed to load materials:", e);
        } finally {
            setLoading(false);
        }
    };

    const categories = {
        "Cuivre & Alliages": ["Cuivre (Cu-OFHC)", "Cuivre-Chrome (CuCr)", "Cuivre-Zirconium (CuZr)", "GlidCop AL-15", "CuCrNb (GRCop-42)"],
        "Aluminium": ["AlSi10Mg (SLM)", "Aluminium 7075-T6", "Aluminium 6061-T6"],
        "Superalliages": ["Inconel 718", "Inconel 625", "Monel 400", "Hastelloy X"],
        "Aciers Inox": ["Acier Inox 316L", "Acier Inox 304L", "Acier Inox 17-4PH"],
        "Réfractaires": ["Titane Ti-6Al-4V", "Niobium C-103", "Molybdène (TZM)"],
    };

    return (
        <AppLayout>
            <div className="p-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Base de Données Matériaux</h1>
                    <p className="text-[#71717a]">Propriétés thermiques et mécaniques des matériaux pour moteurs-fusées</p>
                </div>

                {loading ? (
                    <div className="card text-center py-12">
                        <span className="text-2xl animate-spin inline-block mb-4">⏳</span>
                        <p className="text-[#71717a]">Chargement des matériaux...</p>
                    </div>
                ) : materials ? (
                    <div className="grid grid-cols-12 gap-6">
                        {/* Categories */}
                        <div className="col-span-12 lg:col-span-4 space-y-4">
                            {Object.entries(categories).map(([category, names]) => (
                                <div key={category} className="card">
                                    <h3 className="card-header">{category}</h3>
                                    <div className="space-y-1">
                                        {names.filter(name => materials[name]).map(name => (
                                            <button
                                                key={name}
                                                onClick={() => setSelectedMaterial(name)}
                                                className={`w-full text-left px-3 py-2 rounded-lg transition-all ${selectedMaterial === name
                                                        ? 'bg-[#00d4ff]/20 text-[#00d4ff] border border-[#00d4ff]/30'
                                                        : 'hover:bg-[#1f1f2e] text-[#a1a1aa] hover:text-white'
                                                    }`}
                                            >
                                                <span className="text-sm font-medium">{name}</span>
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Details */}
                        <div className="col-span-12 lg:col-span-8">
                            {selectedMaterial && materials[selectedMaterial] ? (
                                <div className="card">
                                    <h2 className="text-2xl font-bold text-white mb-6">{selectedMaterial}</h2>

                                    {/* Quick Stats */}
                                    <div className="grid grid-cols-3 gap-4 mb-6">
                                        <div className="stat-card glow-cyan">
                                            <p className="text-xs text-[#00d4ff] uppercase tracking-wider mb-1">Conductivité</p>
                                            <p className="stat-value">{materials[selectedMaterial].k}<span className="stat-unit">W/mK</span></p>
                                        </div>
                                        <div className="stat-card">
                                            <p className="text-xs text-[#f59e0b] uppercase tracking-wider mb-1">T Max Service</p>
                                            <p className="stat-value">{materials[selectedMaterial].T_max}<span className="stat-unit">K</span></p>
                                        </div>
                                        <div className="stat-card">
                                            <p className="text-xs text-[#ec4899] uppercase tracking-wider mb-1">T Fusion</p>
                                            <p className="stat-value">{materials[selectedMaterial].T_melt}<span className="stat-unit">K</span></p>
                                        </div>
                                    </div>

                                    {/* All Properties */}
                                    <div className="grid grid-cols-2 gap-6">
                                        <div>
                                            <h4 className="text-sm font-semibold text-[#a1a1aa] uppercase tracking-wider mb-4">Thermique</h4>
                                            <div className="data-grid">
                                                <div className="data-row">
                                                    <span className="data-label">Conductivité (k)</span>
                                                    <span className="data-value">{materials[selectedMaterial].k} W/mK</span>
                                                </div>
                                                <div className="data-row">
                                                    <span className="data-label">Expansion (α)</span>
                                                    <span className="data-value">{materials[selectedMaterial].alpha} ×10⁻⁶/K</span>
                                                </div>
                                                <div className="data-row">
                                                    <span className="data-label">T max service</span>
                                                    <span className="data-value">{materials[selectedMaterial].T_max} K</span>
                                                </div>
                                                <div className="data-row">
                                                    <span className="data-label">T fusion</span>
                                                    <span className="data-value">{materials[selectedMaterial].T_melt} K</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div>
                                            <h4 className="text-sm font-semibold text-[#a1a1aa] uppercase tracking-wider mb-4">Mécanique</h4>
                                            <div className="data-grid">
                                                <div className="data-row">
                                                    <span className="data-label">Module Young (E)</span>
                                                    <span className="data-value">{materials[selectedMaterial].E} GPa</span>
                                                </div>
                                                <div className="data-row">
                                                    <span className="data-label">Coef. Poisson (ν)</span>
                                                    <span className="data-value">{materials[selectedMaterial].nu}</span>
                                                </div>
                                                <div className="data-row">
                                                    <span className="data-label">Limite élastique (σy)</span>
                                                    <span className="data-value">{materials[selectedMaterial].sigma_y} MPa</span>
                                                </div>
                                                <div className="data-row">
                                                    <span className="data-label">Résistance (σuts)</span>
                                                    <span className="data-value">{materials[selectedMaterial].sigma_uts} MPa</span>
                                                </div>
                                                <div className="data-row">
                                                    <span className="data-label">Densité (ρ)</span>
                                                    <span className="data-value">{materials[selectedMaterial].rho} kg/m³</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div className="card h-full flex items-center justify-center text-center py-20">
                                    <div>
                                        <span className="text-5xl mb-4 block">🧱</span>
                                        <h3 className="text-xl font-bold text-white mb-2">Sélectionnez un matériau</h3>
                                        <p className="text-[#71717a]">Cliquez sur un matériau pour voir ses propriétés détaillées</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                ) : (
                    <div className="card text-center py-12">
                        <span className="text-5xl mb-4 block">❌</span>
                        <p className="text-[#ef4444]">Erreur de connexion au serveur Rust</p>
                        <p className="text-[#71717a] text-sm mt-2">Vérifiez que le serveur est démarré sur le port 8000</p>
                    </div>
                )}
            </div>
        </AppLayout>
    );
}
