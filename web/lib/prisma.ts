import { PrismaClient } from "@prisma/client";
import { PrismaBetterSqlite3 } from "@prisma/adapter-better-sqlite3";
import Database from "better-sqlite3";
import path from "path";

const globalForPrisma = globalThis as unknown as {
    prisma: PrismaClient | undefined;
};

// Ensure direct file path for better-sqlite3
// Ensure direct file path for better-sqlite3
const dbPath = path.join(process.cwd(), "dev.db");
// Adapter expects simple config object apparently
const adapter = new PrismaBetterSqlite3({
    url: `file:${dbPath}`
});

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
