import { PrismaClient } from "@prisma/client";
import { PrismaBetterSQLite3 } from "@prisma/adapter-better-sqlite3";
import path from "path";

const globalForPrisma = globalThis as unknown as {
    prisma: PrismaClient | undefined;
};

// Ensure direct file path for better-sqlite3 - pointing to prisma/dev.db
const dbPath = path.join(process.cwd(), "prisma", "dev.db");
const connectionString = `file:${dbPath}`;

console.log("Prisma DB path:", dbPath);

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
