"use client";

import { Activity, Flame, Droplets, Rocket, Database, Settings, Menu, X, ChevronRight, Wind } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

const NAV_ITEMS = [
    { name: "Vue d'ensemble", icon: Activity, href: "/", gradient: "from-blue-500 to-cyan-500" },
    { name: "Thermodynamique", icon: Flame, href: "/thermo", gradient: "from-orange-500 to-red-500" },
    { name: "Canal de Refroidissement", icon: Droplets, href: "/cooling", gradient: "from-green-500 to-emerald-500" },
    { name: "Combustion", icon: Rocket, href: "/combustion", gradient: "from-purple-500 to-pink-500" },
    { name: "CFD 2D", icon: Wind, href: "/cfd", gradient: "from-cyan-500 to-blue-500" },
    { name: "Matériaux", icon: Database, href: "/materials", gradient: "from-yellow-500 to-orange-500" },
    { name: "Paramètres", icon: Settings, href: "/settings", gradient: "from-slate-500 to-slate-600" },
];

export default function Sidebar() {
    const [collapsed, setCollapsed] = useState(false);

    return (
        <aside
            className={`relative backdrop-blur-xl bg-slate-900/80 border-r border-slate-700/50 transition-all duration-300 flex flex-col h-screen sticky top-0 shadow-2xl ${collapsed ? "w-20" : "w-72"
                }`}
        >
            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 via-purple-600/5 to-pink-600/5 pointer-events-none"></div>

            {/* Header */}
            <div className="relative p-6 border-b border-slate-700/50">
                <div className="flex items-center justify-between">
                    {!collapsed && (
                        <div className="flex items-center space-x-3">
                            <div className="p-2 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 shadow-lg shadow-blue-500/50">
                                <Rocket className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <h2 className="font-black text-lg bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                                    ROCKET
                                </h2>
                                <p className="text-xs text-slate-500 font-medium">Design Studio</p>
                            </div>
                        </div>
                    )}
                    <button
                        onClick={() => setCollapsed(!collapsed)}
                        className="p-2 hover:bg-slate-800/50 rounded-xl transition-all hover:scale-110 active:scale-95"
                    >
                        {collapsed ? <ChevronRight className="w-5 h-5 text-slate-400" /> : <X className="w-5 h-5 text-slate-400" />}
                    </button>
                </div>
            </div>

            {/* Navigation */}
            <nav className="relative flex-1 py-6 space-y-2 overflow-y-auto px-3">
                {NAV_ITEMS.map((item, idx) => (
                    <Link
                        key={item.name}
                        href={item.href}
                        className="group relative flex items-center px-4 py-4 text-slate-300 hover:text-white rounded-2xl transition-all hover:scale-105 active:scale-95"
                        style={{ animationDelay: `${idx * 50}ms` }}
                    >
                        {/* Hover Background */}
                        <div className={`absolute inset-0 bg-gradient-to-r ${item.gradient} opacity-0 group-hover:opacity-10 rounded-2xl transition-opacity`}></div>

                        {/* Glow Effect */}
                        <div className={`absolute -inset-1 bg-gradient-to-r ${item.gradient} opacity-0 group-hover:opacity-20 blur-lg rounded-2xl transition-opacity`}></div>

                        {/* Icon */}
                        <div className={`relative p-2 rounded-xl bg-gradient-to-br ${item.gradient} group-hover:scale-110 transition-transform shadow-lg`}>
                            <item.icon className="w-5 h-5 text-white" />
                        </div>

                        {/* Label */}
                        {!collapsed && (
                            <span className="relative ml-4 font-bold text-sm">{item.name}</span>
                        )}

                        {/* Active Indicator */}
                        {item.href === "/" && (
                            <div className="absolute right-4 w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                        )}
                    </Link>
                ))}
            </nav>

            {/* Footer - User Profile */}
            <div className="relative p-4 border-t border-slate-700/50">
                <div className="flex items-center space-x-3">
                    <div className="relative">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center font-black text-white shadow-lg">
                            U
                        </div>
                        <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 border-2 border-slate-900 rounded-full"></div>
                    </div>
                    {!collapsed && (
                        <div className="flex-1">
                            <p className="text-sm font-bold text-white">Ingénieur</p>
                            <p className="text-xs text-slate-500">En ligne</p>
                        </div>
                    )}
                </div>
            </div>
        </aside>
    );
}
