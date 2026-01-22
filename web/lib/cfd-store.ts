// Shared job store for CFD simulations
// In production, use Redis or a database

interface Job {
    status: "pending" | "running" | "completed" | "failed";
    progress: number;
    result?: unknown;
    error?: string;
    params: Record<string, unknown>;
    createdAt: Date;
}

// Use a global Map that persists across hot reloads
const globalForJobs = globalThis as unknown as { cfdJobs: Map<string, Job> | undefined };

export const jobs = globalForJobs.cfdJobs ?? new Map<string, Job>();

if (process.env.NODE_ENV !== "production") {
    globalForJobs.cfdJobs = jobs;
}

export function getJob(jobId: string): Job | undefined {
    return jobs.get(jobId);
}

export function setJob(jobId: string, job: Job) {
    jobs.set(jobId, job);
}

export function deleteJob(jobId: string) {
    jobs.delete(jobId);
}
