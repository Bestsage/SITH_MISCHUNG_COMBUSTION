# 🚀 Rocket Motor Design Plotter v2.0

Application moderne de conception de moteurs-fusées avec architecture Rust + Next.js.

## 📋 Table des Matières

- [Prérequis](#prérequis)
- [Installation](#installation)
- [Compilation](#compilation)
- [Lancement](#lancement)
- [Architecture](#architecture)
- [Utilisation](#utilisation)
- [Dépannage](#dépannage)

---

## 🔧 Prérequis

### Obligatoires

1. **Rust** (stable, 1.70+)
   - Télécharger: https://rustup.rs/
   - Vérifier: `rustc --version`

2. **Python 3.10+**
   - Télécharger: https://www.python.org/downloads/
   - Vérifier: `py -3.10 --version`

3. **Node.js 18+** et **npm**
   - Télécharger: https://nodejs.org/
   - Vérifier: `node --version` et `npm --version`

4. **Git**
   - Télécharger: https://git-scm.com/
   - Vérifier: `git --version`

### Optionnels (pour développement)

- **MSYS2** (Windows uniquement, pour compilation Fortran)
- **Visual Studio Build Tools** (Windows)

---

## 📦 Installation

### 1. Cloner le Repository

```bash
git clone https://github.com/votre-repo/Rocket-Motor-Design-Plotter.git
cd Rocket-Motor-Design-Plotter
```

### 2. Installer les Dépendances Python

```bash
# Créer un environnement virtuel (recommandé)
py -3.10 -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Installer les packages
pip install fastapi uvicorn pydantic numpy rocketcea
```

### 3. Installer les Dépendances Node.js

```bash
cd web
npm install
cd ..
```

### 4. Compiler le Core Rust (rocket_core)

```bash
cd rocket_core

# Définir la variable d'environnement pour PyO3
set PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1  # Windows CMD
# export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1  # Linux/Mac

# Compiler avec maturin
pip install maturin
maturin develop --release

cd ..
```

### 5. Compiler le Serveur Rust (rocket_server)

```bash
cd rocket_server
cargo build --release
cd ..
```

---

## 🔨 Compilation

### Compilation Complète (Tout Recompiler)

```bash
# 1. Core Rust (PyO3)
cd rocket_core
set PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
maturin develop --release
cd ..

# 2. Serveur Rust
cd rocket_server
cargo build --release
cd ..

# 3. Frontend Next.js
cd web
npm run build
cd ..
```

### Compilation Rapide (Développement)

```bash
# Core Rust (mode debug)
cd rocket_core
maturin develop
cd ..

# Serveur Rust (mode debug)
cd rocket_server
cargo build
cd ..

# Frontend (pas de build nécessaire en dev)
```

---

## 🚀 Lancement

### Méthode Recommandée : 3 Terminaux

#### Terminal 1 : Service CEA (Python)

```bash
# Depuis la racine du projet
py -3.10 cea_service.py
```

**Sortie attendue:**
```
🔬 CEA Microservice starting on port 8001...
INFO:     Uvicorn running on http://0.0.0.0:8001
```

#### Terminal 2 : Serveur Rust

```bash
# Depuis la racine du projet
cd rocket_server
cargo run --release
```

**Sortie attendue:**
```
🚀 Rust Server listening on http://0.0.0.0:8000
```

#### Terminal 3 : Frontend Next.js

```bash
# Depuis la racine du projet
cd web
npm run dev
```

**Sortie attendue:**
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
```

### Accès à l'Application

Ouvrez votre navigateur et allez sur:
```
http://localhost:3000
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                   │
│                   http://localhost:3000                 │
│  • React + TypeScript                                   │
│  • TailwindCSS                                          │
│  • Recharts (graphiques)                                │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP REST API
┌────────────────────▼────────────────────────────────────┐
│              SERVEUR RUST (Axum)                        │
│              http://localhost:8000                      │
│  • /api/materials - Base de données matériaux          │
│  • /api/cea/calculate - Proxy vers CEA                 │
│  • /api/geometry/generate - Génération géométrie       │
│  • /api/solve - Solveur thermique                      │
│  • /api/calculate/full - Calcul complet                │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼──────────┐    ┌────────▼─────────┐
│  ROCKET_CORE     │    │  CEA SERVICE     │
│  (Rust + PyO3)   │    │  (Python)        │
│  • Solveur       │    │  Port 8001       │
│  • Optimiseur    │    │  • RocketCEA     │
│  • Math          │    │  • FastAPI       │
└──────────────────┘    └──────────────────┘
```

### Ports Utilisés

- **3000** : Frontend Next.js
- **8000** : Serveur Rust (API principale)
- **8001** : Service CEA Python

---

## 📖 Utilisation

### 1. Charger les Matériaux

Cliquez sur **"📦 Charger Matériaux"** pour charger la base de données de 18+ matériaux.

### 2. Configurer le Moteur

Remplissez les paramètres dans la sidebar gauche:
- **Nom du moteur**
- **Propergols** (Oxydant, Carburant, O/F ratio)
- **Chambre** (Pc, débit, L*, contraction ratio)
- **Tuyère** (Pe, angles)
- **Matériau** (sélection automatique des propriétés)

### 3. Calculer

Cliquez sur **"🔥 CALCULER TOUT"** pour lancer:
1. Calculs NASA CEA
2. Génération de la géométrie
3. Analyse thermique
4. Calculs de performance

### 4. Consulter les Résultats

Le résumé affiche:
- **Performance** : Isp, Poussée, c*, T chambre
- **Géométrie** : Rayons, longueurs, expansion ratio
- **Thermique** : Flux, températures, ΔP
- **CEA** : γ, MW, CF

---

## 🔍 Dépannage

### Erreur : "Module rocket_core not found"

**Solution:**
```bash
cd rocket_core
set PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
maturin develop --release
```

### Erreur : "CEA Service not responding"

**Vérifications:**
1. Le service CEA est-il lancé ? (`py -3.10 cea_service.py`)
2. Port 8001 disponible ? (`netstat -an | findstr 8001`)
3. RocketCEA installé ? (`pip show rocketcea`)

### Erreur : "Rust Server failed to start"

**Vérifications:**
1. Port 8000 disponible ?
2. Compilation réussie ? (`cargo build --release`)
3. Dépendances à jour ? (`cargo update`)

### Erreur : "Frontend build failed"

**Solutions:**
```bash
cd web
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Performance Lente

**Optimisations:**
1. Utiliser `--release` pour Rust : `cargo run --release`
2. Compiler rocket_core en release : `maturin develop --release`
3. Fermer les autres applications

### Erreur Python "No module named 'rocketcea'"

**Solution:**
```bash
pip install rocketcea
# Si erreur de compilation, installer les wheels pré-compilés
pip install --upgrade rocketcea
```

---

## 🛠️ Développement

### Structure du Projet

```
Rocket-Motor-Design-Plotter/
├── rocket_core/          # Core Rust (PyO3)
│   ├── src/
│   │   ├── lib.rs
│   │   ├── solver.rs
│   │   ├── optimizer.rs
│   │   └── math.rs
│   └── Cargo.toml
├── rocket_server/        # Serveur Web Rust
│   ├── src/
│   │   ├── main.rs
│   │   ├── materials.rs
│   │   ├── cea_client.rs
│   │   ├── geometry.rs
│   │   └── motor_definition.rs
│   └── Cargo.toml
├── web/                  # Frontend Next.js
│   ├── app/
│   │   └── page.tsx
│   ├── components/
│   └── package.json
├── cea_service.py        # Micro-service CEA
└── README.md
```

### Commandes Utiles

```bash
# Tester le serveur Rust
curl http://localhost:8000/

# Tester CEA
curl -X POST http://localhost:8001/cea -H "Content-Type: application/json" -d '{"fuel":"RP-1","oxidizer":"LOX","of_ratio":2.5,"pc":50,"expansion_ratio":40}'

# Linter Rust
cargo clippy

# Formater Rust
cargo fmt

# Tests Rust
cargo test

# Linter Frontend
cd web && npm run lint
```

---

## 📝 Notes

- **Python minimal** : Seul le service CEA utilise Python (RocketCEA)
- **Performance** : Le core Rust est ~100x plus rapide que Python
- **Compatibilité** : Testé sur Windows 10/11, devrait fonctionner sur Linux/Mac

---

## 📄 Licence

MIT License - Voir LICENSE pour détails

---

## 🤝 Contribution

Les contributions sont bienvenues ! Ouvrez une issue ou un PR.

---

## 📧 Contact

Pour questions ou support, ouvrez une issue sur GitHub.
