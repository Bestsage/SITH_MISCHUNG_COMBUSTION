# Simplified Dockerfile for Next.js + Python CEA
# Optimized for CasaOS deployment (without Rust server for now)

# === Stage 1: Frontend Build ===
FROM node:20-alpine AS frontend-builder
WORKDIR /app

# Copy package files
COPY web/package*.json ./web/
WORKDIR /app/web
RUN npm ci --legacy-peer-deps || npm install --legacy-peer-deps

# Copy source and build
COPY web/ ./
RUN npm run build

# === Stage 2: Runtime ===
FROM python:3.10-slim AS runtime
WORKDIR /app

# Install Node.js for Next.js standalone server
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies for CEA
RUN pip install --no-cache-dir fastapi uvicorn pydantic

# Try to install rocketcea (may fail on some systems without Fortran)
RUN pip install --no-cache-dir rocketcea || echo "RocketCEA not available"

# Copy Next.js standalone build
COPY --from=frontend-builder /app/web/.next/standalone ./web/
COPY --from=frontend-builder /app/web/.next/static ./web/.next/static
COPY --from=frontend-builder /app/web/public ./web/public

# Copy Python CEA service
COPY cea_service.py ./
COPY wiki.md ./

# Create simple startup script
RUN echo '#!/bin/bash\n\
    echo "🚀 Starting Rocket Design Studio..."\n\
    cd /app && python cea_service.py &\n\
    sleep 2\n\
    cd /app/web && node server.js\n\
    ' > /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

# Expose ports
EXPOSE 3000 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Start services
CMD ["/docker-entrypoint.sh"]
