import type { NextAuthConfig } from "next-auth";
import GitHub from "next-auth/providers/github";
import Google from "next-auth/providers/google";
import Discord from "next-auth/providers/discord";
import Slack from "next-auth/providers/slack";

export const authConfig = {
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
    pages: {
        signIn: "/auth/signin",
        error: "/auth/error",
    },
    callbacks: {
        authorized({ auth, request: { nextUrl } }) {
            const isLoggedIn = !!auth?.user;
            const isOnAuthPage = nextUrl.pathname.startsWith('/auth');
            const isOnApiAuth = nextUrl.pathname.startsWith('/api/auth');
            const isOnPublicPage = nextUrl.pathname === '/' || nextUrl.pathname.startsWith('/_next') || nextUrl.pathname.startsWith('/static');

            // Auth bypass mode - allows access without login
            const authBypass = process.env.AUTH_BYPASS === 'true';
            if (authBypass) {
                return true; // Allow all access when bypass is enabled
            }

            // Allow access to auth pages and API auth routes
            if (isOnAuthPage || isOnApiAuth) {
                return true;
            }

            // Redirect unauthenticated users to login page
            if (!isLoggedIn) {
                return false; // Redirects to signin page automatically by default
            }

            return true;
        },
        jwt({ token, user, trigger, session }) {
            if (user) {
                token.id = user.id;
                token.role = (user as any).role;
            }
            return token;
        },
        session({ session, token }) {
            if (session.user && token) {
                session.user.id = token.id as string;
                session.user.role = token.role as string;

                // Admin check can stay here or be moved, but session callback runs on server/client, usually OK.
                // However, for pure Edge compatibility, we might want to keep this simple.
                // The advanced role logic from DB will be in auth.ts
            }
            return session;
        }
    },
    trustHost: true,
} satisfies NextAuthConfig;
