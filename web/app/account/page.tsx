"use client";

import { useSession, signOut } from "next-auth/react";
import { redirect } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { useState, useEffect, useCallback, useContext } from "react";
import { ThemeContext } from "@/contexts/ThemeContext";
import { getStats } from "@/lib/activity";

// Safe hook that doesn't throw if outside provider
function useSafeTheme() {
    const context = useContext(ThemeContext);
    return context ?? { theme: "dark", setTheme: () => { } };
}

interface UserStats {
    simulations: number;
    designs: number;
    cfdAnalyses: number;
    memberSince: string;
    lastLogin: string;
    recentActivities: Array<{
        id: string;
        type: string;
        metadata: Record<string, unknown> | null;
        createdAt: string;
    }>;
}

interface AdminUser {
    id: string;
    name: string | null;
    email: string;
    image: string | null;
    role: string;
    createdAt: string;
    lastLoginAt: string | null;
    activityCount: number;
    linkedAccounts: string[];
    projectsCount: number;
    simulationsCount: number;
}

const providerIcons: Record<string, string> = {
    github: "🐙",
    google: "🔵",
    discord: "💜",
    slack: "💚",
    email: "📧"
};

export default function AccountPage() {
    const { data: session, status, update } = useSession();
    const { theme, setTheme } = useSafeTheme();
    const [activeTab, setActiveTab] = useState<"profile" | "settings" | "activity" | "admin">("profile");
    const [exporting, setExporting] = useState(false);
    const [stats, setStats] = useState<UserStats | null>(null);
    const [localStats, setLocalStats] = useState({ simulations: 0, designs: 0, cfdAnalyses: 0 });
    const [loading, setLoading] = useState(true);

    // Profile edit state
    const [editingProfile, setEditingProfile] = useState(false);
    const [editName, setEditName] = useState("");
    const [savingProfile, setSavingProfile] = useState(false);

    // Photo edit state
    const [editingPhoto, setEditingPhoto] = useState(false);
    const [photoOptions, setPhotoOptions] = useState<{ provider: string; previewUrl: string | null }[]>([]);
    const [uploadingPhoto, setUploadingPhoto] = useState(false);

    // Admin state
    const [users, setUsers] = useState<AdminUser[]>([]);
    const [userSearch, setUserSearch] = useState("");
    const [loadingUsers, setLoadingUsers] = useState(false);
    const [totalUsers, setTotalUsers] = useState(0);

    const user = session?.user;
    const isAdmin = user?.role === "ADMIN" || user?.role === "SUPERADMIN";
    const isSuperAdmin = user?.role === "SUPERADMIN";

    // Load local stats and refresh periodically
    useEffect(() => {
        const loadLocalStats = () => {
            const local = getStats();
            setLocalStats(local);
        };

        // Load immediately
        loadLocalStats();

        // Refresh every 2 seconds to catch updates from other pages
        const interval = setInterval(loadLocalStats, 2000);

        // Also listen for storage events (updates from other tabs)
        const handleStorage = (e: StorageEvent) => {
            if (e.key === "rocket_studio_stats") {
                loadLocalStats();
            }
        };
        window.addEventListener("storage", handleStorage);

        return () => {
            clearInterval(interval);
            window.removeEventListener("storage", handleStorage);
        };
    }, []);

    // Fetch user stats from server
    useEffect(() => {
        if (status === "authenticated") {
            fetch("/api/user/stats")
                .then(res => res.json())
                .then(data => {
                    if (!data.error) {
                        setStats(data);
                    }
                })
                .catch(console.error)
                .finally(() => setLoading(false));
        } else if (status === "unauthenticated") {
            setLoading(false);
        }
    }, [status]);

    // Combine server stats with local stats (use max of both)
    const combinedStats = {
        simulations: Math.max(stats?.simulations || 0, localStats.simulations),
        designs: Math.max(stats?.designs || 0, localStats.designs),
        cfdAnalyses: Math.max(stats?.cfdAnalyses || 0, localStats.cfdAnalyses),
    };

    // Fetch users for admin
    const fetchUsers = useCallback(async (search = "") => {
        if (!isAdmin) return;
        setLoadingUsers(true);
        try {
            const res = await fetch(`/api/admin/users?search=${encodeURIComponent(search)}`);
            const data = await res.json();
            if (!data.error) {
                setUsers(data.users);
                setTotalUsers(data.total);
            }
        } catch (e) {
            console.error(e);
        } finally {
            setLoadingUsers(false);
        }
    }, [isAdmin]);

    useEffect(() => {
        if (activeTab === "admin" && isAdmin) {
            fetchUsers(userSearch);
        }
    }, [activeTab, isAdmin, userSearch, fetchUsers]);

    // Redirect if not authenticated
    if (status === "unauthenticated") {
        redirect("/auth/signin");
    }

    if (status === "loading") {
        return (
            <div className="min-h-screen bg-slate-950 dark:bg-slate-950 light:bg-slate-100 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500"></div>
            </div>
        );
    }

    const handleSaveProfile = async () => {
        setSavingProfile(true);
        try {
            const res = await fetch("/api/user/profile", {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: editName })
            });
            if (res.ok) {
                await update({ name: editName });
                setEditingProfile(false);
            }
        } catch (e) {
            console.error(e);
        } finally {
            setSavingProfile(false);
        }
    };

    const handleRoleChange = async (userId: string, newRole: string) => {
        try {
            const res = await fetch("/api/admin/users", {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ userId, role: newRole })
            });
            if (res.ok) {
                fetchUsers(userSearch);
            }
        } catch (e) {
            console.error(e);
        }
    };

    const handleExport = () => {
        setExporting(true);
        const userData = {
            user: {
                name: user?.name,
                email: user?.email,
                image: user?.image,
                role: user?.role
            },
            stats: stats || {
                simulations: 0,
                designs: 0,
                cfdAnalyses: 0,
                memberSince: new Date().toISOString()
            },
            exportDate: new Date().toISOString()
        };
        const blob = new Blob([JSON.stringify(userData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `rocket-studio-export-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        setTimeout(() => setExporting(false), 1000);
    };

    const formatDate = (dateStr: string) => {
        return new Date(dateStr).toLocaleDateString("fr-FR", {
            year: "numeric",
            month: "short",
            day: "numeric"
        });
    };

    const formatActivityType = (type: string) => {
        const types: Record<string, string> = {
            simulation: "Simulation CEA",
            cea_calculation: "Calcul CEA",
            design_save: "Design sauvé",
            cfd_analysis: "Analyse CFD",
            account_created: "Création de compte",
            login: "Connexion"
        };
        return types[type] || type;
    };

    const bgClass = theme === "light" ? "bg-slate-100" : "bg-slate-950";
    const cardClass = theme === "light"
        ? "bg-white border-slate-200"
        : "bg-slate-900/50 border-slate-800/50";
    const textClass = theme === "light" ? "text-slate-900" : "text-white";
    const subTextClass = theme === "light" ? "text-slate-600" : "text-slate-400";

    return (
        <div className={`min-h-screen ${bgClass}`}>
            {/* Header */}
            <header className={`border-b ${theme === "light" ? "border-slate-200 bg-white/80" : "border-slate-800/50 bg-slate-900/30"} backdrop-blur-xl sticky top-0 z-50`}>
                <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
                    <Link href="/" className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                            <span className="text-xl">🚀</span>
                        </div>
                        <span className={`text-xl font-bold ${textClass}`}>Rocket Design Studio</span>
                    </Link>
                    <Link
                        href="/"
                        className={`px-4 py-2 ${theme === "light" ? "bg-slate-100 hover:bg-slate-200 text-slate-700" : "bg-slate-800 hover:bg-slate-700 text-slate-300"} rounded-lg transition-colors`}
                    >
                        ← Retour au calculateur
                    </Link>
                </div>
            </header>

            <main className="max-w-6xl mx-auto px-4 py-8">
                {/* Profile Card */}
                <div className={`${cardClass} border rounded-2xl overflow-hidden shadow-xl mb-8`}>
                    {/* Cover Image */}
                    <div className="h-32 bg-gradient-to-r from-cyan-600 via-blue-600 to-purple-600 relative">
                        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20"></div>
                        {/* Role badge */}
                        {user?.role && user.role !== "USER" && (
                            <div className="absolute top-4 right-4 px-3 py-1 bg-black/30 backdrop-blur-sm rounded-full text-sm text-white font-medium">
                                {user.role === "SUPERADMIN" ? "👑 Super Admin" : "⚡ Admin"}
                            </div>
                        )}
                    </div>

                    {/* Profile Info */}
                    <div className="px-8 pb-8 relative">
                        {/* Avatar */}
                        <div className="absolute -top-16 left-8 group">
                            <div className={`w-32 h-32 rounded-2xl border-4 ${theme === "light" ? "border-white bg-slate-100" : "border-slate-900 bg-slate-800"} overflow-hidden shadow-xl relative cursor-pointer`}
                                onClick={async () => {
                                    setEditingPhoto(true);
                                    try {
                                        const res = await fetch("/api/user/image");
                                        const data = await res.json();
                                        if (data.syncOptions) setPhotoOptions(data.syncOptions);
                                    } catch (e) { console.error(e); }
                                }}
                            >
                                {user?.image ? (
                                    <Image
                                        src={user.image}
                                        alt={user.name || "Avatar"}
                                        width={128}
                                        height={128}
                                        className="w-full h-full object-cover"
                                    />
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center text-4xl bg-gradient-to-br from-cyan-500 to-blue-600 text-white">
                                        {user?.name?.[0]?.toUpperCase() || "U"}
                                    </div>
                                )}
                                {/* Hover overlay */}
                                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                    <span className="text-white text-2xl">📷</span>
                                </div>
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="flex justify-end pt-4 gap-3">
                            <button
                                onClick={() => {
                                    setEditName(user?.name || "");
                                    setEditingProfile(true);
                                }}
                                className={`px-4 py-2 ${theme === "light" ? "bg-slate-100 hover:bg-slate-200 text-slate-700" : "bg-slate-700/50 hover:bg-slate-600/50 text-slate-300"} rounded-lg transition-colors text-sm`}
                            >
                                ✏️ Modifier le profil
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
                            <h1 className={`text-3xl font-bold ${textClass} mb-1`}>
                                {user?.name || "Utilisateur"}
                            </h1>
                            <p className={subTextClass}>{user?.email}</p>
                        </div>

                        {/* Stats - Style GitHub */}
                        <div className="mt-6 flex flex-wrap gap-4 text-sm">
                            <div className={`flex items-center gap-2 ${subTextClass}`}>
                                <span>🔥</span>
                                <span className={`font-semibold ${textClass}`}>{combinedStats.simulations}</span> simulations
                            </div>
                            <div className={`flex items-center gap-2 ${subTextClass}`}>
                                <span>💾</span>
                                <span className={`font-semibold ${textClass}`}>{combinedStats.designs}</span> designs sauvés
                            </div>
                            <div className={`flex items-center gap-2 ${subTextClass}`}>
                                <span>🌊</span>
                                <span className={`font-semibold ${textClass}`}>{combinedStats.cfdAnalyses}</span> analyses CFD
                            </div>
                            <div className={`flex items-center gap-2 ${subTextClass}`}>
                                <span>📅</span>
                                Membre depuis <span className={`font-semibold ${textClass}`}>
                                    {loading ? "..." : stats?.memberSince ? formatDate(stats.memberSince) : "Récemment"}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <div className={`flex gap-2 mb-6 border-b ${theme === "light" ? "border-slate-200" : "border-slate-800"}`}>
                    <TabButton theme={theme} active={activeTab === "profile"} onClick={() => setActiveTab("profile")}>
                        👤 Profil
                    </TabButton>
                    <TabButton theme={theme} active={activeTab === "settings"} onClick={() => setActiveTab("settings")}>
                        ⚙️ Paramètres
                    </TabButton>
                    <TabButton theme={theme} active={activeTab === "activity"} onClick={() => setActiveTab("activity")}>
                        📋 Activité
                    </TabButton>
                    {isAdmin && (
                        <TabButton theme={theme} active={activeTab === "admin"} onClick={() => setActiveTab("admin")}>
                            👥 Utilisateurs
                        </TabButton>
                    )}
                </div>

                {/* Tab Content */}
                {activeTab === "profile" && (
                    <div className="grid md:grid-cols-2 gap-6">
                        {/* Personal Info */}
                        <div className={`${cardClass} border rounded-xl p-6`}>
                            <h2 className={`text-lg font-semibold ${textClass} mb-4`}>Informations personnelles</h2>
                            <div className="space-y-4">
                                <InfoField theme={theme} label="Nom complet" value={user?.name || "Non défini"} />
                                <InfoField theme={theme} label="Email" value={user?.email || "Non défini"} />
                                <InfoField theme={theme} label="Rôle" value={user?.role || "USER"} />
                                <InfoField theme={theme} label="Méthode auth" value="Email / Password" />
                            </div>
                        </div>

                        {/* Preferences */}
                        <div className={`${cardClass} border rounded-xl p-6`}>
                            <h2 className={`text-lg font-semibold ${textClass} mb-4`}>Préférences</h2>
                            <div className="space-y-4">
                                <PreferenceToggle
                                    theme={theme}
                                    label="Unités métriques"
                                    description="Utiliser les unités SI (mètres, bar, K)"
                                    checked={true}
                                    onChange={() => { }}
                                />
                                <PreferenceToggle
                                    theme={theme}
                                    label="Animations 3D"
                                    description="Activer la rotation automatique du modèle 3D"
                                    checked={true}
                                    onChange={() => { }}
                                />
                                <PreferenceToggle
                                    theme={theme}
                                    label="Mode sombre"
                                    description="Interface en thème sombre"
                                    checked={theme === "dark"}
                                    onChange={() => setTheme(theme === "dark" ? "light" : "dark")}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === "settings" && (
                    <div className="space-y-6">
                        <div className={`${cardClass} border rounded-xl p-6`}>
                            <h2 className={`text-lg font-semibold ${textClass} mb-4`}>Paramètres du compte</h2>
                            <div className="space-y-4">
                                <div className={`flex items-center justify-between p-4 ${theme === "light" ? "bg-slate-50" : "bg-slate-800/50"} rounded-lg`}>
                                    <div>
                                        <p className={`font-medium ${textClass}`}>Exporter mes données</p>
                                        <p className={`text-sm ${subTextClass}`}>Télécharger toutes vos données en JSON</p>
                                    </div>
                                    <button
                                        onClick={handleExport}
                                        disabled={exporting}
                                        className="px-4 py-2 bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-400 rounded-lg transition-colors text-sm disabled:opacity-50"
                                    >
                                        {exporting ? "⏳ Export..." : "📥 Exporter"}
                                    </button>
                                </div>
                                <div className={`flex items-center justify-between p-4 ${theme === "light" ? "bg-slate-50" : "bg-slate-800/50"} rounded-lg`}>
                                    <div>
                                        <p className={`font-medium ${textClass}`}>Thème de l&apos;interface</p>
                                        <p className={`text-sm ${subTextClass}`}>Basculer entre mode clair et sombre</p>
                                    </div>
                                    <button
                                        onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                                        className={`px-4 py-2 ${theme === "light" ? "bg-slate-900 text-white" : "bg-white text-slate-900"} rounded-lg transition-colors text-sm`}
                                    >
                                        {theme === "dark" ? "☀️ Mode clair" : "🌙 Mode sombre"}
                                    </button>
                                </div>
                                <div className="flex items-center justify-between p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                                    <div>
                                        <p className="font-medium text-red-400">Supprimer le compte</p>
                                        <p className={`text-sm ${subTextClass}`}>Cette action est irréversible</p>
                                    </div>
                                    <button
                                        onClick={() => {
                                            if (confirm("Êtes-vous sûr de vouloir supprimer votre compte ?")) {
                                                alert("Fonctionnalité en développement");
                                            }
                                        }}
                                        className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors text-sm"
                                    >
                                        Supprimer
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === "activity" && (
                    <div className={`${cardClass} border rounded-xl p-6`}>
                        <h2 className={`text-lg font-semibold ${textClass} mb-4`}>Historique d&apos;activité</h2>
                        {loading ? (
                            <div className="text-center py-8">
                                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-cyan-500 mx-auto"></div>
                            </div>
                        ) : stats?.recentActivities && stats.recentActivities.length > 0 ? (
                            <div className="space-y-1">
                                {stats.recentActivities.map((activity) => (
                                    <ActivityItem
                                        key={activity.id}
                                        theme={theme}
                                        action={formatActivityType(activity.type)}
                                        detail={activity.metadata?.detail as string || ""}
                                        time={formatDate(activity.createdAt)}
                                    />
                                ))}
                            </div>
                        ) : (
                            <p className={`text-center py-8 ${subTextClass}`}>
                                Aucune activité enregistrée
                            </p>
                        )}
                    </div>
                )}

                {activeTab === "admin" && isAdmin && (
                    <div className={`${cardClass} border rounded-xl p-6`}>
                        <div className="flex items-center justify-between mb-6">
                            <h2 className={`text-lg font-semibold ${textClass}`}>
                                Gestion des utilisateurs ({totalUsers})
                            </h2>
                            <input
                                type="text"
                                placeholder="Rechercher..."
                                value={userSearch}
                                onChange={(e) => setUserSearch(e.target.value)}
                                className={`px-4 py-2 ${theme === "light" ? "bg-slate-100 border-slate-200" : "bg-slate-800/50 border-slate-700"} border rounded-lg ${textClass} placeholder-slate-500 focus:outline-none focus:border-cyan-500`}
                            />
                        </div>

                        {loadingUsers ? (
                            <div className="text-center py-8">
                                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-cyan-500 mx-auto"></div>
                            </div>
                        ) : (
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead>
                                        <tr className={`text-left border-b ${theme === "light" ? "border-slate-200" : "border-slate-700"}`}>
                                            <th className={`pb-3 ${subTextClass} font-medium`}>Utilisateur</th>
                                            <th className={`pb-3 ${subTextClass} font-medium`}>Connexion</th>
                                            <th className={`pb-3 ${subTextClass} font-medium`}>Rôle</th>
                                            <th className={`pb-3 ${subTextClass} font-medium`}>Stats</th>
                                            <th className={`pb-3 ${subTextClass} font-medium`}>Dernière connexion</th>
                                            {isSuperAdmin && <th className={`pb-3 ${subTextClass} font-medium`}>Actions</th>}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {users.map((u) => (
                                            <tr key={u.id} className={`border-b ${theme === "light" ? "border-slate-100" : "border-slate-800"} hover:${theme === "light" ? "bg-slate-50" : "bg-slate-800/30"}`}>
                                                <td className="py-4">
                                                    <div className="flex items-center gap-3">
                                                        {u.image ? (
                                                            <Image src={u.image} alt={u.name || ""} width={40} height={40} className="w-10 h-10 rounded-full object-cover" />
                                                        ) : (
                                                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white font-medium">
                                                                {u.name?.[0]?.toUpperCase() || u.email[0].toUpperCase()}
                                                            </div>
                                                        )}
                                                        <div>
                                                            <p className={`font-medium ${textClass}`}>{u.name || "Sans nom"}</p>
                                                            <p className={`text-sm ${subTextClass}`}>{u.email}</p>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="py-4">
                                                    <div className="flex items-center gap-1">
                                                        {u.linkedAccounts.length > 0 ? (
                                                            u.linkedAccounts.map((provider, idx) => (
                                                                <span key={idx} title={provider} className="text-lg">
                                                                    {providerIcons[provider] || "🔗"}
                                                                </span>
                                                            ))
                                                        ) : (
                                                            <span className="text-lg" title="Email">{providerIcons.email}</span>
                                                        )}
                                                    </div>
                                                </td>
                                                <td className="py-4">
                                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${u.role === "SUPERADMIN"
                                                        ? "bg-purple-500/20 text-purple-400"
                                                        : u.role === "ADMIN"
                                                            ? "bg-cyan-500/20 text-cyan-400"
                                                            : theme === "light" ? "bg-slate-200 text-slate-700" : "bg-slate-700 text-slate-300"
                                                        }`}>
                                                        {u.role}
                                                    </span>
                                                </td>
                                                <td className="py-4">
                                                    <div className={`text-sm ${subTextClass}`}>
                                                        <div>🔥 {u.activityCount} actions</div>
                                                        <div>📁 {u.projectsCount} projets</div>
                                                        <div>🌊 {u.simulationsCount} CFD</div>
                                                    </div>
                                                </td>
                                                <td className={`py-4 ${subTextClass}`}>
                                                    {u.lastLoginAt ? formatDate(u.lastLoginAt) : "Jamais"}
                                                </td>
                                                {isSuperAdmin && (
                                                    <td className="py-4">
                                                        {u.email !== user?.email && (
                                                            <select
                                                                value={u.role}
                                                                onChange={(e) => handleRoleChange(u.id, e.target.value)}
                                                                className={`px-2 py-1 ${theme === "light" ? "bg-slate-100" : "bg-slate-800"} border-0 rounded text-sm ${textClass}`}
                                                            >
                                                                <option value="USER">USER</option>
                                                                <option value="ADMIN">ADMIN</option>
                                                                <option value="SUPERADMIN">SUPERADMIN</option>
                                                            </select>
                                                        )}
                                                    </td>
                                                )}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                )}
            </main>

            {/* Edit Profile Modal */}
            {editingProfile && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className={`${cardClass} border rounded-2xl p-6 w-full max-w-md`}>
                        <h2 className={`text-xl font-semibold ${textClass} mb-4`}>Modifier le profil</h2>
                        <div className="space-y-4">
                            <div>
                                <label className={`block text-sm font-medium ${subTextClass} mb-2`}>
                                    Nom complet
                                </label>
                                <input
                                    type="text"
                                    value={editName}
                                    onChange={(e) => setEditName(e.target.value)}
                                    className={`w-full px-4 py-3 ${theme === "light" ? "bg-slate-100 border-slate-200" : "bg-slate-800/50 border-slate-700"} border rounded-xl ${textClass} focus:outline-none focus:border-cyan-500`}
                                />
                            </div>
                            <div className="flex gap-3 pt-4">
                                <button
                                    onClick={() => setEditingProfile(false)}
                                    className={`flex-1 px-4 py-3 ${theme === "light" ? "bg-slate-100 text-slate-700" : "bg-slate-700 text-slate-300"} rounded-xl transition-colors`}
                                >
                                    Annuler
                                </button>
                                <button
                                    onClick={handleSaveProfile}
                                    disabled={savingProfile}
                                    className="flex-1 px-4 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-xl transition-colors disabled:opacity-50"
                                >
                                    {savingProfile ? "Sauvegarde..." : "Sauvegarder"}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Edit Photo Modal */}
            {editingPhoto && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className={`${cardClass} border rounded-2xl p-6 w-full max-w-md`}>
                        <h2 className={`text-xl font-semibold ${textClass} mb-4`}>📷 Modifier la photo de profil</h2>

                        {/* Current photo */}
                        <div className="flex justify-center mb-6">
                            <div className="w-24 h-24 rounded-full overflow-hidden bg-slate-800">
                                {user?.image ? (
                                    <Image src={user.image} alt="Current" width={96} height={96} className="w-full h-full object-cover" />
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center text-3xl bg-gradient-to-br from-cyan-500 to-blue-600 text-white">
                                        {user?.name?.[0]?.toUpperCase() || "U"}
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Sync from provider */}
                        {photoOptions.length > 0 && (
                            <div className="mb-4">
                                <p className={`text-sm ${subTextClass} mb-2`}>Synchroniser depuis :</p>
                                <div className="flex gap-2">
                                    {photoOptions.map((opt) => (
                                        <button
                                            key={opt.provider}
                                            onClick={async () => {
                                                setUploadingPhoto(true);
                                                try {
                                                    const res = await fetch("/api/user/image", {
                                                        method: "POST",
                                                        headers: { "Content-Type": "application/json" },
                                                        body: JSON.stringify({ action: "sync", provider: opt.provider })
                                                    });
                                                    if (res.ok) {
                                                        await update();
                                                        setEditingPhoto(false);
                                                    } else {
                                                        const err = await res.json();
                                                        alert(err.error || "Erreur lors de la synchronisation");
                                                    }
                                                } catch (e) { console.error(e); }
                                                setUploadingPhoto(false);
                                            }}
                                            disabled={uploadingPhoto}
                                            title={opt.previewUrl ? `Sync depuis ${opt.provider}` : `Reconnectez-vous via ${opt.provider} pour capturer l'image`}
                                            className={`flex-1 p-3 ${theme === "light" ? "bg-slate-100 hover:bg-slate-200" : "bg-slate-800 hover:bg-slate-700"} rounded-xl transition-colors flex flex-col items-center gap-2 disabled:opacity-50`}
                                        >
                                            {opt.previewUrl ? (
                                                <Image
                                                    src={opt.previewUrl}
                                                    alt={opt.provider}
                                                    width={48}
                                                    height={48}
                                                    className="w-12 h-12 rounded-full object-cover"
                                                />
                                            ) : (
                                                <span className="text-3xl">{providerIcons[opt.provider] || "🔗"}</span>
                                            )}
                                            <span className={`text-xs ${subTextClass} capitalize`}>{opt.provider}</span>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Upload custom */}
                        <div className="mb-4">
                            <p className={`text-sm ${subTextClass} mb-2`}>Ou télécharger une image :</p>
                            <label className={`block w-full p-4 ${theme === "light" ? "bg-slate-100 hover:bg-slate-200" : "bg-slate-800 hover:bg-slate-700"} rounded-xl transition-colors cursor-pointer text-center`}>
                                <input
                                    type="file"
                                    accept="image/*"
                                    className="hidden"
                                    onChange={async (e) => {
                                        const file = e.target.files?.[0];
                                        if (!file) return;

                                        setUploadingPhoto(true);
                                        const reader = new FileReader();
                                        reader.onload = async () => {
                                            try {
                                                const res = await fetch("/api/user/image", {
                                                    method: "POST",
                                                    headers: { "Content-Type": "application/json" },
                                                    body: JSON.stringify({ action: "upload", imageUrl: reader.result })
                                                });
                                                if (res.ok) {
                                                    await update();
                                                    setEditingPhoto(false);
                                                }
                                            } catch (err) { console.error(err); }
                                            setUploadingPhoto(false);
                                        };
                                        reader.readAsDataURL(file);
                                    }}
                                />
                                <span className={`${textClass}`}>📁 Choisir un fichier</span>
                            </label>
                        </div>

                        {/* Remove photo */}
                        {user?.image && (
                            <button
                                onClick={async () => {
                                    setUploadingPhoto(true);
                                    try {
                                        const res = await fetch("/api/user/image", {
                                            method: "POST",
                                            headers: { "Content-Type": "application/json" },
                                            body: JSON.stringify({ action: "remove" })
                                        });
                                        if (res.ok) {
                                            await update();
                                            setEditingPhoto(false);
                                        }
                                    } catch (e) { console.error(e); }
                                    setUploadingPhoto(false);
                                }}
                                disabled={uploadingPhoto}
                                className="w-full p-3 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-xl transition-colors text-sm mb-4 disabled:opacity-50"
                            >
                                🗑️ Supprimer la photo
                            </button>
                        )}

                        {/* Close */}
                        <button
                            onClick={() => setEditingPhoto(false)}
                            className={`w-full p-3 ${theme === "light" ? "bg-slate-200 text-slate-700" : "bg-slate-700 text-slate-300"} rounded-xl transition-colors`}
                        >
                            Fermer
                        </button>

                        {uploadingPhoto && (
                            <div className="absolute inset-0 bg-black/50 rounded-2xl flex items-center justify-center">
                                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-cyan-500"></div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

function TabButton({ theme, active, onClick, children }: { theme: string; active: boolean; onClick: () => void; children: React.ReactNode }) {
    const activeClass = "text-cyan-400 border-b-2 border-cyan-400";
    const inactiveClass = theme === "light"
        ? "text-slate-600 hover:text-slate-900"
        : "text-slate-400 hover:text-slate-300";

    return (
        <button
            onClick={onClick}
            className={`px-4 py-3 font-medium transition-colors ${active ? activeClass : inactiveClass}`}
        >
            {children}
        </button>
    );
}

function InfoField({ theme, label, value }: { theme: string; label: string; value: string }) {
    const textClass = theme === "light" ? "text-slate-900" : "text-white";
    const subTextClass = theme === "light" ? "text-slate-600" : "text-slate-400";
    const borderClass = theme === "light" ? "border-slate-200" : "border-slate-800/50";

    return (
        <div className={`flex items-center justify-between py-2 border-b ${borderClass} last:border-0`}>
            <span className={subTextClass}>{label}</span>
            <span className={textClass}>{value}</span>
        </div>
    );
}

function PreferenceToggle({ theme, label, description, checked, onChange }: {
    theme: string;
    label: string;
    description: string;
    checked: boolean;
    onChange: () => void;
}) {
    const textClass = theme === "light" ? "text-slate-900" : "text-white";
    const subTextClass = theme === "light" ? "text-slate-600" : "text-slate-400";

    return (
        <div className="flex items-center justify-between py-2">
            <div>
                <p className={`font-medium ${textClass}`}>{label}</p>
                <p className={`text-sm ${subTextClass}`}>{description}</p>
            </div>
            <button
                onClick={onChange}
                className={`w-12 h-6 rounded-full transition-colors ${checked ? "bg-cyan-500" : theme === "light" ? "bg-slate-300" : "bg-slate-700"
                    }`}
            >
                <div
                    className={`w-5 h-5 bg-white rounded-full transition-transform shadow-md ${checked ? "translate-x-6" : "translate-x-0.5"
                        }`}
                />
            </button>
        </div>
    );
}

function ActivityItem({ theme, action, detail, time }: { theme: string; action: string; detail: string; time: string }) {
    const textClass = theme === "light" ? "text-slate-900" : "text-white";
    const subTextClass = theme === "light" ? "text-slate-600" : "text-slate-400";
    const borderClass = theme === "light" ? "border-slate-200" : "border-slate-800/50";

    return (
        <div className={`flex items-center justify-between py-3 border-b ${borderClass} last:border-0`}>
            <div>
                <p className={`font-medium ${textClass}`}>{action}</p>
                {detail && <p className={`text-sm ${subTextClass}`}>{detail}</p>}
            </div>
            <span className={`text-xs ${theme === "light" ? "text-slate-500" : "text-slate-500"}`}>{time}</span>
        </div>
    );
}
