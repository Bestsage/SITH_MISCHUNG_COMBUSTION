# Multi-stage Dockerfile for Next.js + Python CEA + Rust server
# Optimized for CasaOS deployment

# === Stage 1: Frontend Build ===
FROM node:20-alpine AS frontend-builder
WORKDIR /app/web

# Copy package files
COPY web/package*.json ./
RUN npm ci

# Copy source and build
COPY web/ ./
RUN npm run build

# === Stage 2: Rust Build ===
FROM rust:1.75-slim AS rust-builder
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*

# Copy Cargo files
COPY rocket_server/Cargo.toml rocket_server/Cargo.lock ./rocket_server/
COPY rocket_server/src ./rocket_server/src
COPY rocket_core ./rocket_core

# Build release
WORKDIR /app/rocket_server
RUN cargo build --release

# === Stage 3: Runtime ===
FROM python:3.10-slim AS runtime
WORKDIR /app

# Install Node.js for Next.js standalone server
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies for CEA
RUN pip install --no-cache-dir fastapi uvicorn rocketcea pydantic

# Copy Next.js standalone build
COPY --from=frontend-builder /app/web/.next/standalone ./web/
COPY --from=frontend-builder /app/web/.next/static ./web/.next/static
COPY --from=frontend-builder /app/web/public ./web/public

# Copy Rust server
COPY --from=rust-builder /app/rocket_server/target/release/rocket_server ./rocket_server/

# Copy Python CEA service
COPY cea_service.py ./
COPY wiki.md ./

# Startup script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Expose ports
EXPOSE 3000 8000 8001

# Start all services
CMD ["/docker-entrypoint.sh"]
