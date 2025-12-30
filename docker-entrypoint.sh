#!/bin/bash
# Docker entrypoint script - starts all services

echo "🚀 Starting Rocket Design Studio..."

# Start CEA Python microservice in background
echo "🔬 Starting CEA Service on :8001..."
cd /app && python cea_service.py &

# Wait for CEA to start
sleep 2

# Start Rust API server in background
echo "⚙️ Starting Rust API on :8000..."
cd /app/rocket_server && ./rocket_server &

# Wait for Rust to start
sleep 2

# Start Next.js frontend (foreground)
echo "🌐 Starting Next.js on :3000..."
cd /app/web && node server.js
