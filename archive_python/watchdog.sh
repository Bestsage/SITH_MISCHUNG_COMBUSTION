#!/bin/bash

# Dossier du projet
PROJECT_DIR="/opt/SITH_MISCHUNG_COMBUSTION"
cd $PROJECT_DIR

# On récupère les dernières infos de GitHub sans fusionner
git fetch origin main

# On compare le commit local avec le commit distant
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse @{u})

if [ $LOCAL != $REMOTE ]; then
    echo "$(date): 🚀 Nouveau commit détecté ! Mise à jour en cours..."
    
    # On télécharge le code
    git pull origin main
    
    # On reconstruit l'image monolithique
    # On utilise 'docker compose' (version V2 sans le tiret)
    docker compose up -d --build
    
    echo "$(date): ✅ Déploiement terminé."
else
    echo "$(date): 😴 Rien de neuf sur GitHub."
fi