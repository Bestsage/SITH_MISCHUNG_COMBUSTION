"use client";

import { useSession, signOut } from "next-auth/react";
import { redirect } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";

export default function AccountPage() {
    const { data: session, status } = useSession();
    const [activeTab, setActiveTab] = useState<"profile" | "settings" | "usage">("profile");

    // Redirect if not authenticated
    if (status === "unauthenticated") {
        redirect("/auth/signin");
    }

    if (status === "loading") {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500"></div>
            </div>
        );
    }

    const user = session?.user;

    return (
        <div className="min-h-screen bg-slate-950">
            {/* Header */}
            <header className="border-b border-slate-800/50 bg-slate-900/30 backdrop-blur-xl sticky top-0 z-50">
                <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
                    <Link href="/" className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                            <span className="text-xl">🚀</span>
                        </div>
                        <span className="text-xl font-bold text-white">Rocket Design Studio</span>
                    </Link>
                    <Link
                        href="/"
                        className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
                    >
                        ← Retour au calculateur
                    </Link>
                </div>
            </header>

            <main className="max-w-6xl mx-auto px-4 py-8">
                {/* Profile Card */}
                <div className="bg-gradient-to-br from-slate-900/80 to-slate-800/50 border border-slate-700/50 rounded-2xl overflow-hidden shadow-xl mb-8">
                    {/* Cover Image */}
                    <div className="h-32 bg-gradient-to-r from-cyan-600 via-blue-600 to-purple-600 relative">
                        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20"></div>
                    </div>

                    {/* Profile Info */}
                    <div className="px-8 pb-8 relative">
                        {/* Avatar */}
                        <div className="absolute -top-16 left-8">
                            <div className="w-32 h-32 rounded-2xl border-4 border-slate-900 bg-slate-800 overflow-hidden shadow-xl">
                                {user?.image ? (
                                    <Image
                                        src={user.image}
                                        alt={user.name || "Avatar"}
                                        width={128}
                                        height={128}
                                        className="w-full h-full object-cover"
                                    />
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center text-4xl bg-gradient-to-br from-cyan-500 to-blue-600">
                                        {user?.name?.[0]?.toUpperCase() || "U"}
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="flex justify-end pt-4 gap-3">
                            <button className="px-4 py-2 bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 rounded-lg transition-colors text-sm">
                                Modifier le profil
                            </button>
                            <button
                                onClick={() => signOut({ callbackUrl: "/" })}
                                className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors text-sm"
                            >
                                Déconnexion
                            </button>
                        </div>

                        {/* User Info */}
                        <div className="mt-8">
                            <h1 className="text-3xl font-bold text-white mb-1">
                                {user?.name || "Utilisateur"}
                            </h1>
                            <p className="text-slate-400">{user?.email}</p>
                        </div>

                        {/* Stats */}
                        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
                            <StatCard label="Simulations" value="156" icon="🔥" />
                            <StatCard label="Designs sauvés" value="23" icon="💾" />
                            <StatCard label="Analyses CFD" value="8" icon="🌊" />
                            <StatCard label="Depuis" value="Dec 2024" icon="📅" />
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex gap-2 mb-6 border-b border-slate-800">
                    <TabButton active={activeTab === "profile"} onClick={() => setActiveTab("profile")}>
                        👤 Profil
                    </TabButton>
                    <TabButton active={activeTab === "settings"} onClick={() => setActiveTab("settings")}>
                        ⚙️ Paramètres
                    </TabButton>
                    <TabButton active={activeTab === "usage"} onClick={() => setActiveTab("usage")}>
                        📊 Utilisation
                    </TabButton>
                </div>

                {/* Tab Content */}
                {activeTab === "profile" && (
                    <div className="grid md:grid-cols-2 gap-6">
                        {/* Personal Info */}
                        <div className="bg-slate-900/50 border border-slate-800/50 rounded-xl p-6">
                            <h2 className="text-lg font-semibold text-white mb-4">Informations personnelles</h2>
                            <div className="space-y-4">
                                <InfoField label="Nom complet" value={user?.name || "Non défini"} />
                                <InfoField label="Email" value={user?.email || "Non défini"} />
                                <InfoField label="Fournisseur" value="GitHub" />
                                <InfoField label="Rôle" value="Ingénieur" editable />
                                <InfoField label="Organisation" value="Non définie" editable />
                            </div>
                        </div>

                        {/* Preferences */}
                        <div className="bg-slate-900/50 border border-slate-800/50 rounded-xl p-6">
                            <h2 className="text-lg font-semibold text-white mb-4">Préférences</h2>
                            <div className="space-y-4">
                                <PreferenceToggle
                                    label="Unités métriques"
                                    description="Utiliser les unités SI (mètres, bar, K)"
                                    defaultChecked={true}
                                />
                                <PreferenceToggle
                                    label="Animations 3D"
                                    description="Activer la rotation automatique du modèle 3D"
                                    defaultChecked={true}
                                />
                                <PreferenceToggle
                                    label="Mode sombre"
                                    description="Interface en thème sombre"
                                    defaultChecked={true}
                                />
                                <PreferenceToggle
                                    label="Notifications"
                                    description="Recevoir des alertes par email"
                                    defaultChecked={false}
                                />
                            </div>
                        </div>

                        {/* Recent Activity */}
                        <div className="bg-slate-900/50 border border-slate-800/50 rounded-xl p-6 md:col-span-2">
                            <h2 className="text-lg font-semibold text-white mb-4">Activité récente</h2>
                            <div className="space-y-3">
                                <ActivityItem
                                    action="Simulation CEA"
                                    detail="LOX/RP-1 @ O/F 2.5"
                                    time="il y a 2 heures"
                                />
                                <ActivityItem
                                    action="Design sauvegardé"
                                    detail="Merlin-like 1MN"
                                    time="il y a 5 heures"
                                />
                                <ActivityItem
                                    action="Analyse thermique"
                                    detail="Profil de température chambre"
                                    time="hier"
                                />
                                <ActivityItem
                                    action="Export CFD"
                                    detail="Géométrie OpenFOAM"
                                    time="il y a 3 jours"
                                />
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === "settings" && (
                    <div className="space-y-6">
                        {/* Account Settings */}
                        <div className="bg-slate-900/50 border border-slate-800/50 rounded-xl p-6">
                            <h2 className="text-lg font-semibold text-white mb-4">Paramètres du compte</h2>
                            <div className="space-y-4">
                                <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                                    <div>
                                        <p className="font-medium text-white">Exporter mes données</p>
                                        <p className="text-sm text-slate-400">Télécharger toutes vos données</p>
                                    </div>
                                    <button className="px-4 py-2 bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-400 rounded-lg transition-colors text-sm">
                                        Exporter
                                    </button>
                                </div>
                                <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                                    <div>
                                        <p className="font-medium text-white">Connexions liées</p>
                                        <p className="text-sm text-slate-400">Gérer vos connexions OAuth</p>
                                    </div>
                                    <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
                                        GitHub ✓
                                    </span>
                                </div>
                                <div className="flex items-center justify-between p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                                    <div>
                                        <p className="font-medium text-red-400">Supprimer le compte</p>
                                        <p className="text-sm text-slate-400">Cette action est irréversible</p>
                                    </div>
                                    <button className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors text-sm">
                                        Supprimer
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* API Keys */}
                        <div className="bg-slate-900/50 border border-slate-800/50 rounded-xl p-6">
                            <h2 className="text-lg font-semibold text-white mb-4">Clés API</h2>
                            <p className="text-slate-400 mb-4">
                                Utilisez des clés API pour accéder à l&apos;API programmatiquement.
                            </p>
                            <button className="px-4 py-2 bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-400 rounded-lg transition-colors">
                                + Générer une nouvelle clé
                            </button>
                        </div>
                    </div>
                )}

                {activeTab === "usage" && (
                    <div className="space-y-6">
                        {/* Usage Stats */}
                        <div className="grid md:grid-cols-3 gap-6">
                            <UsageCard
                                title="Simulations CEA"
                                used={156}
                                limit={500}
                                color="cyan"
                            />
                            <UsageCard
                                title="Calculs CFD"
                                used={8}
                                limit={20}
                                color="purple"
                            />
                            <UsageCard
                                title="Stockage"
                                used={45}
                                limit={100}
                                unit="MB"
                                color="orange"
                            />
                        </div>

                        {/* Plan Info */}
                        <div className="bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/30 rounded-xl p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h3 className="text-xl font-bold text-white mb-1">Plan Gratuit</h3>
                                    <p className="text-slate-400">
                                        Accès aux fonctionnalités de base du calculateur de moteur fusée
                                    </p>
                                </div>
                                <button className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-medium rounded-xl transition-all shadow-lg hover:shadow-xl">
                                    Passer à Pro
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

function StatCard({ label, value, icon }: { label: string; value: string; icon: string }) {
    return (
        <div className="bg-slate-800/50 rounded-xl p-4 text-center">
            <span className="text-2xl">{icon}</span>
            <p className="text-2xl font-bold text-white mt-1">{value}</p>
            <p className="text-sm text-slate-400">{label}</p>
        </div>
    );
}

function TabButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
    return (
        <button
            onClick={onClick}
            className={`px-4 py-3 font-medium transition-colors ${
                active
                    ? "text-cyan-400 border-b-2 border-cyan-400"
                    : "text-slate-400 hover:text-slate-300"
            }`}
        >
            {children}
        </button>
    );
}

function InfoField({ label, value, editable }: { label: string; value: string; editable?: boolean }) {
    return (
        <div className="flex items-center justify-between py-2 border-b border-slate-800/50 last:border-0">
            <span className="text-slate-400">{label}</span>
            <div className="flex items-center gap-2">
                <span className="text-white">{value}</span>
                {editable && (
                    <button className="text-cyan-400 hover:text-cyan-300 text-sm">✏️</button>
                )}
            </div>
        </div>
    );
}

function PreferenceToggle({ label, description, defaultChecked }: { label: string; description: string; defaultChecked: boolean }) {
    const [checked, setChecked] = useState(defaultChecked);
    return (
        <div className="flex items-center justify-between py-2">
            <div>
                <p className="font-medium text-white">{label}</p>
                <p className="text-sm text-slate-400">{description}</p>
            </div>
            <button
                onClick={() => setChecked(!checked)}
                className={`w-12 h-6 rounded-full transition-colors ${
                    checked ? "bg-cyan-500" : "bg-slate-700"
                }`}
            >
                <div
                    className={`w-5 h-5 bg-white rounded-full transition-transform shadow-md ${
                        checked ? "translate-x-6" : "translate-x-0.5"
                    }`}
                />
            </button>
        </div>
    );
}

function ActivityItem({ action, detail, time }: { action: string; detail: string; time: string }) {
    return (
        <div className="flex items-center justify-between py-3 border-b border-slate-800/50 last:border-0">
            <div>
                <p className="font-medium text-white">{action}</p>
                <p className="text-sm text-slate-400">{detail}</p>
            </div>
            <span className="text-xs text-slate-500">{time}</span>
        </div>
    );
}

function UsageCard({ title, used, limit, unit = "", color }: { title: string; used: number; limit: number; unit?: string; color: "cyan" | "purple" | "orange" }) {
    const percentage = Math.round((used / limit) * 100);
    const colorClasses = {
        cyan: "from-cyan-500 to-cyan-600",
        purple: "from-purple-500 to-purple-600",
        orange: "from-orange-500 to-orange-600",
    };

    return (
        <div className="bg-slate-900/50 border border-slate-800/50 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
            <div className="flex items-end gap-1 mb-3">
                <span className="text-3xl font-bold text-white">{used}</span>
                <span className="text-slate-400 mb-1">/ {limit} {unit}</span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <div
                    className={`h-full bg-gradient-to-r ${colorClasses[color]} transition-all`}
                    style={{ width: `${percentage}%` }}
                />
            </div>
            <p className="text-sm text-slate-400 mt-2">{percentage}% utilisé</p>
        </div>
    );
}
