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
        const response = await fetch(`${OPENFOAM_URL}/api/cfd/status/${jobId}`);
        
        if (!response.ok) {
            const errorText = await response.text();
            return NextResponse.json(
                { error: `OpenFOAM status error: ${response.status}`, details: errorText },
                { status: response.status }
            );
        }
        
        const data = await response.json();
        
        return NextResponse.json({
            status: data.status,
            progress: data.progress,
            message: data.message,
            error: data.status === "failed" ? data.message : undefined,
        });
    } catch (error) {
        console.error("CFD status error:", error);
        return NextResponse.json(
            { error: "Erreur de connexion au serveur OpenFOAM" },
            { status: 500 }
        );
    }
}
