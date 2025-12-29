"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";

const NAV_ITEMS = [
    { name: "Vue d'ensemble", href: "/", icon: "📊" },
    { name: "Éléments CEA", href: "/elements", icon: "⚗️" },
    { name: "Thermodynamique", href: "/thermo", icon: "🌡️" },
    { name: "Refroidissement", href: "/cooling", icon: "❄️" },
    { name: "Matériaux", href: "/materials", icon: "🧱" },
    { name: "Wiki", href: "/wiki", icon: "📖" },
    { name: "Paramètres", href: "/settings", icon: "⚙️" },
];

export default function AppLayout({ children }: { children: ReactNode }) {
    const pathname = usePathname();

    return (
        <div className="min-h-screen bg-[#0a0a0f] flex">
            {/* Sidebar */}
            <aside className="w-64 bg-[#12121a] border-r border-[#27272a] flex flex-col">
                {/* Logo */}
                <div className="p-6 border-b border-[#27272a]">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#00d4ff] to-[#8b5cf6] flex items-center justify-center">
                            <span className="text-xl">🚀</span>
                        </div>
                        <div>
                            <h1 className="font-bold text-white text-lg">ROCKET</h1>
                            <p className="text-xs text-[#71717a]">Design Studio</p>
                        </div>
                    </div>
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-4 space-y-1">
                    {NAV_ITEMS.map((item) => (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`nav-item ${pathname === item.href ? 'nav-item-active' : ''}`}
                        >
                            <span className="text-lg">{item.icon}</span>
                            <span className="font-medium">{item.name}</span>
                        </Link>
                    ))}
                </nav>

                {/* Status */}
                <div className="p-4 border-t border-[#27272a]">
                    <div className="card p-3">
                        <div className="flex items-center gap-2 mb-2">
                            <div className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse"></div>
                            <span className="text-xs text-[#a1a1aa]">Serveurs</span>
                        </div>
                        <div className="space-y-1 text-xs">
                            <div className="flex justify-between">
                                <span className="text-[#71717a]">Rust API</span>
                                <span className="text-[#10b981]">:8000</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-[#71717a]">CEA Service</span>
                                <span className="text-[#10b981]">:8001</span>
                            </div>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 bg-grid overflow-auto">
                {children}
            </main>
        </div>
    );
}
