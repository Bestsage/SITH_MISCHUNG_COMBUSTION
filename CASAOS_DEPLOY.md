# CasaOS Deployment Guide

## 🚀 Auto-Deploying Rocket Design Studio on CasaOS

This project is configured for automatic deployment on CasaOS with updates on every GitHub push.

## Setup Steps

### 1. Prerequisites

- CasaOS installed on your server
- Docker running on CasaOS
- GitHub repository with Actions enabled

### 2. GitHub Actions (Already Configured)

The workflow at `.github/workflows/deploy.yml` automatically builds and pushes Docker images to GitHub Container Registry (ghcr.io) on every push to `main` or `master`.

**Image URL:** `ghcr.io/bestsage/sith_mischung_combustion:latest`

### 3. Install on CasaOS

1. Open CasaOS Dashboard
2. Click **App Store** → **Custom Install** (top right)
3. Fill in the details:
   - **Docker Image:** `ghcr.io/bestsage/sith_mischung_combustion:latest`
   - **Container Name:** `rocket-studio`
   - **Network:** `bridge`
   - **Ports:**
     - `3000:3000` (Web UI)
     - `8000:8000` (Rust API)
     - `8001:8001` (CEA Service)
   - **Web UI Port:** `3000`

4. Click **Install**

### 4. Enable Auto-Updates with Watchtower

1. In CasaOS, go to **Custom Install**
2. Install Watchtower:
   - **Docker Image:** `containrrr/watchtower`
   - **Container Name:** `watchtower`
   - **Command:** `--interval 300` (checks every 5 minutes)
   - **Volumes:**
     - Host: `/var/run/docker.sock` → Container: `/var/run/docker.sock`

Now every push to GitHub will:
1. Trigger GitHub Actions
2. Build new Docker image
3. Push to ghcr.io
4. Watchtower detects the update
5. CasaOS restarts the container with new image

## Environment Variables (Optional)

You can configure these in CasaOS:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `3000` | Next.js port |
| `RUST_API_URL` | `http://localhost:8000` | Rust server URL |
| `CEA_SERVICE_URL` | `http://localhost:8001` | CEA service URL |

## Troubleshooting

- **Container won't start:** Check logs in CasaOS → Containers → rocket-studio → Logs
- **CEA not working:** RocketCEA requires specific Python version, check Python logs
- **No auto-update:** Verify Watchtower is running and has Docker socket mounted

## Manual Update

```bash
docker pull ghcr.io/YOUR_USERNAME/rocket-motor-design-plotter:latest
docker restart rocket-studio
```
