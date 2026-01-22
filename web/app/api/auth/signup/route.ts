import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

// Simple hash function - same as in auth.ts
function hashPassword(password: string): string {
    const crypto = require('crypto');
    return crypto.createHash('sha256').update(password).digest('hex');
}

export async function POST(request: Request) {
    try {
        const body = await request.json();
        const { name, email, password } = body;

        console.log("[Signup] Attempting signup for:", email);

        if (!name || !email || !password) {
            return NextResponse.json(
                { error: "Tous les champs sont requis" },
                { status: 400 }
            );
        }

        if (password.length < 4) {
            return NextResponse.json(
                { error: "Le mot de passe doit contenir au moins 4 caractères" },
                { status: 400 }
            );
        }

        // Check if user already exists
        let existingUser;
        try {
            existingUser = await prisma.user.findUnique({
                where: { email: email.toLowerCase() }
            });
            console.log("[Signup] Existing user check:", existingUser ? "found" : "not found");
        } catch (dbError) {
            console.error("[Signup] Database error checking user:", dbError);
            return NextResponse.json(
                { error: "Erreur de base de données" },
                { status: 500 }
            );
        }

        if (existingUser) {
            return NextResponse.json(
                { error: "Un compte existe déjà avec cet email" },
                { status: 400 }
            );
        }

        // Create user
        const user = await prisma.user.create({
            data: {
                name,
                email: email.toLowerCase(),
                password: hashPassword(password),
                role: "USER"
            }
        });

        // Create welcome activity
        await prisma.activity.create({
            data: {
                type: "account_created",
                metadata: JSON.stringify({ source: "signup" }),
                userId: user.id
            }
        });

        return NextResponse.json({
            success: true,
            user: {
                id: user.id,
                name: user.name,
                email: user.email
            }
        });
    } catch (error) {
        console.error("Signup error:", error);
        return NextResponse.json(
            { error: "Erreur lors de la création du compte" },
            { status: 500 }
        );
    }
}
