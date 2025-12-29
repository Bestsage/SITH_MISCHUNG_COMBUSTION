"use client";

import Sidebar from "@/components/Sidebar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="flex w-full">
            <Sidebar />
            <main className="flex-1 overflow-auto bg-slate-950 p-8">
                {children}
            </main>
        </div>
    );
}
