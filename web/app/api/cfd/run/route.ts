import { NextResponse } from "next/server";

// OpenFOAM service running in Docker container
const OPENFOAM_URL = process.env.OPENFOAM_URL || "http://localhost:8001";

export async function POST(request: Request) {
    try {
        const params = await request.json();
        
        console.log("[CFD Run] Forwarding to OpenFOAM:", OPENFOAM_URL);
        
        // Forward to real OpenFOAM service
        const response = await fetch(`${OPENFOAM_URL}/api/cfd/run`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                r_throat: params.r_throat || 0.025,
                r_chamber: params.r_chamber || 0.05,
                r_exit: params.r_exit || 0.075,
                l_chamber: params.l_chamber || 0.1,
                l_nozzle: params.l_nozzle || 0.2,
                p_chamber: params.p_chamber || 2500000,
                p_ambient: params.p_ambient || 101325,
                t_chamber: params.t_chamber || 3500,
                gamma: params.gamma || 1.2,
                molar_mass: params.molar_mass || 0.022,
                nx: params.nx || 150,
                ny: params.ny || 50,
                max_iter: params.max_iter || 5000,
                solver: "openfoam"
            }),
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error("[CFD Run] OpenFOAM error:", errorText);
            return NextResponse.json(
                { error: `OpenFOAM error: ${response.status}`, details: errorText },
                { status: response.status }
            );
        }
        
        const data = await response.json();
        console.log("[CFD Run] Job created:", data.job_id);
        
        return NextResponse.json(data);
        
    } catch (error) {
        console.error("[CFD Run] Error:", error);
        return NextResponse.json(
            { error: "Erreur de connexion au serveur OpenFOAM", details: String(error) },
            { status: 500 }
        );
    }
}
