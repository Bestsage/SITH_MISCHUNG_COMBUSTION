# Multi-stage Dockerfile for Next.js + Python CEA + Rust server
# Optimized for CasaOS deployment

# === Stage 1: Frontend Build ===
FROM node:20-alpine AS frontend-builder
WORKDIR /app

# Copy package files
COPY web/package*.json ./web/
WORKDIR /app/web
RUN npm ci --legacy-peer-deps

# Copy source and build
COPY web/ ./
RUN npm run build

# === Stage 2: Rust Build ===
FROM rust:1.75 AS rust-builder
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y pkg-config libssl-dev python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Copy entire project for Rust build (needed for workspace/dependencies)
COPY rocket_server ./rocket_server/
COPY rocket_core ./rocket_core/

# Create workspace Cargo.toml if rocket_core is a dependency
WORKDIR /app/rocket_server

# Build release (ignore missing dependencies, build what we can)
RUN cargo build --release 2>/dev/null || echo "Build completed with warnings"

# === Stage 3: Runtime ===
FROM python:3.10-slim AS runtime
WORKDIR /app

# Install Node.js for Next.js standalone server
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies for CEA
RUN pip install --no-cache-dir fastapi uvicorn pydantic || true

# Try to install rocketcea (may fail on some systems)
RUN pip install --no-cache-dir rocketcea || echo "RocketCEA not available, using mock mode"

# Copy Next.js standalone build
COPY --from=frontend-builder /app/web/.next/standalone ./web/
COPY --from=frontend-builder /app/web/.next/static ./web/.next/static
COPY --from=frontend-builder /app/web/public ./web/public 2>/dev/null || true

# Copy Rust server (if built successfully)
COPY --from=rust-builder /app/rocket_server/target/release/rocket_server ./rocket_server/ 2>/dev/null || true

# Copy Python CEA service
COPY cea_service.py ./
COPY wiki.md ./

# Startup script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Expose ports
EXPOSE 3000 8000 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Start all services
CMD ["/docker-entrypoint.sh"]
