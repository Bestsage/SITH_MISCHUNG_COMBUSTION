import { NextResponse } from "next/server";

// OpenFOAM service running in Docker container
const OPENFOAM_URL = process.env.OPENFOAM_URL || "http://172.18.0.2:8001";

export async function GET(request: Request) {
    try {
        const { searchParams } = new URL(request.url);
        const jobId = searchParams.get("jobId");
        
        if (!jobId) {
            return NextResponse.json(
                { error: "jobId requis" },
                { status: 400 }
            );
        }
        
        // Forward to real OpenFOAM service
        const response = await fetch(`${OPENFOAM_URL}/api/cfd/result/${jobId}`);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error("[CFD Result] OpenFOAM error:", errorText);
            return NextResponse.json(
                { error: `OpenFOAM result error: ${response.status}`, details: errorText },
                { status: response.status }
            );
        }
        
        const data = await response.json();
        
        // Return the raw OpenFOAM result - it should have the right structure
        return NextResponse.json(data);
    } catch (error) {
        console.error("CFD result error:", error);
        return NextResponse.json(
            { error: "Erreur lors de la récupération des résultats OpenFOAM" },
            { status: 500 }
        );
    }
}
