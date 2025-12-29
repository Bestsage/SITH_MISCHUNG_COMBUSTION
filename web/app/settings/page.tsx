import AppLayout from "@/components/AppLayout";

export default function SettingsPage() {
    return (
        <AppLayout>
            <div className="p-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Paramètres</h1>
                    <p className="text-[#71717a]">Configuration de l'application</p>
                </div>

                <div className="grid grid-cols-12 gap-6">
                    <div className="col-span-12 lg:col-span-6 space-y-6">
                        {/* Server Status */}
                        <div className="card">
                            <h3 className="card-header">🖥️ État des Serveurs</h3>
                            <div className="space-y-3">
                                <div className="flex items-center justify-between p-3 bg-[#1a1a25] rounded-lg">
                                    <div className="flex items-center gap-3">
                                        <div className="w-3 h-3 rounded-full bg-[#10b981] animate-pulse"></div>
                                        <span className="text-white font-medium">Serveur Rust (Axum)</span>
                                    </div>
                                    <span className="text-[#10b981]">localhost:8000</span>
                                </div>
                                <div className="flex items-center justify-between p-3 bg-[#1a1a25] rounded-lg">
                                    <div className="flex items-center gap-3">
                                        <div className="w-3 h-3 rounded-full bg-[#10b981] animate-pulse"></div>
                                        <span className="text-white font-medium">Service CEA (Python)</span>
                                    </div>
                                    <span className="text-[#10b981]">localhost:8001</span>
                                </div>
                                <div className="flex items-center justify-between p-3 bg-[#1a1a25] rounded-lg">
                                    <div className="flex items-center gap-3">
                                        <div className="w-3 h-3 rounded-full bg-[#10b981] animate-pulse"></div>
                                        <span className="text-white font-medium">Frontend (Next.js)</span>
                                    </div>
                                    <span className="text-[#10b981]">localhost:3000</span>
                                </div>
                            </div>
                        </div>

                        {/* About */}
                        <div className="card">
                            <h3 className="card-header">ℹ️ À Propos</h3>
                            <div className="data-grid">
                                <div className="data-row">
                                    <span className="data-label">Version</span>
                                    <span className="data-value">2.0.0</span>
                                </div>
                                <div className="data-row">
                                    <span className="data-label">Backend</span>
                                    <span className="data-value">Rust (Axum)</span>
                                </div>
                                <div className="data-row">
                                    <span className="data-label">Frontend</span>
                                    <span className="data-value">Next.js 14</span>
                                </div>
                                <div className="data-row">
                                    <span className="data-label">CEA</span>
                                    <span className="data-value">NASA CEA (RocketCEA)</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="col-span-12 lg:col-span-6 space-y-6">
                        {/* Architecture */}
                        <div className="card">
                            <h3 className="card-header">🏗️ Architecture</h3>
                            <div className="bg-[#1a1a25] rounded-lg p-4 font-mono text-xs text-[#a1a1aa]">
                                <pre>{`
┌──────────────────────────────┐
│     Frontend (Next.js)       │
│       localhost:3000         │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│   Serveur Rust (Axum)        │
│      localhost:8000          │
│  • /api/materials            │
│  • /api/geometry/generate    │
│  • /api/calculate/full       │
│  • /api/solve                │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│   Service CEA (Python)       │
│      localhost:8001          │
│  • NASA CEA calculations     │
└──────────────────────────────┘
                `.trim()}</pre>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
