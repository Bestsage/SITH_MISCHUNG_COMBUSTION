import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { NextResponse } from "next/server";

export async function GET(
    req: Request,
    { params }: { params: Promise<{ id: string }> }
) {
    const session = await auth();
    const { id } = await params;

    if (!session?.user?.id) {
        return new NextResponse("Unauthorized", { status: 401 });
    }

    try {
        const project = await prisma.project.findUnique({
            where: { id },
            include: {
                owner: { select: { name: true, email: true, image: true } },
                members: {
                    include: {
                        user: { select: { name: true, email: true, image: true } }
                    }
                }
            }
        });

        if (!project) {
            return new NextResponse("Not Found", { status: 404 });
        }

        // Check permissions
        const isMember = project.members.some((m: any) => m.userId === session.user.id);
        const isAdmin = session.user.isAdmin;
        const isPublic = project.isPublic;

        if (!isMember && !isAdmin && !isPublic) {
            return new NextResponse("Forbidden", { status: 403 });
        }

        return NextResponse.json(project);
    } catch (error) {
        return new NextResponse("Internal Error", { status: 500 });
    }
}

export async function PATCH(
    req: Request,
    { params }: { params: Promise<{ id: string }> }
) {
    const session = await auth();
    const { id } = await params;

    if (!session?.user?.id) {
        return new NextResponse("Unauthorized", { status: 401 });
    }

    try {
        // Check permissions directly in query or before
        const member = await prisma.projectMember.findUnique({
            where: {
                userId_projectId: {
                    userId: session.user.id,
                    projectId: id
                }
            }
        });

        const isProjectAdmin = member?.role === "OWNER" || member?.role === "PROJECT_ADMIN";
        const isSiteAdmin = session.user.isAdmin;

        if (!isProjectAdmin && !isSiteAdmin) {
            return new NextResponse("Forbidden", { status: 403 });
        }

        const body = await req.json();
        const { name, description, isPublic, grade } = body;

        const data: any = { name, description, isPublic };

        // Only superadmins/admins can change grade
        if (grade && session.user.isAdmin) {
            data.grade = grade;
        }

        const updatedProject = await prisma.project.update({
            where: { id },
            data,
        });

        return NextResponse.json(updatedProject);
    } catch (error) {
        return new NextResponse("Internal Error", { status: 500 });
    }
}

export async function DELETE(
    req: Request,
    { params }: { params: Promise<{ id: string }> }
) {
    const session = await auth();
    const { id } = await params;

    if (!session?.user?.id) {
        return new NextResponse("Unauthorized", { status: 401 });
    }

    try {
        const project = await prisma.project.findUnique({
            where: { id },
            include: { members: true }
        });

        if (!project) return new NextResponse("Not Found", { status: 404 });

        // Only Owner or Site Admin can delete
        const isOwner = project.ownerId === session.user.id;
        const isSiteAdmin = session.user.isAdmin;

        if (!isOwner && !isSiteAdmin) {
            return new NextResponse("Forbidden", { status: 403 });
        }

        await prisma.project.delete({
            where: { id }
        });

        return new NextResponse(null, { status: 204 });
    } catch (error) {
        return new NextResponse("Internal Error", { status: 500 });
    }
}
