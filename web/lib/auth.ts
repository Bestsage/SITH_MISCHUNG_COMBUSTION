import NextAuth from "next-auth";
import { PrismaAdapter } from "@auth/prisma-adapter";
import { prisma } from "@/lib/prisma";
import Credentials from "next-auth/providers/credentials";
import GitHub from "next-auth/providers/github";
import Google from "next-auth/providers/google";
import Discord from "next-auth/providers/discord";
import Slack from "next-auth/providers/slack";

// Simple hash function for passwords (in production, use bcrypt)
function hashPassword(password: string): string {
    // Simple hash for demo - in production use bcrypt!
    const crypto = require('crypto');
    return crypto.createHash('sha256').update(password).digest('hex');
}

function verifyPassword(password: string, hash: string): boolean {
    return hashPassword(password) === hash;
}

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

console.log("[Auth] NEXTAUTH_URL:", process.env.NEXTAUTH_URL);
console.log("[Auth] NODE_ENV:", process.env.NODE_ENV);

export const { handlers, signIn, signOut, auth } = NextAuth({
    adapter: PrismaAdapter(prisma),
    session: {
        strategy: "jwt",
        maxAge: 30 * 24 * 60 * 60, // 30 days
    },
    // Let NextAuth handle cookies automatically
    providers: [
        Credentials({
            name: "Email",
            credentials: {
                email: { label: "Email", type: "email" },
                password: { label: "Mot de passe", type: "password" }
            },
            async authorize(credentials) {
                console.log("[Auth] authorize() called with email:", credentials?.email);

                if (!credentials?.email || !credentials?.password) {
                    console.log("[Auth] Missing credentials");
                    return null;
                }

                const email = (credentials.email as string).toLowerCase();
                const password = credentials.password as string;

                console.log("[Auth] Looking up user:", email);

                // Find user in database
                let user;
                try {
                    user = await prisma.user.findUnique({
                        where: { email }
                    });
                    console.log("[Auth] User found:", user ? "yes" : "no");
                } catch (error) {
                    console.error("[Auth] Database error:", error);
                    return null;
                }

                if (!user) {
                    // User doesn't exist - create if it's admin email with default password
                    console.log("[Auth] User not found, checking admin email");
                    if (ADMIN_EMAILS.includes(email) && password === "1234") {
                        const newUser = await prisma.user.create({
                            data: {
                                email,
                                name: "Samuel Gebhard",
                                password: hashPassword("1234"),
                                role: "SUPERADMIN",
                            }
                        });
                        console.log("[Auth] Created admin user");
                        return {
                            id: newUser.id,
                            email: newUser.email,
                            name: newUser.name,
                            role: newUser.role,
                        };
                    }
                    console.log("[Auth] Not admin or wrong password");
                    return null;
                }

                // Verify password
                if (user.password) {
                    if (!verifyPassword(password, user.password)) {
                        return null;
                    }
                } else {
                    // User exists but has no password (OAuth user)
                    // Allow admin with default password to set it
                    if (ADMIN_EMAILS.includes(email) && password === "1234") {
                        await prisma.user.update({
                            where: { id: user.id },
                            data: { password: hashPassword("1234") }
                        });
                    } else {
                        return null;
                    }
                }

                return {
                    id: user.id,
                    email: user.email,
                    name: user.name,
                    image: user.image,
                    role: user.role,
                };
            }
        }),
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
    pages: {
        signIn: "/auth/signin",
        error: "/auth/error",
    },
    callbacks: {
        authorized({ auth, request: { nextUrl } }) {
            const isLoggedIn = !!auth?.user;
            const isOnAuthPage = nextUrl.pathname.startsWith('/auth');
            const isOnApiAuth = nextUrl.pathname.startsWith('/api/auth');

            // Auth bypass mode
            const authBypass = process.env.AUTH_BYPASS === 'true';
            if (authBypass) return true;

            if (isOnAuthPage || isOnApiAuth) return true;
            if (!isLoggedIn) return false;

            return true;
        },
        async signIn({ user, account, profile }) {
            // Allow credentials sign-in
            if (account?.provider === "credentials") {
                return true;
            }

            // For OAuth providers, check if user with this email already exists
            if (user.email && account) {
                try {
                    const existingUser = await prisma.user.findUnique({
                        where: { email: user.email.toLowerCase() },
                        include: { accounts: true }
                    });

                    if (existingUser) {
                        // Check if this OAuth account is already linked
                        const linkedAccount = existingUser.accounts.find(
                            a => a.provider === account.provider && a.providerAccountId === account.providerAccountId
                        );

                        if (!linkedAccount) {
                            // Link the OAuth account to existing user
                            await prisma.account.create({
                                data: {
                                    userId: existingUser.id,
                                    type: account.type,
                                    provider: account.provider,
                                    providerAccountId: account.providerAccountId,
                                    access_token: account.access_token,
                                    refresh_token: account.refresh_token,
                                    expires_at: account.expires_at,
                                    token_type: account.token_type,
                                    scope: account.scope,
                                    id_token: account.id_token,
                                    session_state: account.session_state as string | undefined,
                                }
                            });

                            console.log(`[Auth] Linked ${account.provider} account to existing user ${existingUser.email}`);
                        }

                        // Always update user image from OAuth provider
                        // Google uses 'picture', GitHub uses 'avatar_url', Discord uses 'image_url' or avatar in profile
                        const profileImage = (profile as any)?.picture || (profile as any)?.avatar_url || (profile as any)?.image_url;
                        if (profileImage) {
                            await prisma.user.update({
                                where: { id: existingUser.id },
                                data: { image: profileImage }
                            });
                            console.log(`[Auth] Updated image from ${account.provider} for ${existingUser.email}`);
                        }
                    }
                } catch (error) {
                    console.error("[Auth] Error linking OAuth account:", error);
                    // Don't block sign-in on linking error
                }
            }

            return true;
        },
        async jwt({ token, user }) {
            if (user) {
                token.id = user.id;
                token.role = (user as any).role;
                token.email = user.email;
            }
            return token;
        },
        async session({ session, token }) {
            if (session.user && token) {
                session.user.id = token.id as string;
                session.user.role = token.role as string;
                session.user.email = token.email as string;

                // Fetch fresh user data from database (image and name can change)
                try {
                    const dbUser = await prisma.user.findUnique({
                        where: { id: token.id as string },
                        select: { image: true, name: true }
                    });
                    if (dbUser) {
                        session.user.image = dbUser.image;
                        session.user.name = dbUser.name;
                    }
                } catch (e) {
                    console.error("[Auth] Error fetching user data for session:", e);
                }

                const userEmail = session.user.email?.toLowerCase();
                session.user.isAdmin =
                    token.role === 'ADMIN' ||
                    token.role === 'SUPERADMIN' ||
                    (userEmail ? ADMIN_EMAILS.includes(userEmail) : false);
            }
            return session;
        }
    },
    events: {
        async signIn({ user }) {
            if (user.id) {
                try {
                    await prisma.user.update({
                        where: { id: user.id },
                        data: { lastLoginAt: new Date() },
                    });

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
    trustHost: true,
});
