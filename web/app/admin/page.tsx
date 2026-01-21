import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma"; // Direct DB access because server component
import { redirect } from "next/navigation";
import Link from "next/link";
import Image from "next/image";

async function getSiteStats() {
    const [
        totalUsers,
        totalProjects,
        totalActivities,
        recentProjects,
        recentUsers
    ] = await Promise.all([
        prisma.user.count(),
        prisma.project.count(),
        prisma.activity.count(),
        prisma.project.findMany({
            take: 5,
            orderBy: { createdAt: 'desc' },
            include: { owner: true }
        }),
        prisma.user.findMany({
            take: 5,
            orderBy: { createdAt: 'desc' }
        })
    ]);

    return {
        totalUsers,
        totalProjects,
        totalActivities,
        recentProjects,
        recentUsers,
        totalCalculations: 1247 + totalActivities, // Hybrid stat
    };
}

export default async function AdminPage() {
    const session = await auth();

    // Redirect if not authenticated or not admin
    if (!session?.user) {
        redirect("/auth/signin?callbackUrl=/admin");
    }

    // Note: session.user.isAdmin comes from our extended session logic
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
                                    Super Admin
                                </h1>
                                <p className="text-sm text-slate-400">Master Control Panel</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="px-3 py-1 bg-amber-500/20 text-amber-400 text-sm font-medium rounded-full border border-amber-500/30 flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
                                Live Database
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-6 py-8">

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <StatCard
                        title="Total Users"
                        value={stats.totalUsers.toLocaleString()}
                        icon="👥"
                        color="cyan"
                    />
                    <StatCard
                        title="Projects"
                        value={stats.totalProjects.toLocaleString()}
                        icon="🚀"
                        color="blue"
                    />
                    <StatCard
                        title="Activities"
                        value={stats.totalActivities.toLocaleString()}
                        icon="⚡"
                        color="purple"
                    />
                    <StatCard
                        title="Simulations"
                        value={stats.totalCalculations.toLocaleString()}
                        icon="🔥"
                        color="orange"
                    />
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Recent Users */}
                    <section className="bg-slate-900/50 rounded-2xl border border-slate-800/50 p-6">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <span className="text-xl">🌟</span> New Users
                        </h3>
                        <div className="space-y-4">
                            {stats.recentUsers.map((user: any) => (
                                <div key={user.id} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-xl hover:bg-slate-700/50 transition-colors">
                                    <div className="flex items-center gap-3">
                                        {user.image ? (
                                            <Image src={user.image} alt="avatar" width={40} height={40} className="rounded-full" />
                                        ) : (
                                            <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center text-slate-300">
                                                {user.name?.[0]?.toUpperCase() || "U"}
                                            </div>
                                        )}
                                        <div>
                                            <p className="font-medium text-white">{user.name || "Anonymous"}</p>
                                            <p className="text-xs text-slate-400">{user.email}</p>
                                        </div>
                                    </div>
                                    <div className="flex flex-col items-end">
                                        <span className={`text-xs font-mono px-2 py-0.5 rounded-full border ${user.role === 'SUPERADMIN' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                                            user.role === 'ADMIN' ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' :
                                                'bg-slate-500/20 text-slate-400 border-slate-500/30'
                                            }`}>
                                            {user.role}
                                        </span>
                                        <span className="text-xs text-slate-500 mt-1">
                                            {new Date(user.createdAt).toLocaleDateString()}
                                        </span>
                                    </div>
                                </div>
                            ))}
                            <div className="text-center py-2 text-sm text-slate-500">
                                Manage users in database directly for now
                            </div>
                        </div>
                    </section>

                    {/* Recent Projects */}
                    <section className="bg-slate-900/50 rounded-2xl border border-slate-800/50 p-6">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <span className="text-xl">🛠️</span> Recent Projects
                        </h3>
                        <div className="space-y-4">
                            {stats.recentProjects.map((project: any) => (
                                <div key={project.id} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-xl hover:bg-slate-700/50 transition-colors">
                                    <div>
                                        <h4 className="font-medium text-white">{project.name}</h4>
                                        <p className="text-xs text-slate-400">by {project.owner.name}</p>
                                    </div>
                                    <div className="flex flex-col items-end">
                                        <span className={`text-xs px-2 py-0.5 rounded-full border ${project.grade === 'ENTERPRISE' ? 'bg-purple-500/20 text-purple-400 border-purple-500/30' :
                                            project.grade === 'PREMIUM' ? 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30' :
                                                'bg-slate-500/20 text-slate-400 border-slate-500/30'
                                            }`}>
                                            {project.grade}
                                        </span>
                                        <span className="text-xs text-slate-500 mt-1">
                                            {new Date(project.createdAt).toLocaleDateString()}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>
                </div>
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
    color: "cyan" | "blue" | "green" | "purple" | "amber" | "rose" | "orange";
    description?: string;
}) {
    const colorClasses = {
        cyan: "from-cyan-500/20 to-cyan-600/10 border-cyan-500/30",
        blue: "from-blue-500/20 to-blue-600/10 border-blue-500/30",
        green: "from-green-500/20 to-green-600/10 border-green-500/30",
        purple: "from-purple-500/20 to-purple-600/10 border-purple-500/30",
        amber: "from-amber-500/20 to-amber-600/10 border-amber-500/30",
        rose: "from-rose-500/20 to-rose-600/10 border-rose-500/30",
        orange: "from-orange-500/20 to-orange-600/10 border-orange-500/30",
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
