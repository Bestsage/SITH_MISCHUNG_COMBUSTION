# 🚀 SITH Mischung Combustion - Rocket Motor Design Suite

Application complète de conception de moteurs-fusées avec solveur CFD avancé, déployable sur Proxmox/Docker.

## 📋 Table des Matières

- [Architecture](#architecture)
- [Ports & Services](#ports--services)
- [Déploiement Proxmox](#déploiement-proxmox)
- [Déploiement Local (Dev)](#déploiement-local-dev)
- [Solveur CFD](#solveur-cfd)
- [API Endpoints](#api-endpoints)
- [Dépannage](#dépannage)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PROXMOX SERVER                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    DOCKER COMPOSE STACK                                 │ │
│  │                                                                         │ │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │ │
│  │  │   FRONTEND       │  │   RUST SERVER    │  │   CFD SOLVER         │  │ │
│  │  │   Next.js        │  │   Axum           │  │   OpenFOAM           │  │ │
│  │  │   Port: 3000     │  │   Port: 8000     │  │   rhoCentralFoam     │  │ │
│  │  │                  │  │                  │  │   Port: 8001         │  │ │
│  │  │  • React 18      │  │  • API REST      │  │                      │  │ │
│  │  │  • TailwindCSS   │  │  • SSE Progress  │  │  • Compressible      │  │ │
│  │  │  • Recharts      │  │  • CFD Solver    │  │  • Shock Capture     │  │ │
│  │  │  • 3D Viewer     │  │  • Thermal       │  │  • Python Fallback   │  │ │
│  │  └────────┬─────────┘  └────────┬─────────┘  └──────────┬───────────┘  │ │
│  │           │                     │                       │              │ │
│  │           └─────────────────────┴───────────────────────┘              │ │
│  │                            Docker Network                               │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🌐 Ports & Services

| Service | Port | Description | Conteneur |
|---------|------|-------------|-----------|
| **Frontend** | `3000` | Interface utilisateur Next.js | `sith-frontend` |
| **Backend API** | `8000` | Serveur Rust (Axum) - API principale | `sith-backend` |
| **CFD Solver** | `8001` | Solveur CFD OpenFOAM (rhoCentralFoam) | `sith-openfoam` |

### URLs d'accès depuis le réseau

```
http://<IP_PROXMOX>:3000    # Interface Web
http://<IP_PROXMOX>:8000    # API REST
http://<IP_PROXMOX>:8001    # CFD Solver API (interne)
```

---

## 🖥️ Déploiement Proxmox

### Prérequis sur Proxmox

1. **VM ou LXC avec Docker installé**
   ```bash
   # Sur Debian/Ubuntu
   apt update && apt install -y docker.io docker-compose
   systemctl enable docker
   systemctl start docker
   ```

2. **Ressources recommandées**
   - CPU: 4+ cores (8 recommandés pour CFD)
   - RAM: 8 GB minimum (16 GB recommandés)
   - Stockage: 20 GB SSD

### Étape 1 : Cloner le Repository

```bash
cd /opt
git clone https://github.com/votre-repo/SITH_MISCHUNG_COMBUSTION.git
cd SITH_MISCHUNG_COMBUSTION
```

### Étape 2 : Créer le docker-compose.yml principal

Créez `/opt/SITH_MISCHUNG_COMBUSTION/docker-compose.yml`:

```yaml
version: '3.8'

services:
  # =============================================
  # FRONTEND - Next.js (Port 3000)
  # =============================================
  frontend:
    container_name: sith-frontend
    build:
      context: ./web
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    networks:
      - sith-network
    restart: unless-stopped

  # =============================================
  # BACKEND - Rust Axum Server (Port 8000)
  # =============================================
  backend:
    container_name: sith-backend
    build:
      context: ./rocket_server
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - CFD_API_URL=http://cfd-solver:8001
      - RUST_LOG=info
    depends_on:
      - cfd-solver
    networks:
      - sith-network
    restart: unless-stopped

  # =============================================
  # CFD SOLVER - OpenFOAM rhoCentralFoam (Port 8001)
  # =============================================
  openfoam-cfd:
    container_name: sith-openfoam
    build:
      context: ./openfoam-cfd
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    volumes:
      - cfd-cases:/app/cases
      - cfd-results:/app/results
    environment:
      - NUM_PROCS=4
      - PYTHONUNBUFFERED=1
    networks:
      - sith-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G

networks:
  sith-network:
    driver: bridge

volumes:
  cfd-cases:
  cfd-results:
```

### Étape 3 : Créer les Dockerfiles manquants

#### 3.1 Dockerfile Frontend (`web/Dockerfile`)

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
```

#### 3.2 Dockerfile Backend (`rocket_server/Dockerfile`)

```dockerfile
FROM rust:1.75-bookworm AS builder

WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /app/target/release/rocket_server .

EXPOSE 8000
ENV RUST_LOG=info
CMD ["./rocket_server"]
```

### Étape 4 : Lancer le Stack

```bash
# Depuis /opt/SITH_MISCHUNG_COMBUSTION
docker-compose up -d --build

# Vérifier les logs
docker-compose logs -f

# Vérifier le status
docker-compose ps
```

### Étape 5 : Configurer le Firewall Proxmox

```bash
# Sur le host Proxmox, ouvrir les ports
iptables -A INPUT -p tcp --dport 3000 -j ACCEPT
iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
iptables -A INPUT -p tcp --dport 8001 -j ACCEPT

# Ou via pve-firewall si activé
```

### Étape 6 : Accéder à l'Application

Depuis votre navigateur:
```
http://<IP_PROXMOX>:3000
```

---

## 💻 Déploiement Local (Dev)

### Prérequis

1. **Rust** (1.70+): https://rustup.rs/
2. **Node.js** (18+): https://nodejs.org/
3. **Python** (3.10+): https://python.org/

### Installation Rapide

```powershell
# 1. Cloner
git clone <repo>
cd SITH_MISCHUNG_COMBUSTION

# 2. Backend Rust
cd rocket_server
cargo build --release
cd ..

# 3. Frontend
cd web
npm install
cd ..
```

### Lancement (3 terminaux)

```powershell
# Terminal 1 - CFD Service (OpenFOAM Docker ou Python)
cd openfoam-cfd && docker-compose up -d
# Ou sans Docker:
python openfoam-cfd/api/server.py

# Terminal 2 - Backend Rust
cd rocket_server; cargo run --release

# Terminal 3 - Frontend
cd web; npm run dev
```

---

## 🔬 Solveur CFD

Le système CFD utilise une architecture en cascade:

```
Requête CFD → OpenFOAM (rhoCentralFoam)
               ↓ (si indisponible)
             Python Quasi-1D (fallback)
```

### Caractéristiques

- **Solveur principal**: OpenFOAM rhoCentralFoam
- **Méthode**: Central-upwind Kurganov-Tadmor
- **Maillage**: Axisymétrique wedge
- **Fallback**: Python quasi-1D + corrections 2D
- **Formats de sortie**: JSON

### Appel API CFD

```bash
curl -X POST http://localhost:8001/api/cfd/run \
  -H "Content-Type: application/json" \
  -d '{
    "r_throat": 0.025,
    "r_exit": 0.075,
    "p_chamber": 5000000,
    "t_chamber": 3500,
    "gamma": 1.2,
    "molar_mass": 0.022
  }'
```

---

## 📡 API Endpoints

### Backend Rust (Port 8000)

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Health check |
| `/api/materials` | GET | Liste des matériaux |
| `/api/cea/calculate` | POST | Calculs thermochimiques CEA |
| `/api/geometry/generate` | POST | Génération géométrie tuyère |
| `/api/cfd/solve` | POST | Solveur CFD intégré + SSE progress |
| `/api/cfd/external` | POST | Appel solveur CFD externe (Docker) |
| `/api/calculate/full` | POST | Calcul complet moteur |

### CFD Solver (Port 8001)

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | Health check |
| `/api/cfd/run` | POST | Lancer simulation CFD |
| `/api/cfd/status/{job_id}` | GET | Status d'un job |
| `/api/cfd/result/{job_id}` | GET | Résultats d'un job |

---

## 🔧 Commandes Docker Utiles

```bash
# Voir les logs en temps réel
docker-compose logs -f sith-backend

# Redémarrer un service
docker-compose restart sith-cfd

# Reconstruire un service spécifique
docker-compose up -d --build sith-backend

# Entrer dans un conteneur
docker exec -it sith-cfd /bin/bash

# Nettoyer tout
docker-compose down -v
docker system prune -a

# Stats ressources
docker stats
```

---

## 🔍 Dépannage

### Container ne démarre pas

```bash
# Voir les logs détaillés
docker-compose logs sith-backend

# Vérifier le build
docker-compose build --no-cache sith-backend
```

### Port déjà utilisé

```bash
# Trouver le processus
netstat -tulpn | grep 8000
# ou sur Windows
netstat -ano | findstr 8000

# Arrêter le processus
kill <PID>  # Linux
taskkill /PID <PID> /F  # Windows
```

### CFD Solver ne répond pas

```bash
# Vérifier le health
curl http://localhost:8001/health

# Redémarrer le solver
docker-compose restart sith-cfd
```

### Erreur mémoire CFD

```bash
# Augmenter les limites dans docker-compose.yml
deploy:
  resources:
    limits:
      memory: 16G
```

---

## 📊 Monitoring (Optionnel)

Ajouter Prometheus + Grafana au stack:

```yaml
# Ajouter à docker-compose.yml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    networks:
      - sith-network

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    networks:
      - sith-network
```

---

## 📝 Variables d'Environnement

| Variable | Service | Description | Défaut |
|----------|---------|-------------|--------|
| `CFD_API_URL` | backend | URL du solveur CFD | `http://cfd-solver:8001` |
| `RUST_LOG` | backend | Niveau de log | `info` |
| `OMP_NUM_THREADS` | cfd-solver | Threads OpenMP | `4` |
| `MPI_PROCESSES` | cfd-solver | Processus MPI | `4` |
| `NEXT_PUBLIC_API_URL` | frontend | URL API backend | `http://backend:8000` |

---

## 📄 Licence

MIT License

---

## 🤝 Support

Pour questions ou bugs, ouvrir une issue sur GitHub.
