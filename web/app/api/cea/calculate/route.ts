import { NextResponse } from "next/server";

const CEA_SERVICE_URL = process.env.CEA_SERVICE_URL || "http://localhost:8001";

export async function POST(request: Request) {
    try {
        const params = await request.json();
        
        // Forward to CEA Python service
        const response = await fetch(`${CEA_SERVICE_URL}/cea`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                fuel: params.fuel || "RP-1",
                oxidizer: params.oxidizer || "LOX",
                of_ratio: params.of_ratio || 2.5,
                pc: params.pc || 50.0,  // bar
                expansion_ratio: params.expansion_ratio || 40.0,
            }),
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error("CEA service error:", errorText);
            return NextResponse.json(
                { error: `CEA service error: ${response.status}` },
                { status: response.status }
            );
        }
        
        const data = await response.json();
        return NextResponse.json(data);
        
    } catch (error) {
        console.error("CEA calculate error:", error);
        
        // Return mock data if CEA service is unavailable
        const params = await request.json().catch(() => ({}));
        return NextResponse.json({
            chamber: {
                temperature: 3500 + Math.random() * 200,
                pressure: (params.pc || 50) * 1e5,
                density: 3.2,
                molecular_weight: 22.5,
                gamma: 1.15,
                cp: 2100,
                viscosity: 8.5e-5,
                conductivity: 0.15,
                prandtl: 0.75,
            },
            throat: {
                temperature: 3200 + Math.random() * 100,
                pressure: (params.pc || 50) * 0.56 * 1e5,
                velocity: 1150,
                mach: 1.0,
                area_ratio: 1.0,
            },
            exit: {
                temperature: 1800 + Math.random() * 200,
                pressure: 1.0e5,
                velocity: 2800 + Math.random() * 200,
                mach: 3.2,
                area_ratio: params.expansion_ratio || 40,
            },
            performance: {
                cstar: 1750 + Math.random() * 50,
                cf_vacuum: 1.85,
                cf_sea_level: 1.55,
                isp_vacuum: 320 + Math.random() * 20,
                isp_sea_level: 270 + Math.random() * 15,
            },
            propellants: {
                fuel: params.fuel || "RP-1",
                oxidizer: params.oxidizer || "LOX",
                of_ratio: params.of_ratio || 2.5,
            },
            _mock: true,
            _message: "CEA service unavailable - using approximations"
        });
    }
}
