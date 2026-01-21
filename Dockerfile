# Full Dockerfile for Next.js + Python CEA + Rust server
# Optimized for CasaOS deployment

# === Stage 1: Frontend Build ===
FROM node:22-alpine AS frontend-builder
WORKDIR /app

# Copy package files
COPY web/package*.json ./web/
WORKDIR /app/web
RUN npm ci --legacy-peer-deps || npm install --legacy-peer-deps

# Copy source and build
# Copy source and build
COPY web/ ./
RUN echo "=== DEBUG FILE STRUCTURE ===" && ls -R lib/ && ls -R app/
RUN echo "=== DEBUG TSCONFIG ===" && cat tsconfig.json
RUN npx prisma generate
RUN npm run build

# === Stage 2: Rust Build ===
FROM rust:latest AS rust-builder
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*

# Copy Rust project
COPY rocket_server/ ./rocket_server/
COPY rocket_core/ ./rocket_core/

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
RUN pip install --no-cache-dir fastapi uvicorn pydantic

# Try to install rocketcea
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    gfortran \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir rocketcea || echo "RocketCEA not available"

# Copy Next.js standalone build
COPY --from=frontend-builder /app/web/.next/standalone ./web/
COPY --from=frontend-builder /app/web/.next/static ./web/.next/static
COPY --from=frontend-builder /app/web/public ./web/public
COPY --from=frontend-builder /app/web/prisma ./web/prisma

# Copy Rust server binary
COPY --from=rust-builder /app/rocket_server/target/release/rocket_server ./

# Copy Python CEA service and resources
COPY cea_service.py ./
COPY wiki.md ./

# Create startup script
RUN echo '#!/bin/bash\n\
    echo "🚀 Starting Rocket Design Studio..."\n\
    echo "🔬 Starting CEA Service on :8001..."\n\
    cd /app && python cea_service.py &\n\
    sleep 2\n\
    echo "⚙️ Starting Rust API on :8000..."\n\
    cd /app && ./rocket_server &\n\
    sleep 2\n\
    echo "🌐 Starting Next.js on :3000..."\n\
    cd /app/web && node server.js\n\
    ' > /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

# Expose ports
EXPOSE 3000 8000 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Start all services
CMD ["/docker-entrypoint.sh"]
