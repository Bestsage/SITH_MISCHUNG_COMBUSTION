import { NextRequest, NextResponse } from "next/server";
import { readFile } from "fs/promises";
import { existsSync } from "fs";
import path from "path";

// Serve uploaded avatar images
export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ filename: string }> }
) {
    try {
        const { filename } = await params;

        // Validate filename to prevent path traversal attacks
        if (!filename || filename.includes('..') || filename.includes('/')) {
            return NextResponse.json({ error: "Invalid filename" }, { status: 400 });
        }

        // Check both possible locations (Docker and development)
        const isDocker = process.env.DATABASE_URL?.includes('/app/db');
        const basePath = isDocker ? '/app/web/public/uploads/avatars' : path.join(process.cwd(), 'public', 'uploads', 'avatars');
        const filepath = path.join(basePath, filename);

        console.log(`[Avatar Serve] Trying to serve: ${filepath} (Docker: ${isDocker})`);

        if (!existsSync(filepath)) {
            console.log(`[Avatar Serve] File not found: ${filepath}`);
            return NextResponse.json({ error: "Image not found" }, { status: 404 });
        }

        const buffer = await readFile(filepath);

        // Determine content type from extension
        const ext = path.extname(filename).toLowerCase();
        const contentTypes: Record<string, string> = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
        };
        const contentType = contentTypes[ext] || 'application/octet-stream';

        console.log(`[Avatar Serve] Serving ${filename} as ${contentType}`);

        return new NextResponse(buffer, {
            headers: {
                'Content-Type': contentType,
                'Cache-Control': 'public, max-age=31536000, immutable',
            },
        });
    } catch (error) {
        console.error("[Avatar Serve] Error:", error);
        return NextResponse.json({ error: "Server error" }, { status: 500 });
    }
}
