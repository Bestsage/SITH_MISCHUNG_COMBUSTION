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
                { error: "Job non trouvé", available: Array.from(jobs.keys()) },
                { status: 404 }
            );
        }
        
        return NextResponse.json({
            status: job.status,
            progress: job.progress,
            error: job.error,
        });
    } catch (error) {
        console.error("CFD status error:", error);
        return NextResponse.json(
            { error: "Erreur lors de la récupération du status" },
            { status: 500 }
        );
    }
}
