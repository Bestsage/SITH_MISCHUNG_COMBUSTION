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
            include: { accounts: true },
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
                // GitHub: can construct URL from account ID
                newImageUrl = `https://avatars.githubusercontent.com/u/${account.providerAccountId}`;
            } else if (provider === "google") {
                // For Google, use passed imageUrl or user's current Google image
                if (imageUrl) {
                    newImageUrl = imageUrl;
                } else if (currentUser.image?.includes('googleusercontent.com')) {
                    newImageUrl = currentUser.image;
                }
            } else if (provider === "discord") {
                // For Discord, use passed imageUrl or user's current Discord image
                if (imageUrl) {
                    newImageUrl = imageUrl;
                } else if (currentUser.image?.includes('cdn.discordapp.com')) {
                    newImageUrl = currentUser.image;
                }
            } else if (imageUrl) {
                newImageUrl = imageUrl;
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
            console.log("[Image Upload] Starting upload...");

            if (!imageUrl || !imageUrl.startsWith("data:image/")) {
                console.log("[Image Upload] Invalid image data");
                return NextResponse.json({ error: "Image invalide" }, { status: 400 });
            }

            // Extract base64 data
            const matches = imageUrl.match(/^data:image\/(\w+);base64,(.+)$/);
            if (!matches) {
                console.log("[Image Upload] Failed to parse base64");
                return NextResponse.json({ error: "Format d'image invalide" }, { status: 400 });
            }

            const ext = matches[1];
            const base64Data = matches[2];
            const buffer = Buffer.from(base64Data, "base64");
            console.log(`[Image Upload] Parsed image: ${ext}, size: ${buffer.length} bytes`);

            // Ensure uploads directory exists
            const uploadsDir = path.join(process.cwd(), "public", "uploads", "avatars");
            console.log(`[Image Upload] Uploads dir: ${uploadsDir}`);

            try {
                await mkdir(uploadsDir, { recursive: true });
            } catch (mkdirErr) {
                console.error("[Image Upload] Failed to create directory:", mkdirErr);
            }

            // Generate unique filename
            const filename = `${userId}-${Date.now()}.${ext}`;
            const filepath = path.join(uploadsDir, filename);
            console.log(`[Image Upload] Writing to: ${filepath}`);

            // Write file
            try {
                await writeFile(filepath, buffer);
                console.log("[Image Upload] File written successfully");
            } catch (writeErr) {
                console.error("[Image Upload] Failed to write file:", writeErr);
                return NextResponse.json({ error: "Erreur d'écriture du fichier" }, { status: 500 });
            }

            // Update user with new image URL
            const publicUrl = `/uploads/avatars/${filename}`;
            await prisma.user.update({
                where: { id: userId },
                data: { image: publicUrl }
            });
            console.log(`[Image Upload] User updated with image: ${publicUrl}`);

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
        const syncOptions = user.accounts.map((account: { provider: string; providerAccountId: string }) => {
            let previewUrl: string | null = null;

            if (account.provider === "github") {
                // GitHub: can always construct URL from account ID
                previewUrl = `https://avatars.githubusercontent.com/u/${account.providerAccountId}`;
            } else if (account.provider === "google" && user.image?.includes('googleusercontent.com')) {
                // For Google, use user's current image if it's from Google
                previewUrl = user.image;
            } else if (account.provider === "discord" && user.image?.includes('cdn.discordapp.com')) {
                // For Discord, use user's current image if it's from Discord
                previewUrl = user.image;
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
