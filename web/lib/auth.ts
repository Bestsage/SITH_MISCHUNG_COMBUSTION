import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";
import Google from "next-auth/providers/google";
import Discord from "next-auth/providers/discord";
import Slack from "next-auth/providers/slack";
import { PrismaAdapter } from "@auth/prisma-adapter";
import { prisma } from "@/lib/prisma";

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
    adapter: PrismaAdapter(prisma),
    providers: [
        GitHub({
            clientId: process.env.GITHUB_CLIENT_ID,
            clientSecret: process.env.GITHUB_CLIENT_SECRET,
        }),
        Google({
            clientId: process.env.GOOGLE_CLIENT_ID,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET,
        }),
        Discord({
            clientId: process.env.DISCORD_CLIENT_ID,
            clientSecret: process.env.DISCORD_CLIENT_SECRET,
        }),
        Slack({
            clientId: process.env.SLACK_CLIENT_ID,
            clientSecret: process.env.SLACK_CLIENT_SECRET,
        }),
    ],
    callbacks: {
        async jwt({ token, user }) {
            // Add admin flag to the token (only needed if using JWT session, which Prisma adapter might not use by default but we can check)
            // With database, NextAuth often uses database sessions, but we can stick to JWT strategy or just enhance session
            return token;
        },
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
                    // We can't await prisma here easily without causing delays, 
                    // but technically we could update the user in DB if we imported prisma
                    // For now, allow access via isAdmin flag
                }
            }
            return session;
        },
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
    pages: {
        signIn: "/auth/signin",
        error: "/auth/error",
    },
    trustHost: true,
});
