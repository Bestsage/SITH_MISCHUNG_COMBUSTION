import { PrismaClient } from "@prisma/client";
import { PrismaBetterSQLite3 } from "@prisma/adapter-better-sqlite3";
import Database from "better-sqlite3";
import path from "path";

const globalForPrisma = globalThis as unknown as {
    prisma: PrismaClient | undefined;
};

// Ensure direct file path for better-sqlite3
// Ensure direct file path for better-sqlite3
// Ensure direct file path for better-sqlite3
const dbPath = path.join(process.cwd(), "dev.db");
// Initialize better-sqlite3 database instance
const db = new Database(dbPath);
// Pass the database instance to the adapter
const adapter = new PrismaBetterSQLite3(db);

export const prisma =
    globalForPrisma.prisma ??
    new PrismaClient({
        adapter,
        log: process.env.NODE_ENV === "development" ? ["query", "error", "warn"] : ["error"],
    });

if (process.env.NODE_ENV !== "production") {
    globalForPrisma.prisma = prisma;
}

export default prisma;
