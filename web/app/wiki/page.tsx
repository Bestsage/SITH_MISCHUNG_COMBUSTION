"use client";

import { useState } from "react";
import AppLayout from "@/components/AppLayout";

export default function WikiPage() {
    const [activeSection, setActiveSection] = useState("intro");

    const sections = [
        { id: "intro", title: "1. Introduction", icon: "🚀" },
        { id: "laval", title: "2. Tuyère de Laval", icon: "🔧" },
        { id: "thermal", title: "3. Problème Thermique", icon: "🔥" },
        { id: "regen", title: "4. Refroidissement Régénératif", icon: "❄️" },
        { id: "cea", title: "5. NASA CEA", icon: "⚗️" },
        { id: "bartz", title: "6. Équation de Bartz", icon: "📐" },
        { id: "channels", title: "7. Canaux de Refroidissement", icon: "🌊" },
        { id: "fluids", title: "8. Mécanique des Fluides", icon: "💨" },
        { id: "materials", title: "9-10. Matériaux", icon: "🧱" },
    ];

    return (
        <AppLayout>
            <div className="p-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">📖 Wiki - Guide de Conception</h1>
                    <p className="text-[#71717a]">Documentation complète pour la conception de moteurs-fusées</p>
                </div>

                <div className="grid grid-cols-12 gap-6">
                    {/* TOC */}
                    <div className="col-span-12 lg:col-span-3">
                        <div className="card sticky top-6">
                            <h3 className="card-header">📑 Sommaire</h3>
                            <div className="space-y-1">
                                {sections.map((section) => (
                                    <button
                                        key={section.id}
                                        onClick={() => setActiveSection(section.id)}
                                        className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all ${activeSection === section.id
                                                ? 'bg-[#00d4ff]/20 text-[#00d4ff]'
                                                : 'text-[#a1a1aa] hover:bg-[#1f1f2e] hover:text-white'
                                            }`}
                                    >
                                        <span className="mr-2">{section.icon}</span>
                                        {section.title}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Content */}
                    <div className="col-span-12 lg:col-span-9">
                        <div className="card prose prose-invert max-w-none">
                            {activeSection === "intro" && (
                                <div className="space-y-6">
                                    <h2 className="text-2xl font-bold text-white">🚀 Comment ça vole ?</h2>
                                    <p className="text-[#a1a1aa]">
                                        Une fusée ne "pousse" pas sur l'air ambiant. Elle fonctionne selon le principe de
                                        <strong className="text-white"> conservation de la quantité de mouvement</strong>.
                                        Elle éjecte de la masse à haute vitesse, créant une force opposée.
                                    </p>

                                    <div className="bg-[#1a1a25] rounded-lg p-4 border-l-4 border-[#00d4ff]">
                                        <h4 className="text-[#00d4ff] font-semibold mb-2">Équation de Poussée</h4>
                                        <code className="text-white text-lg">F = ṁ × Vₑ + (Pₑ - Pₐ) × Aₑ</code>
                                        <div className="mt-3 text-sm text-[#71717a]">
                                            <div>ṁ = Débit massique (kg/s)</div>
                                            <div>Vₑ = Vitesse d'éjection (m/s)</div>
                                            <div>Pₑ = Pression de sortie</div>
                                        </div>
                                    </div>

                                    <div className="bg-[#1a1a25] rounded-lg p-4 border-l-4 border-[#8b5cf6]">
                                        <h4 className="text-[#8b5cf6] font-semibold mb-2">Impulsion Spécifique (Isp)</h4>
                                        <code className="text-white text-lg">Isp = F / (ṁ × g₀) = Vₑq / g₀</code>
                                        <p className="mt-2 text-sm text-[#71717a]">
                                            L'Isp mesure l'efficacité du moteur. Plus elle est élevée, moins on consomme.
                                        </p>
                                    </div>

                                    <div className="bg-[#1a1a25] rounded-lg p-4 border-l-4 border-[#10b981]">
                                        <h4 className="text-[#10b981] font-semibold mb-2">Équation de Tsiolkovsky</h4>
                                        <code className="text-white text-lg">Δv = Isp × g₀ × ln(m₀/mf)</code>
                                        <p className="mt-2 text-sm text-[#71717a]">
                                            Pour orbite: Δv ≈ 9.4 km/s. Le logarithme écrase le ratio de masse,
                                            d'où l'importance d'une Isp élevée.
                                        </p>
                                    </div>
                                </div>
                            )}

                            {activeSection === "laval" && (
                                <div className="space-y-6">
                                    <h2 className="text-2xl font-bold text-white">🔧 La Tuyère de Laval</h2>
                                    <p className="text-[#a1a1aa]">
                                        Pour transformer l'énergie chimique en vitesse, on utilise une tuyère convergente-divergente.
                                    </p>

                                    <div className="grid grid-cols-3 gap-4">
                                        <div className="bg-[#1a1a25] rounded-lg p-4 text-center">
                                            <div className="text-3xl mb-2">↘️</div>
                                            <h4 className="font-semibold text-white">Convergent</h4>
                                            <p className="text-sm text-[#71717a]">M &lt; 1 (Subsonique)</p>
                                            <p className="text-xs text-[#a1a1aa]">Accélération par rétrécissement</p>
                                        </div>
                                        <div className="bg-gradient-to-br from-[#ef4444]/20 to-transparent rounded-lg p-4 text-center border border-[#ef4444]/30">
                                            <div className="text-3xl mb-2">⚡</div>
                                            <h4 className="font-semibold text-[#ef4444]">COL</h4>
                                            <p className="text-sm text-white">M = 1 (Sonique)</p>
                                            <p className="text-xs text-[#a1a1aa]">Débit bloqué (choked)</p>
                                        </div>
                                        <div className="bg-[#1a1a25] rounded-lg p-4 text-center">
                                            <div className="text-3xl mb-2">↗️</div>
                                            <h4 className="font-semibold text-white">Divergent</h4>
                                            <p className="text-sm text-[#71717a]">M &gt; 1 (Supersonique)</p>
                                            <p className="text-xs text-[#a1a1aa]">Accélération par expansion</p>
                                        </div>
                                    </div>

                                    <div className="bg-[#1a1a25] rounded-lg p-4">
                                        <h4 className="text-[#f59e0b] font-semibold mb-2">Rapport d'Expansion (ε)</h4>
                                        <code className="text-white text-lg">ε = Aₑ / Aₜ</code>
                                        <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
                                            <div className="text-[#71717a]">Grand ε → Optimal pour le vide</div>
                                            <div className="text-[#71717a]">Petit ε → Optimal niveau mer</div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeSection === "thermal" && (
                                <div className="space-y-6">
                                    <h2 className="text-2xl font-bold text-white">🔥 Le Problème Thermique</h2>

                                    <div className="bg-gradient-to-r from-[#ef4444]/20 to-transparent border border-[#ef4444]/30 rounded-lg p-4">
                                        <h4 className="text-[#ef4444] font-bold mb-2">⚠️ PROBLÈME CRITIQUE</h4>
                                        <p className="text-[#a1a1aa]">
                                            Température de combustion: <span className="text-white font-bold">3500+ K</span><br />
                                            Point de fusion du cuivre: <span className="text-white font-bold">1358 K</span>
                                        </p>
                                        <p className="text-sm text-[#71717a] mt-2">
                                            La paroi fondrait en moins d'une seconde sans refroidissement actif !
                                        </p>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="bg-[#1a1a25] rounded-lg p-4">
                                            <h4 className="font-semibold text-white mb-2">Températures Typiques</h4>
                                            <div className="space-y-2 text-sm">
                                                <div className="flex justify-between"><span className="text-[#71717a]">LOX/RP-1</span><span className="text-[#ef4444]">~3600 K</span></div>
                                                <div className="flex justify-between"><span className="text-[#71717a]">LOX/LH2</span><span className="text-[#f59e0b]">~3300 K</span></div>
                                                <div className="flex justify-between"><span className="text-[#71717a]">LOX/CH4</span><span className="text-[#ef4444]">~3550 K</span></div>
                                            </div>
                                        </div>
                                        <div className="bg-[#1a1a25] rounded-lg p-4">
                                            <h4 className="font-semibold text-white mb-2">Points de Fusion</h4>
                                            <div className="space-y-2 text-sm">
                                                <div className="flex justify-between"><span className="text-[#71717a]">Cuivre</span><span className="text-white">1358 K</span></div>
                                                <div className="flex justify-between"><span className="text-[#71717a]">Inconel</span><span className="text-white">1609 K</span></div>
                                                <div className="flex justify-between"><span className="text-[#71717a]">Tungstène</span><span className="text-white">3695 K</span></div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="bg-[#1a1a25] rounded-lg p-4 border-l-4 border-[#f59e0b]">
                                        <h4 className="text-[#f59e0b] font-semibold mb-2">Flux Thermique</h4>
                                        <code className="text-white text-lg">q = hg × (Taw - Twg)</code>
                                        <p className="mt-2 text-sm text-[#71717a]">
                                            Le flux au col peut dépasser <span className="text-white font-bold">50 MW/m²</span> !
                                        </p>
                                    </div>
                                </div>
                            )}

                            {activeSection === "regen" && (
                                <div className="space-y-6">
                                    <h2 className="text-2xl font-bold text-white">❄️ Refroidissement Régénératif</h2>

                                    <div className="bg-gradient-to-r from-[#00d4ff]/20 to-transparent border border-[#00d4ff]/30 rounded-lg p-4">
                                        <p className="text-[#a1a1aa]">
                                            Le propergol circule dans des canaux autour de la chambre <strong className="text-white">AVANT</strong> d'être injecté.
                                            Il absorbe la chaleur puis est brûlé - l'énergie n'est pas perdue !
                                        </p>
                                    </div>

                                    <div className="grid grid-cols-3 gap-4">
                                        <div className="bg-[#1a1a25] rounded-lg p-4 text-center">
                                            <div className="text-3xl mb-2">1️⃣</div>
                                            <p className="text-sm text-[#a1a1aa]">Le carburant froid entre dans les canaux</p>
                                        </div>
                                        <div className="bg-[#1a1a25] rounded-lg p-4 text-center">
                                            <div className="text-3xl mb-2">2️⃣</div>
                                            <p className="text-sm text-[#a1a1aa]">Il absorbe la chaleur de la paroi</p>
                                        </div>
                                        <div className="bg-[#1a1a25] rounded-lg p-4 text-center">
                                            <div className="text-3xl mb-2">3️⃣</div>
                                            <p className="text-sm text-[#a1a1aa]">Il est injecté chaud dans la chambre</p>
                                        </div>
                                    </div>

                                    <div className="bg-gradient-to-r from-[#ef4444]/20 to-transparent border border-[#ef4444]/30 rounded-lg p-4">
                                        <h4 className="text-[#ef4444] font-semibold mb-2">⚠️ Limites</h4>
                                        <ul className="text-sm text-[#a1a1aa] space-y-1">
                                            <li><strong>Ébullition:</strong> Si le liquide bout → film de vapeur isolant → fusion</li>
                                            <li><strong>Cokéfaction:</strong> Kérosène trop chaud → dépôts de suie → bouchage</li>
                                        </ul>
                                    </div>
                                </div>
                            )}

                            {activeSection === "cea" && (
                                <div className="space-y-6">
                                    <h2 className="text-2xl font-bold text-white">⚗️ NASA CEA - Chimie de Combustion</h2>

                                    <p className="text-[#a1a1aa]">
                                        Le code NASA CEA calcule les propriétés thermodynamiques des produits de combustion
                                        en équilibre chimique.
                                    </p>

                                    <div className="bg-[#1a1a25] rounded-lg p-4 border-l-4 border-[#8b5cf6]">
                                        <h4 className="text-[#8b5cf6] font-semibold mb-2">Ratio de Mélange O/F</h4>
                                        <code className="text-white text-lg">O/F = ṁ_ox / ṁ_fuel</code>
                                        <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
                                            <div>
                                                <span className="text-[#f59e0b]">Stœchiométrique:</span>
                                                <span className="text-[#71717a] ml-2">T maximale</span>
                                            </div>
                                            <div>
                                                <span className="text-[#10b981]">Optimal (Isp max):</span>
                                                <span className="text-[#71717a] ml-2">Légèrement riche</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="bg-[#1a1a25] rounded-lg p-4 border-l-4 border-[#00d4ff]">
                                        <h4 className="text-[#00d4ff] font-semibold mb-2">Vitesse Caractéristique c*</h4>
                                        <code className="text-white text-lg">c* = Pc × At / ṁ</code>
                                        <p className="mt-2 text-sm text-[#71717a]">
                                            Mesure l'efficacité de la chambre, indépendamment de la tuyère.
                                        </p>
                                    </div>
                                </div>
                            )}

                            {activeSection === "bartz" && (
                                <div className="space-y-6">
                                    <h2 className="text-2xl font-bold text-white">📐 L'Équation de Bartz</h2>

                                    <p className="text-[#a1a1aa]">
                                        Corrélation semi-empirique pour le coefficient de convection côté gaz.
                                    </p>

                                    <div className="bg-[#1a1a25] rounded-lg p-4 font-mono text-sm overflow-x-auto">
                                        <code className="text-[#00d4ff]">
                                            hg = (0.026/Dt⁰·²) × (μ⁰·² × Cp / Pr⁰·⁶) × (Pc/c*)⁰·⁸ × (At/A)⁰·⁹ × σ
                                        </code>
                                    </div>

                                    <div className="grid grid-cols-3 gap-4">
                                        <div className="bg-[#1a1a25] rounded-lg p-4">
                                            <h4 className="text-[#ef4444] font-semibold text-sm">Effet d'Échelle</h4>
                                            <p className="text-xs text-[#71717a] mt-1">
                                                Dt⁻⁰·² → Petits moteurs plus difficiles à refroidir !
                                            </p>
                                        </div>
                                        <div className="bg-[#1a1a25] rounded-lg p-4">
                                            <h4 className="text-[#f59e0b] font-semibold text-sm">Effet de Pression</h4>
                                            <p className="text-xs text-[#71717a] mt-1">
                                                Pc⁰·⁸ → Doubler Pc = +74% de flux
                                            </p>
                                        </div>
                                        <div className="bg-[#1a1a25] rounded-lg p-4">
                                            <h4 className="text-[#8b5cf6] font-semibold text-sm">Localisation</h4>
                                            <p className="text-xs text-[#71717a] mt-1">
                                                (At/A)⁰·⁹ → Maximum au col
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeSection === "channels" && (
                                <div className="space-y-6">
                                    <h2 className="text-2xl font-bold text-white">🌊 Dimensionnement des Canaux</h2>

                                    <div className="bg-[#1a1a25] rounded-lg p-4 border-l-4 border-[#00d4ff]">
                                        <h4 className="text-[#00d4ff] font-semibold mb-2">Circuit Thermique</h4>
                                        <code className="text-white">q = hg(Taw - Twh) = (k/e)(Twh - Twc) = hc(Twc - Tcool)</code>
                                        <p className="mt-2 text-xs text-[#71717a]">
                                            Flux convectif gaz = Flux conductif = Flux convectif coolant
                                        </p>
                                    </div>

                                    <div className="bg-[#1a1a25] rounded-lg p-4 border-l-4 border-[#10b981]">
                                        <h4 className="text-[#10b981] font-semibold mb-2">Corrélation de Gnielinski</h4>
                                        <code className="text-white text-sm">Nu = [(f/8)(Re-1000)Pr] / [1 + 12.7√(f/8)(Pr²/³-1)]</code>
                                        <p className="mt-2 text-xs text-[#71717a]">
                                            Plus précise que Dittus-Boelter pour Re &lt; 10⁴
                                        </p>
                                    </div>

                                    <div className="bg-gradient-to-r from-[#8b5cf6]/20 to-transparent border border-[#8b5cf6]/30 rounded-lg p-4">
                                        <h4 className="text-[#8b5cf6] font-semibold mb-2">💡 Secret de conception</h4>
                                        <p className="text-sm text-[#a1a1aa]">
                                            Pour augmenter hc: augmenter la vitesse (Re↑) ou réduire Dh.<br />
                                            → Beaucoup de petits canaux &gt; peu de gros canaux
                                        </p>
                                    </div>
                                </div>
                            )}

                            {activeSection === "fluids" && (
                                <div className="space-y-6">
                                    <h2 className="text-2xl font-bold text-white">💨 Mécanique des Fluides</h2>

                                    <div className="bg-[#1a1a25] rounded-lg p-4 border-l-4 border-[#f59e0b]">
                                        <h4 className="text-[#f59e0b] font-semibold mb-2">Équation de Darcy-Weisbach</h4>
                                        <code className="text-white text-lg">ΔP = f × (L/Dh) × (ρv²/2)</code>
                                        <p className="mt-2 text-xs text-[#71717a]">
                                            Perte de pression proportionnelle au carré de la vitesse
                                        </p>
                                    </div>

                                    <div className="bg-gradient-to-r from-[#ef4444]/20 to-transparent border border-[#ef4444]/30 rounded-lg p-4">
                                        <h4 className="text-white font-semibold mb-2">⚖️ Le Compromis de Design</h4>
                                        <div className="grid grid-cols-2 gap-4 text-sm">
                                            <div>
                                                <span className="text-[#10b981]">Vitesse élevée:</span>
                                                <ul className="text-[#71717a] text-xs mt-1">
                                                    <li>✅ Bon refroidissement (hc↑)</li>
                                                    <li>❌ Perte de charge énorme (ΔP↑↑)</li>
                                                </ul>
                                            </div>
                                            <div>
                                                <span className="text-[#f59e0b]">Vitesse faible:</span>
                                                <ul className="text-[#71717a] text-xs mt-1">
                                                    <li>✅ Faible perte de charge</li>
                                                    <li>❌ Risque de fusion !</li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeSection === "materials" && (
                                <div className="space-y-6">
                                    <h2 className="text-2xl font-bold text-white">🧱 Science des Matériaux</h2>

                                    <div className="grid grid-cols-3 gap-4 mb-6">
                                        <div className="bg-[#1a1a25] rounded-lg p-4 text-center">
                                            <div className="text-2xl mb-2">🔥</div>
                                            <h4 className="font-semibold text-white text-sm">Conductivité k</h4>
                                            <p className="text-xs text-[#71717a]">Évacuer la chaleur</p>
                                        </div>
                                        <div className="bg-[#1a1a25] rounded-lg p-4 text-center">
                                            <div className="text-2xl mb-2">🌡️</div>
                                            <h4 className="font-semibold text-white text-sm">T Fusion</h4>
                                            <p className="text-xs text-[#71717a]">Ne pas fondre</p>
                                        </div>
                                        <div className="bg-[#1a1a25] rounded-lg p-4 text-center">
                                            <div className="text-2xl mb-2">💪</div>
                                            <h4 className="font-semibold text-white text-sm">Résistance σy</h4>
                                            <p className="text-xs text-[#71717a]">Tenir la pression</p>
                                        </div>
                                    </div>

                                    <div className="space-y-4">
                                        <div className="bg-gradient-to-r from-[#f59e0b]/20 to-transparent border border-[#f59e0b]/30 rounded-lg p-4">
                                            <h4 className="text-[#f59e0b] font-semibold mb-2">🟠 Cuivres (Standard)</h4>
                                            <p className="text-sm text-[#a1a1aa]">
                                                <strong>GRCop-42:</strong> Le roi actuel (SpaceX). Excellente tenue au fluage, imprimable 3D.<br />
                                                <strong>GlidCop:</strong> Reste dur près du point de fusion. NASA standard.
                                            </p>
                                        </div>

                                        <div className="bg-gradient-to-r from-[#71717a]/20 to-transparent border border-[#71717a]/30 rounded-lg p-4">
                                            <h4 className="text-white font-semibold mb-2">⚪ Superalliages</h4>
                                            <p className="text-sm text-[#a1a1aa]">
                                                <strong>Inconel 718/625:</strong> Tiennent 1200°C+ mais conductivité faible (10 W/mK).<br />
                                                Pour extensions de tuyère ou si refroidissement insuffisant.
                                            </p>
                                        </div>

                                        <div className="bg-gradient-to-r from-[#8b5cf6]/20 to-transparent border border-[#8b5cf6]/30 rounded-lg p-4">
                                            <h4 className="text-[#8b5cf6] font-semibold mb-2">🟣 Réfractaires</h4>
                                            <p className="text-sm text-[#a1a1aa]">
                                                <strong>Niobium C-103:</strong> Extensions radiatives (2200°C). S'oxyde à l'air.<br />
                                                <strong>Tungstène:</strong> 3400°C mais très lourd et cassant.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
