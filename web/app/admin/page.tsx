import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import Link from "next/link";

// Site statistics placeholders - will be replaced with real data later
async function getSiteStats() {
    // TODO: Connect to actual data sources
    return {
        totalCalculations: 1247,
        activeSessions: 12,
        cfDSimulations: 89,
        materialLibraryItems: 156,
        totalUsers: 0, // Will be populated when user DB is added
        pendingRequests: 0, // Future feature: access requests
    };
}

export default async function AdminPage() {
    const session = await auth();

    // Redirect if not authenticated or not admin
    if (!session?.user) {
        redirect("/auth/signin?callbackUrl=/admin");
    }

    if (!session.user.isAdmin) {
        redirect("/?error=unauthorized");
    }

    const stats = await getSiteStats();

    return (
        <div className="min-h-screen bg-slate-950 w-full">
            {/* Header */}
            <header className="bg-slate-900/80 backdrop-blur-xl border-b border-slate-800/50 sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <Link
                                href="/"
                                className="text-slate-400 hover:text-white transition-colors"
                            >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                                </svg>
                            </Link>
                            <div>
                                <h1 className="text-2xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">
                                    Admin Dashboard
                                </h1>
                                <p className="text-sm text-slate-400">Rocket Design Studio Control Panel</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <span className="px-3 py-1 bg-amber-500/20 text-amber-400 text-sm font-medium rounded-full border border-amber-500/30">
                                Admin Mode
                            </span>
                        </div>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-6 py-8">
                {/* Welcome Section */}
                <div className="mb-8 p-6 bg-gradient-to-r from-slate-800/50 to-slate-800/30 rounded-2xl border border-slate-700/50">
                    <h2 className="text-xl font-semibold text-white mb-2">
                        Bienvenue, {session.user.name || "Admin"} 👋
                    </h2>
                    <p className="text-slate-400">
                        Voici un aperçu de l&apos;activité du site Rocket Design Studio.
                    </p>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                    <StatCard
                        title="Total Calculations"
                        value={stats.totalCalculations.toLocaleString()}
                        icon="🔬"
                        color="cyan"
                    />
                    <StatCard
                        title="CFD Simulations"
                        value={stats.cfDSimulations.toLocaleString()}
                        icon="🌊"
                        color="blue"
                    />
                    <StatCard
                        title="Active Sessions"
                        value={stats.activeSessions.toLocaleString()}
                        icon="👥"
                        color="green"
                    />
                    <StatCard
                        title="Material Library"
                        value={stats.materialLibraryItems.toLocaleString()}
                        icon="🧪"
                        color="purple"
                    />
                    <StatCard
                        title="Registered Users"
                        value={stats.totalUsers.toLocaleString()}
                        icon="👤"
                        color="amber"
                        description="Coming soon"
                    />
                    <StatCard
                        title="Access Requests"
                        value={stats.pendingRequests.toLocaleString()}
                        icon="📬"
                        color="rose"
                        description="Coming soon"
                    />
                </div>

                {/* Quick Actions */}
                <section className="mb-8">
                    <h3 className="text-lg font-semibold text-white mb-4">Actions Rapides</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <QuickActionCard
                            title="Combustion"
                            href="/combustion"
                            icon="🔥"
                        />
                        <QuickActionCard
                            title="CFD"
                            href="/cfd"
                            icon="🌊"
                        />
                        <QuickActionCard
                            title="Materials"
                            href="/materials"
                            icon="🧪"
                        />
                        <QuickActionCard
                            title="Cooling"
                            href="/cooling"
                            icon="❄️"
                        />
                    </div>
                </section>

                {/* Future Features Section */}
                <section className="p-6 bg-slate-800/30 rounded-2xl border border-slate-700/50">
                    <h3 className="text-lg font-semibold text-white mb-4">Fonctionnalités à Venir</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <FutureFeatureCard
                            title="Sync de Projets"
                            description="Synchronisez et sauvegardez les projets utilisateur"
                            status="planned"
                        />
                        <FutureFeatureCard
                            title="Collaboration"
                            description="Partagez des projets entre utilisateurs"
                            status="planned"
                        />
                        <FutureFeatureCard
                            title="API Keys"
                            description="Générez des clés API pour l'accès programmatique"
                            status="planned"
                        />
                        <FutureFeatureCard
                            title="Site Fermé"
                            description="Mode accès restreint avec demandes d'invitation"
                            status="planned"
                        />
                    </div>
                </section>
            </main>
        </div>
    );
}

function StatCard({
    title,
    value,
    icon,
    color,
    description,
}: {
    title: string;
    value: string;
    icon: string;
    color: "cyan" | "blue" | "green" | "purple" | "amber" | "rose";
    description?: string;
}) {
    const colorClasses = {
        cyan: "from-cyan-500/20 to-cyan-600/10 border-cyan-500/30",
        blue: "from-blue-500/20 to-blue-600/10 border-blue-500/30",
        green: "from-green-500/20 to-green-600/10 border-green-500/30",
        purple: "from-purple-500/20 to-purple-600/10 border-purple-500/30",
        amber: "from-amber-500/20 to-amber-600/10 border-amber-500/30",
        rose: "from-rose-500/20 to-rose-600/10 border-rose-500/30",
    };

    return (
        <div className={`p-6 rounded-xl bg-gradient-to-br ${colorClasses[color]} border backdrop-blur-sm`}>
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-sm text-slate-400 mb-1">{title}</p>
                    <p className="text-3xl font-bold text-white">{value}</p>
                    {description && (
                        <p className="text-xs text-slate-500 mt-1">{description}</p>
                    )}
                </div>
                <span className="text-3xl">{icon}</span>
            </div>
        </div>
    );
}

function QuickActionCard({
    title,
    href,
    icon,
}: {
    title: string;
    href: string;
    icon: string;
}) {
    return (
        <Link
            href={href}
            className="flex items-center gap-3 p-4 bg-slate-800/50 hover:bg-slate-700/50 rounded-xl border border-slate-700/50 transition-colors group"
        >
            <span className="text-2xl">{icon}</span>
            <span className="font-medium text-white group-hover:text-cyan-400 transition-colors">
                {title}
            </span>
            <svg className="w-5 h-5 text-slate-500 group-hover:text-cyan-400 ml-auto transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
        </Link>
    );
}

function FutureFeatureCard({
    title,
    description,
    status,
}: {
    title: string;
    description: string;
    status: "planned" | "in-progress" | "completed";
}) {
    const statusColors = {
        planned: "bg-slate-500/20 text-slate-400 border-slate-500/30",
        "in-progress": "bg-amber-500/20 text-amber-400 border-amber-500/30",
        completed: "bg-green-500/20 text-green-400 border-green-500/30",
    };

    const statusLabels = {
        planned: "Prévu",
        "in-progress": "En cours",
        completed: "Terminé",
    };

    return (
        <div className="p-4 bg-slate-800/30 rounded-xl border border-slate-700/30">
            <div className="flex items-start justify-between mb-2">
                <h4 className="font-medium text-white">{title}</h4>
                <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${statusColors[status]}`}>
                    {statusLabels[status]}
                </span>
            </div>
            <p className="text-sm text-slate-400">{description}</p>
        </div>
    );
}
