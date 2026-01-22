import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import Database from "better-sqlite3";
import path from "path";
import { randomUUID } from "crypto";

// Direct SQLite connection (Prisma 7 compatibility)
const dbPath = path.join(process.cwd(), "prisma", "dev.db");

function getDb() {
    return new Database(dbPath);
}

// Save CFD simulation results
export async function POST(request: Request) {
    try {
        const session = await auth();
        
        if (!session?.user?.id) {
            return NextResponse.json(
                { error: "Authentification requise" },
                { status: 401 }
            );
        }
        
        const body = await request.json();
        const { name, description, jobId, params, result } = body;
        
        if (!name || !result) {
            return NextResponse.json(
                { error: "Nom et résultats requis" },
                { status: 400 }
            );
        }
        
        const db = getDb();
        const id = randomUUID();
        
        db.prepare(`
            INSERT INTO CFDSimulation (id, name, description, jobId, params, result, userId, createdAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        `).run(id, name, description || "", jobId || null, JSON.stringify(params || {}), JSON.stringify(result), session.user.id);
        
        db.close();
        
        return NextResponse.json({
            id,
            message: "Simulation sauvegardée avec succès"
        });
        
    } catch (error) {
        console.error("CFD save error:", error);
        return NextResponse.json(
            { error: "Erreur lors de la sauvegarde", details: String(error) },
            { status: 500 }
        );
    }
}

// Get all saved CFD simulations for current user
export async function GET(request: Request) {
    try {
        const session = await auth();
        
        if (!session?.user?.id) {
            return NextResponse.json(
                { error: "Authentification requise" },
                { status: 401 }
            );
        }
        
        const db = getDb();
        const simulations = db.prepare(`
            SELECT id, name, description, jobId, createdAt
            FROM CFDSimulation
            WHERE userId = ?
            ORDER BY createdAt DESC
        `).all(session.user.id);
        
        db.close();
        
        return NextResponse.json(simulations);
        
    } catch (error) {
        console.error("CFD list error:", error);
        return NextResponse.json(
            { error: "Erreur lors de la récupération" },
            { status: 500 }
        );
    }
}
