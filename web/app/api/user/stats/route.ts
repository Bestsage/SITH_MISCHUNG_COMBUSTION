import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function GET() {
    try {
        const session = await auth();
        if (!session?.user?.email) {
            return NextResponse.json({ error: "Non autorisé" }, { status: 401 });
        }

        const user = await prisma.user.findUnique({
            where: { email: session.user.email },
            include: {
                activities: {
                    orderBy: { createdAt: "desc" },
                    take: 20
                }
            }
        });

        if (!user) {
            return NextResponse.json({ error: "Utilisateur non trouvé" }, { status: 404 });
        }

        // Count activities by type
        const allActivities = await prisma.activity.findMany({
            where: { userId: user.id }
        });

        // Get counts from activities or return 0
        const simCount = allActivities.filter(a => 
            a.type === "simulation" || 
            a.type === "cea_calculation" || 
            a.type === "combustion_calc"
        ).length;
        
        const designCount = allActivities.filter(a => 
            a.type === "design_save" || 
            a.type === "project_create"
        ).length;
        
        const cfdCount = allActivities.filter(a => 
            a.type === "cfd_analysis" || 
            a.type === "cfd_run"
        ).length;

        const stats = {
            simulations: simCount,
            designs: designCount,
            cfdAnalyses: cfdCount,
            memberSince: user.createdAt.toISOString(),
            lastLogin: user.lastLoginAt?.toISOString() || user.createdAt.toISOString(),
            recentActivities: user.activities.map(a => ({
                id: a.id,
                type: a.type,
                metadata: a.metadata ? JSON.parse(a.metadata) : null,
                createdAt: a.createdAt.toISOString()
            }))
        };

        return NextResponse.json(stats);
    } catch (error) {
        console.error("Error fetching user stats:", error);
        return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
    }
}

// Track a new activity
export async function POST(request: Request) {
    try {
        const session = await auth();
        if (!session?.user?.email) {
            return NextResponse.json({ error: "Non autorisé" }, { status: 401 });
        }

        const user = await prisma.user.findUnique({
            where: { email: session.user.email }
        });

        if (!user) {
            return NextResponse.json({ error: "Utilisateur non trouvé" }, { status: 404 });
        }

        const body = await request.json();
        const { type, metadata } = body;

        const activity = await prisma.activity.create({
            data: {
                type,
                metadata: metadata ? JSON.stringify(metadata) : null,
                userId: user.id
            }
        });

        return NextResponse.json({ success: true, activityId: activity.id });
    } catch (error) {
        console.error("Error creating activity:", error);
        return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
    }
}
