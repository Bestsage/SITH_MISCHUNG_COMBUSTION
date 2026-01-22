import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { writeFile, mkdir } from "fs/promises";
import path from "path";

// Sync profile image from OAuth provider
export async function POST(request: Request) {
    try {
        const session = await auth();
        if (!session?.user?.email) {
            return NextResponse.json({ error: "Non autorisé" }, { status: 401 });
        }

        const body = await request.json();
        const { action, provider, imageUrl, targetUserId } = body;

        // Check if user is admin for updating other users
        const currentUser = await prisma.user.findUnique({
            where: { email: session.user.email },
            include: { accounts: true }
        });

        if (!currentUser) {
            return NextResponse.json({ error: "Utilisateur non trouvé" }, { status: 404 });
        }

        const isAdmin = currentUser.role === "ADMIN" || currentUser.role === "SUPERADMIN";
        const userId = (targetUserId && isAdmin) ? targetUserId : currentUser.id;

        if (action === "sync") {
            // Sync from OAuth provider
            const account = currentUser.accounts.find(a => a.provider === provider);
            if (!account) {
                return NextResponse.json({ error: `Compte ${provider} non lié` }, { status: 400 });
            }

            // Get the image URL from the OAuth provider
            let newImageUrl: string | null = null;

            if (provider === "github" && account.providerAccountId) {
                newImageUrl = `https://avatars.githubusercontent.com/u/${account.providerAccountId}`;
            } else if (provider === "google" && imageUrl) {
                newImageUrl = imageUrl;
            } else if (provider === "discord" && account.providerAccountId) {
                // Discord avatar - need to fetch from API or use default
                newImageUrl = `https://cdn.discordapp.com/avatars/${account.providerAccountId}/default.png`;
            }

            if (newImageUrl) {
                await prisma.user.update({
                    where: { id: userId },
                    data: { image: newImageUrl }
                });
                return NextResponse.json({ success: true, image: newImageUrl });
            }

            return NextResponse.json({ error: "Impossible de récupérer l'image" }, { status: 400 });
        }

        if (action === "upload") {
            // Handle base64 image upload
            if (!imageUrl || !imageUrl.startsWith("data:image/")) {
                return NextResponse.json({ error: "Image invalide" }, { status: 400 });
            }

            // Extract base64 data
            const matches = imageUrl.match(/^data:image\/(\w+);base64,(.+)$/);
            if (!matches) {
                return NextResponse.json({ error: "Format d'image invalide" }, { status: 400 });
            }

            const ext = matches[1];
            const base64Data = matches[2];
            const buffer = Buffer.from(base64Data, "base64");

            // Ensure uploads directory exists
            const uploadsDir = path.join(process.cwd(), "public", "uploads", "avatars");
            await mkdir(uploadsDir, { recursive: true });

            // Generate unique filename
            const filename = `${userId}-${Date.now()}.${ext}`;
            const filepath = path.join(uploadsDir, filename);

            // Write file
            await writeFile(filepath, buffer);

            // Update user with new image URL
            const publicUrl = `/uploads/avatars/${filename}`;
            await prisma.user.update({
                where: { id: userId },
                data: { image: publicUrl }
            });

            return NextResponse.json({ success: true, image: publicUrl });
        }

        if (action === "remove") {
            await prisma.user.update({
                where: { id: userId },
                data: { image: null }
            });
            return NextResponse.json({ success: true, image: null });
        }

        return NextResponse.json({ error: "Action non reconnue" }, { status: 400 });
    } catch (error) {
        console.error("Error updating profile image:", error);
        return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
    }
}

// GET - Get user's linked accounts for photo sync options
export async function GET() {
    try {
        const session = await auth();
        if (!session?.user?.email) {
            return NextResponse.json({ error: "Non autorisé" }, { status: 401 });
        }

        const user = await prisma.user.findUnique({
            where: { email: session.user.email },
            select: {
                id: true,
                image: true,
                accounts: {
                    select: {
                        provider: true,
                        providerAccountId: true
                    }
                }
            }
        });

        if (!user) {
            return NextResponse.json({ error: "Utilisateur non trouvé" }, { status: 404 });
        }

        // Build available sync options
        const syncOptions = user.accounts.map(account => {
            let previewUrl: string | null = null;

            if (account.provider === "github") {
                previewUrl = `https://avatars.githubusercontent.com/u/${account.providerAccountId}`;
            } else if (account.provider === "discord") {
                previewUrl = `https://cdn.discordapp.com/avatars/${account.providerAccountId}/default.png`;
            }

            return {
                provider: account.provider,
                previewUrl
            };
        });

        return NextResponse.json({
            currentImage: user.image,
            syncOptions
        });
    } catch (error) {
        console.error("Error getting profile image options:", error);
        return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
    }
}
