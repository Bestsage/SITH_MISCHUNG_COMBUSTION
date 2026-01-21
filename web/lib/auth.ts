import NextAuth from "next-auth";
import { PrismaAdapter } from "@auth/prisma-adapter";
import { prisma } from "@/lib/prisma";
import { authConfig } from "./auth.config";


// Extend the session type to include admin role
declare module "next-auth" {
    interface Session {
        user: {
            id?: string;
            name?: string | null;
            email?: string | null;
            image?: string | null;
            isAdmin?: boolean;
            role?: string;
        };
    }
}

// Admin email(s) - the main user who has full access
const ADMIN_EMAILS = (process.env.ADMIN_EMAIL || "").split(",").map((e) => e.trim().toLowerCase());

export const { handlers, signIn, signOut, auth } = NextAuth({
    ...authConfig,
    adapter: PrismaAdapter(prisma),
    session: { strategy: "database" }, // Explicitly use database strategy with adapter
    callbacks: {
        ...authConfig.callbacks,
        async session({ session, user }) {
            // With database adapter, 'user' object is passed to session callback
            if (session.user && user) {
                session.user.id = user.id;
                // Check DB role or env var admin
                // We use 'any' cast because Prisma user type might not match explicitly yet in TS
                const userRole = (user as any).role;
                const userEmail = session.user.email?.toLowerCase();

                session.user.role = userRole;
                session.user.isAdmin = userRole === 'ADMIN' || userRole === 'SUPERADMIN' || (userEmail ? ADMIN_EMAILS.includes(userEmail) : false);

                // Auto-promote to SUPERADMIN if in env var
                if (userEmail && ADMIN_EMAILS.includes(userEmail) && userRole !== 'SUPERADMIN') {
                    // Optimization: Auto promote logic is handled in signIn event usually
                }
            }
            return session;
        }
    },
    events: {
        async signIn({ user }) {
            // Update last login
            if (user.id) {
                try {
                    await prisma.user.update({
                        where: { id: user.id },
                        data: { lastLoginAt: new Date() },
                    });

                    // Auto-promote to SUPERADMIN if email matches env
                    if (user.email && ADMIN_EMAILS.includes(user.email.toLowerCase())) {
                        const currentUser = await prisma.user.findUnique({ where: { id: user.id } });
                        if (currentUser && currentUser.role !== 'SUPERADMIN') {
                            await prisma.user.update({
                                where: { id: user.id },
                                data: { role: 'SUPERADMIN' }
                            });
                        }
                    }
                } catch (error) {
                    console.error("Error updating user login:", error);
                }
            }
        }
    },
});
