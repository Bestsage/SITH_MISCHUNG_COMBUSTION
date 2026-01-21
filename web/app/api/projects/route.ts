import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { NextResponse } from "next/server";

export async function GET(req: Request) {
    const session = await auth();
    if (!session?.user?.id) {
        return new NextResponse("Unauthorized", { status: 401 });
    }

    try {
        // Récupérer les projets où l'utilisateur est membre ou propriétaire
        // ADMIN voit tout
        const where: any = session.user.isAdmin
            ? {}
            : {
                OR: [
                    { ownerId: session.user.id },
                    { members: { some: { userId: session.user.id } } },
                    { isPublic: true }
                ]
            };

        const projects = await prisma.project.findMany({
            where,
            orderBy: { updatedAt: "desc" },
            include: {
                owner: {
                    select: { name: true, image: true, email: true }
                },
                _count: {
                    select: { members: true, data: true }
                }
            }
        });

        return NextResponse.json(projects);
    } catch (error) {
        return new NextResponse("Internal Error", { status: 500 });
    }
}

export async function POST(req: Request) {
    const session = await auth();
    if (!session?.user?.id) {
        return new NextResponse("Unauthorized", { status: 401 });
    }

    try {
        const body = await req.json();
        const { name, description, isPublic } = body;

        const project = await prisma.project.create({
            data: {
                name,
                description,
                isPublic: !!isPublic,
                ownerId: session.user.id,
                members: {
                    create: {
                        userId: session.user.id,
                        role: "OWNER"
                    }
                }
            }
        });

        // Log activity
        await prisma.activity.create({
            data: {
                type: "project_create",
                userId: session.user.id,
                projectId: project.id,
                metadata: JSON.stringify({ name: project.name })
            }
        });

        return NextResponse.json(project);
    } catch (error) {
        return new NextResponse("Internal Error", { status: 500 });
    }
}
