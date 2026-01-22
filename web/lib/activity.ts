// Activity tracking utility
// Tracks user activities and stores them locally + syncs to server

const STORAGE_KEY = "rocket_studio_stats";

interface LocalStats {
    simulations: number;
    designs: number;
    cfdAnalyses: number;
    lastSync: string;
}

function getLocalStats(): LocalStats {
    if (typeof window === "undefined") {
        return { simulations: 0, designs: 0, cfdAnalyses: 0, lastSync: "" };
    }
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            return JSON.parse(stored);
        }
    } catch {
        // ignore
    }
    return { simulations: 0, designs: 0, cfdAnalyses: 0, lastSync: "" };
}

function setLocalStats(stats: LocalStats) {
    if (typeof window === "undefined") return;
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(stats));
    } catch {
        // ignore
    }
}

export async function trackActivity(type: string, metadata?: Record<string, unknown>) {
    // Update local stats
    const local = getLocalStats();
    
    if (type === "simulation" || type === "cea_calculation" || type === "combustion_calc") {
        local.simulations++;
    } else if (type === "design_save" || type === "project_create") {
        local.designs++;
    } else if (type === "cfd_analysis" || type === "cfd_run") {
        local.cfdAnalyses++;
    }
    
    setLocalStats(local);
    
    // Try to sync to server
    try {
        await fetch("/api/user/stats", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ type, metadata })
        });
    } catch {
        // Silent fail - local stats are saved
    }
}

export function getStats(): LocalStats {
    return getLocalStats();
}

export function resetLocalStats() {
    setLocalStats({ simulations: 0, designs: 0, cfdAnalyses: 0, lastSync: "" });
}
