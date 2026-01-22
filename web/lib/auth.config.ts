import type { NextAuthConfig } from "next-auth";

// This config is used by the Edge middleware only
// It cannot access the database, so we just check if there's a valid session
// The actual authentication logic is in auth.ts

export const authConfig = {
    // No providers here - they are defined in auth.ts
    // The middleware only needs to check existing sessions
    providers: [],
    pages: {
        signIn: "/auth/signin",
        error: "/auth/error",
    },
    callbacks: {
        authorized({ auth, request: { nextUrl } }) {
            const isLoggedIn = !!auth?.user;
            const isOnAuthPage = nextUrl.pathname.startsWith('/auth');
            const isOnApiAuth = nextUrl.pathname.startsWith('/api/auth');
            const isOnApi = nextUrl.pathname.startsWith('/api');

            console.log("[Middleware] Path:", nextUrl.pathname);
            console.log("[Middleware] isLoggedIn:", isLoggedIn);
            console.log("[Middleware] auth?.user:", auth?.user?.email);

            // Auth bypass mode - allows access without login
            const authBypass = process.env.AUTH_BYPASS === 'true';
            if (authBypass) {
                return true;
            }

            // Allow access to auth pages, API auth routes, and all API routes
            if (isOnAuthPage || isOnApiAuth || isOnApi) {
                return true;
            }

            // Redirect unauthenticated users to login page
            if (!isLoggedIn) {
                return false;
            }

            return true;
        },
        jwt({ token, user }) {
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
            }
            return session;
        }
    },
    trustHost: true,
} satisfies NextAuthConfig;
