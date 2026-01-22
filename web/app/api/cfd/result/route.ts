import { NextResponse } from "next/server";
import { jobs } from "@/lib/cfd-store";

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
        
        const job = jobs.get(jobId);
        
        if (!job) {
            return NextResponse.json(
                { error: "Job non trouvé" },
                { status: 404 }
            );
        }
        
        if (job.status !== "completed") {
            return NextResponse.json(
                { error: "Simulation pas encore terminée", status: job.status, progress: job.progress },
                { status: 202 }
            );
        }
        
        return NextResponse.json(job.result);
    } catch (error) {
        console.error("CFD result error:", error);
        return NextResponse.json(
            { error: "Erreur lors de la récupération des résultats" },
            { status: 500 }
        );
    }
}
