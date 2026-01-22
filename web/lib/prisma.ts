import { PrismaClient } from "@prisma/client";
import { PrismaBetterSQLite3 } from "@prisma/adapter-better-sqlite3";
import path from "path";

const globalForPrisma = globalThis as unknown as {
    prisma: PrismaClient | undefined;
};

// Use DATABASE_URL if defined, otherwise fallback to local prisma/dev.db
let connectionString: string;

if (process.env.DATABASE_URL) {
    // Use the environment variable directly
    connectionString = process.env.DATABASE_URL;
    console.log("Prisma using DATABASE_URL:", connectionString);
} else {
    // Fallback for local development
    const dbPath = path.join(process.cwd(), "prisma", "dev.db");
    connectionString = `file:${dbPath}`;
    console.log("Prisma using local path:", dbPath);
}

// Initialize adapter with the correct configuration object
const adapter = new PrismaBetterSQLite3({
    url: connectionString,
});

export const prisma =
    globalForPrisma.prisma ??
    new PrismaClient({
        adapter,
        log: process.env.NODE_ENV === "development" ? ["error", "warn"] : ["error"],
    });

if (process.env.NODE_ENV !== "production") {
    globalForPrisma.prisma = prisma;
}

export default prisma;
