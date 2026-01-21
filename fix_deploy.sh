#!/bin/bash
# Script to resolve "KeyError: 'ContainerConfig'" on Docker Compose 1.29.2

echo "🛑 Stopping containers..."
docker-compose stop

echo "🧹 FORCE CLEANUP: Removing potentially corrupted containers..."
docker rm -f sith-monolith sith-openfoam 2>/dev/null || true

echo "🧹 Cleaning up network and orphans..."
docker-compose down --remove-orphans

echo "🚀 Rebuilding and starting application..."
docker-compose up -d --build

echo "✅ Done! Check logs with: docker logs -f sith-monolith"
