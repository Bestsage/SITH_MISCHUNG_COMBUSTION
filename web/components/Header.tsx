"use client";

import { useSession } from "next-auth/react";
import Link from "next/link";
import { SignInButton, UserMenu } from "@/components/auth";

export function Header() {
    const { data: session, status } = useSession();

    return (
        <header className="fixed top-0 left-0 right-0 z-50 bg-slate-900/80 backdrop-blur-xl border-b border-slate-800/50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-3 group">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/25 group-hover:shadow-cyan-500/40 transition-shadow">
                            <span className="text-xl">🚀</span>
                        </div>
                        <div className="hidden sm:block">
                            <h1 className="font-bold text-white group-hover:text-cyan-400 transition-colors">
                                Rocket Design Studio
                            </h1>
                            <p className="text-xs text-slate-400">Advanced Engine Design</p>
                        </div>
                    </Link>

                    {/* Navigation (optionnel - à personnaliser) */}
                    <nav className="hidden md:flex items-center gap-6 text-sm">
                        <Link href="/combustion" className="text-slate-300 hover:text-white transition-colors">
                            Combustion
                        </Link>
                        <Link href="/cooling" className="text-slate-300 hover:text-white transition-colors">
                            Cooling
                        </Link>
                        <Link href="/cfd" className="text-slate-300 hover:text-white transition-colors">
                            CFD
                        </Link>
                        <Link href="/materials" className="text-slate-300 hover:text-white transition-colors">
                            Materials
                        </Link>
                    </nav>

                    {/* Auth Section */}
                    <div className="flex items-center gap-4">
                        {status === "loading" ? (
                            <div className="w-10 h-10 rounded-full bg-slate-700 animate-pulse" />
                        ) : session?.user ? (
                            <UserMenu />
                        ) : (
                            <SignInButton />
                        )}
                    </div>
                </div>
            </div>
        </header>
    );
}
