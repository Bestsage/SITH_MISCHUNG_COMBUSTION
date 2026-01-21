# Fonctionnalités Futures - Rocket Design Studio

Ce document décrit l'architecture prévue pour les fonctionnalités avancées du site.

## 1. Sync de Projets

### Description
Permettre aux utilisateurs de sauvegarder leurs configurations de moteurs (paramètres de combustion, refroidissement, géométrie) dans des "projets" persistants.

### Architecture Proposée
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Next.js API   │────▶│   Database      │
│   (React)       │     │   /api/projects │     │   (PostgreSQL)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Tables de Base de Données
- `projects` - id, user_id, name, description, created_at, updated_at
- `project_data` - id, project_id, type (combustion/cooling/cfd), data (JSON)
- `project_files` - id, project_id, filename, s3_key, created_at

---

## 2. Sauvegarde CFD

### Description
Sauvegarder les résultats de simulations OpenFOAM dans les projets utilisateur.

### Données Sauvegardées
- Paramètres d'entrée (géométrie, conditions aux limites)
- Résultats de simulation (champs de pression, température, vitesse)
- Visualisations générées (images, animations)
- Logs de simulation

---

## 3. Collaboration

### Description
Permettre à plusieurs utilisateurs de travailler sur le même projet.

### Fonctionnalités
- **Partage de projet**: Inviter des utilisateurs par email
- **Rôles**: Owner, Editor, Viewer
- **Historique**: Suivi des modifications par utilisateur
- **Commentaires**: Discussion sur les résultats

---

## 4. Site Fermé / Accès Restreint

### Description
Fermer l'accès public au site. Seuls les utilisateurs approuvés peuvent utiliser les fonctionnalités avancées.

### Modes d'Accès

#### Via Demande Admin (DM)
1. L'utilisateur se connecte (OAuth)
2. Il voit un message "Accès en attente"
3. Il envoie une demande avec justification
4. L'admin reçoit notification sur /admin
5. L'admin approuve/refuse
6. L'utilisateur reçoit email de confirmation

#### Via API Key
1. L'utilisateur demande une API key
2. L'admin génère une key avec permissions spécifiques
3. L'utilisateur utilise la key pour:
   - Accès programmatique aux calculs
   - Intégration dans pipelines CI/CD
   - Scripts de simulation batch

### Tables Additionnelles
- `access_requests` - id, user_id, status, message, reviewed_at, reviewed_by
- `api_keys` - id, user_id, key_hash, name, permissions, last_used, expires_at

---

## Priorisation Suggérée

1. **Phase 1** (actuel): Authentification de base ✅
2. **Phase 2**: Projets et sauvegarde de données
3. **Phase 3**: Sauvegarde CFD
4. **Phase 4**: Collaboration
5. **Phase 5**: Site fermé + API Keys
