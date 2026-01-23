import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  experimental: {
    serverActions: {
      allowedOrigins: ['*'],
    },
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'avatars.githubusercontent.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'lh3.googleusercontent.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'cdn.discordapp.com',
        pathname: '/**',
      },
    ],
  },
  async rewrites() {
    return {
      // Auth routes should NOT be proxied - handled by NextAuth
      beforeFiles: [],
      afterFiles: [
        // CFD API routes -> OpenFOAM container (direct, avoids timeout)
        {
          source: '/api/cfd/:path*',
          destination: 'http://openfoam-cfd:8001/api/cfd/:path*',
        },
        // All other API routes -> Rust backend (except auth, user, admin)
        {
          source: '/api/:path((?!auth|user|admin).*)',
          destination: 'http://localhost:8000/api/:path*',
        },
        {
          source: '/docs',
          destination: 'http://localhost:8000/docs',
        }
      ],
      fallback: [],
    };
  },
};

export default nextConfig;
