import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  experimental: {
    serverActions: {
      allowedOrigins: ['*'],
    },
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*', // Proxy to Rust backend
      },
      {
        source: '/docs', // Optional: Proxy documentation if needed
        destination: 'http://localhost:8000/docs',
      }
    ];
  },
};

export default nextConfig;
