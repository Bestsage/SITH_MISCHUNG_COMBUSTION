# OpenFOAM CFD Integration

Solveur CFD haute-fidélité pour simulations d'écoulements compressibles dans les tuyères de fusée.

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   Rust Server    │────▶│  Docker         │
│   (Next.js)     │     │   (Port 8000)    │     │  OpenFOAM       │
│   Port 3000     │     │                  │     │  Port 8001      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                         │
                              ┌───────────────────────────┤
                              ▼                           ▼
                        ┌──────────┐              ┌──────────┐
                        │ OpenFOAM │              │ Python   │
                        │rhoCentral│              │ Fallback │
                        └──────────┘              └──────────┘
```

## 🔬 Solveur

### OpenFOAM (rhoCentralFoam)
- Écoulements compressibles haute vitesse
- Schéma central-upwind de Kurganov-Tadmor
- Excellent pour les chocs et détentes
- Maillage axisymétrique wedge

### Python Fallback
- Solution quasi-1D isentropic
- Corrections 2D
- Toujours disponible

## 🚀 Déploiement

### Docker (Recommandé)

```bash
cd openfoam-cfd
docker-compose up -d --build
```

Le conteneur démarre l'API FastAPI sur le port **8001**.

### Vérifier le status

```bash
curl http://localhost:8001/health
```

## 📡 API Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | Status du serveur |
| `/api/cfd/run` | POST | Lancer simulation (async) |
| `/api/cfd/solve` | POST | Simulation directe (sync) |
| `/api/cfd/status/{id}` | GET | Status d'un job |
| `/api/cfd/result/{id}` | GET | Résultats d'un job |
| `/api/cfd/jobs` | GET | Liste des jobs |

## 📋 Exemple d'utilisation

### Simulation asynchrone

```bash
# Lancer une simulation
curl -X POST http://localhost:8001/api/cfd/run \
  -H "Content-Type: application/json" \
  -d '{
    "r_throat": 0.025,
    "r_chamber": 0.05,
    "r_exit": 0.075,
    "l_chamber": 0.1,
    "l_nozzle": 0.2,
    "p_chamber": 5000000,
    "t_chamber": 3500,
    "gamma": 1.2,
    "molar_mass": 0.022,
    "nx": 150,
    "ny": 50
  }'

# Réponse: {"job_id":"abc12345","status":"pending",...}

# Vérifier le status
curl http://localhost:8001/api/cfd/status/abc12345

# Récupérer les résultats
curl http://localhost:8001/api/cfd/result/abc12345
```

### Simulation synchrone (rapide)

```bash
curl -X POST http://localhost:8001/api/cfd/solve \
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

## 🐳 Docker Compose

```yaml
version: '3.8'

services:
  openfoam-cfd:
    build: .
    container_name: sith-openfoam
    ports:
      - "8001:8001"
    volumes:
      - cfd-cases:/app/cases
      - cfd-results:/app/results
    environment:
      - NUM_PROCS=4
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
    restart: unless-stopped

volumes:
  cfd-cases:
  cfd-results:
```

## 📊 Format des résultats

```json
{
  "x": [...],           // Coordonnées axiales
  "r": [...],           // Coordonnées radiales
  "pressure": [...],    // Pression [Pa]
  "temperature": [...], // Température [K]
  "mach": [...],        // Nombre de Mach
  "velocity_x": [...],  // Vitesse axiale [m/s]
  "velocity_r": [...],  // Vitesse radiale [m/s]
  "density": [...],     // Densité [kg/m³]
  "nx": 150,
  "ny": 50,
  "converged": true,
  "iterations": 1000,
  "solver": "openfoam"
}
```

## 🔧 Configuration

| Variable | Description | Défaut |
|----------|-------------|--------|
| `NUM_PROCS` | Nombre de processus MPI | 4 |
| `CASES_DIR` | Dossier des cas | /app/cases |
| `RESULTS_DIR` | Dossier des résultats | /app/results |

## 📁 Fichiers

| Fichier | Description |
|---------|-------------|
| `Dockerfile` | Image OpenFOAM + FastAPI |
| `docker-compose.yml` | Stack Docker complet |
| `api/server.py` | API REST FastAPI |
| `scripts/python_cfd_solver.py` | Solveur Python fallback |

## 📈 Performance

| Configuration | Temps estimé |
|---------------|--------------|
| 100x50 cells (OpenFOAM) | ~30 sec |
| 100x50 cells (Python) | ~5 sec |
| 200x100 cells (OpenFOAM) | ~2 min |
| 500x200 cells (OpenFOAM) | ~10 min |

## 🔗 Références

- [OpenFOAM User Guide](https://www.openfoam.com/documentation/user-guide)
- [rhoCentralFoam](https://www.openfoam.com/documentation/guides/latest/doc/guide-applications-solvers-compressible-rhoCentralFoam.html)
