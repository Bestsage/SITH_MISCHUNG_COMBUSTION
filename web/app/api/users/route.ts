import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { NextResponse } from "next/server";

export async function GET() {
    const session = await auth();

    if (!session?.user?.isAdmin) {
        return new NextResponse("Unauthorized", { status: 401 });
    }

    try {
        const users = await prisma.user.findMany({
            orderBy: { createdAt: "desc" },
            select: {
                id: true,
                name: true,
                email: true,
                image: true,
                role: true,
                createdAt: true,
                lastLoginAt: true,
                _count: {
                    select: { ownedProjects: true }
                }
            }
        });

        return NextResponse.json(users);
    } catch (error) {
        return new NextResponse("Internal Error", { status: 500 });
    }
}

export async function PATCH(req: Request) {
    const session = await auth();

    // Seul le SUPERADMIN peut changer les rôles (ou l'admin pour passer USER -> ADMIN, à voir)
    // Pour l'instant, disons admin
    if (!session?.user?.isAdmin) {
        return new NextResponse("Unauthorized", { status: 401 });
    }

    try {
        const body = await req.json();
        const { userId, role } = body;

        if (!["USER", "ADMIN", "SUPERADMIN"].includes(role)) {
            return new NextResponse("Invalid role", { status: 400 });
        }

        // Empêcher de modifier son propre rôle pour éviter de se bloquer
        if (userId === session.user.id) {
            return new NextResponse("Cannot change own role", { status: 400 });
        }

        const updatedUser = await prisma.user.update({
            where: { id: userId },
            data: { role },
        });

        return NextResponse.json(updatedUser);
    } catch (error) {
        return new NextResponse("Internal Error", { status: 500 });
    }
}
