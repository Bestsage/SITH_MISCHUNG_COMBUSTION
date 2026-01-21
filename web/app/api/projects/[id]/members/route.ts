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

    // Allow members and admins to see member list
    try {
        const isMember = await prisma.projectMember.findUnique({
            where: { userId_projectId: { userId: session.user.id, projectId: id } }
        });

        if (!isMember && !session.user.isAdmin) {
            return new NextResponse("Forbidden", { status: 403 });
        }

        const members = await prisma.projectMember.findMany({
            where: { projectId: id },
            include: {
                user: {
                    select: { id: true, name: true, email: true, image: true }
                }
            }
        });

        return NextResponse.json(members);
    } catch (error) {
        return new NextResponse("Internal Error", { status: 500 });
    }
}

export async function POST(
    req: Request,
    { params }: { params: Promise<{ id: string }> }
) {
    const session = await auth();
    const { id } = await params;

    if (!session?.user?.id) return new NextResponse("Unauthorized", { status: 401 });

    try {
        // Permission check: Need PROJECT_ADMIN or OWNER
        const currentMember = await prisma.projectMember.findUnique({
            where: { userId_projectId: { userId: session.user.id, projectId: id } }
        });

        if (!session.user.isAdmin && (!currentMember || (currentMember.role !== 'OWNER' && currentMember.role !== 'PROJECT_ADMIN'))) {
            return new NextResponse("Forbidden", { status: 403 });
        }

        const { email, role } = await req.json();

        // Find user by email
        const user = await prisma.user.findUnique({ where: { email } });
        if (!user) return new NextResponse("User not found", { status: 404 });

        // Check if already member
        const existingMember = await prisma.projectMember.findUnique({
            where: { userId_projectId: { userId: user.id, projectId: id } }
        });
        if (existingMember) return new NextResponse("User already in project", { status: 400 });

        // Add member
        const newMember = await prisma.projectMember.create({
            data: {
                projectId: id,
                userId: user.id,
                role: role || 'VIEWER'
            },
            include: { user: true }
        });

        // Log invite
        await prisma.activity.create({
            data: {
                type: "member_invite",
                userId: session.user.id,
                projectId: id,
                metadata: JSON.stringify({ invitedUser: email, role })
            }
        });

        return NextResponse.json(newMember);
    } catch (error) {
        return new NextResponse("Internal Error", { status: 500 });
    }
}
