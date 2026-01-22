import { NextResponse } from "next/server";
import { getJob, setJob } from "@/lib/cfd-store";

export async function POST(request: Request) {
    try {
        const params = await request.json();
        
        // Generate job ID
        const jobId = `cfd-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        // Store job
        setJob(jobId, {
            status: "pending",
            progress: 0,
            params,
            createdAt: new Date()
        });
        
        // Start simulation in background
        simulateJob(jobId, params);
        
        return NextResponse.json({ 
            job_id: jobId,
            message: "Simulation CFD démarrée"
        });
    } catch (error) {
        console.error("CFD run error:", error);
        return NextResponse.json(
            { error: "Erreur lors du démarrage de la simulation" },
            { status: 500 }
        );
    }
}

// Simulate CFD computation (simplified for demo)
async function simulateJob(jobId: string, params: Record<string, unknown>) {
    const job = getJob(jobId);
    if (!job) return;
    
    job.status = "running";
    setJob(jobId, job);
    
    // Simulate progress over ~30 seconds
    const totalSteps = 100;
    const stepDelay = 300; // ms
    
    for (let i = 0; i <= totalSteps; i++) {
        await new Promise(r => setTimeout(r, stepDelay));
        
        job.progress = i / totalSteps;
        setJob(jobId, job); // Update progress
        
        if (i === totalSteps) {
            // Generate mock results based on input parameters
            const r_throat = (params.r_throat as number) || 0.025;
            const r_exit = (params.r_exit as number) || 0.1;
            const p_chamber = (params.p_chamber as number) || 2500000;
            const t_chamber = (params.t_chamber as number) || 3500;
            
            const expansion_ratio = (r_exit / r_throat) ** 2;
            const mach_exit = Math.sqrt(2 / 0.2 * ((p_chamber / 101325) ** 0.2 - 1));
            
            job.result = {
                summary: {
                    max_mach: Math.min(mach_exit, 4.5),
                    max_temperature: t_chamber,
                    min_pressure: p_chamber * 0.01,
                    max_velocity: mach_exit * 1000,
                    mass_flow: p_chamber * Math.PI * r_throat ** 2 / (t_chamber * 287),
                    thrust: p_chamber * Math.PI * r_throat ** 2 * 1.8,
                    isp_vacuum: 320 + expansion_ratio * 2,
                },
                mesh_info: {
                    cells: 125000,
                    points: 130000,
                    faces: 375000,
                },
                convergence: {
                    iterations: 1500,
                    residual_final: 1e-6,
                    time_seconds: 28.5,
                },
                field_data: generateFieldData(params),
            };
            job.status = "completed";
            setJob(jobId, job); // Final update
        }
    }
}

function generateFieldData(params: Record<string, unknown>) {
    const r_throat = (params.r_throat as number) || 0.025;
    const r_chamber = (params.r_chamber as number) || 0.05;
    const r_exit = (params.r_exit as number) || 0.1;
    const l_chamber = (params.l_chamber as number) || 0.1;
    const l_nozzle = (params.l_nozzle as number) || 0.2;
    const p_chamber = (params.p_chamber as number) || 2500000;
    const t_chamber = (params.t_chamber as number) || 3500;
    
    const points = [];
    const nAxial = 50;
    const nRadial = 20;
    
    for (let i = 0; i < nAxial; i++) {
        const x = (i / (nAxial - 1)) * (l_chamber + l_nozzle);
        
        // Calculate local radius based on position
        let r_local;
        if (x < l_chamber) {
            r_local = r_chamber;
        } else {
            const nozzle_x = (x - l_chamber) / l_nozzle;
            if (nozzle_x < 0.3) {
                // Convergent section
                r_local = r_chamber - (r_chamber - r_throat) * (nozzle_x / 0.3);
            } else {
                // Divergent section
                r_local = r_throat + (r_exit - r_throat) * ((nozzle_x - 0.3) / 0.7);
            }
        }
        
        for (let j = 0; j < nRadial; j++) {
            const r = (j / (nRadial - 1)) * r_local;
            
            // Calculate flow properties
            const area_ratio = (r_local / r_throat) ** 2;
            const mach = x < l_chamber ? 0.3 : Math.min(1 + (x - l_chamber) / l_nozzle * 3, 4);
            const pressure = p_chamber / (1 + 0.2 * mach ** 2) ** 3.5;
            const temperature = t_chamber / (1 + 0.2 * mach ** 2);
            const velocity = mach * Math.sqrt(1.2 * 287 * temperature);
            
            points.push({
                x: x * 1000, // Convert to mm
                y: r * 1000,
                mach,
                pressure: pressure / 1e5, // Convert to bar
                temperature,
                velocity,
            });
        }
    }
    
    return points;
}
