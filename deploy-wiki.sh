#!/bin/bash
# Script pour déployer le wiki vers GitHub

set -e

echo "🚀 Script de déploiement du Wiki GitHub"
echo "========================================"
echo ""

# Vérifier que nous sommes dans le bon répertoire
if [ ! -d "wiki" ]; then
    echo "❌ Erreur: Le dossier wiki/ n'existe pas."
    echo "   Assurez-vous d'exécuter ce script depuis la racine du dépôt."
    exit 1
fi

# Récupérer les informations du dépôt
REPO_URL=$(git remote get-url origin)
WIKI_URL="${REPO_URL%.git}.wiki.git"

echo "📍 Dépôt source: $REPO_URL"
echo "📍 Wiki cible: $WIKI_URL"
echo ""

# Demander confirmation
read -p "Voulez-vous continuer le déploiement vers le wiki GitHub? (o/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Oo]$ ]]; then
    echo "❌ Déploiement annulé."
    exit 0
fi

# Créer un répertoire temporaire
TEMP_DIR=$(mktemp -d)
echo "📁 Répertoire temporaire: $TEMP_DIR"

# Cloner le wiki
echo "📥 Clonage du wiki..."
if git clone "$WIKI_URL" "$TEMP_DIR" 2>/dev/null; then
    echo "✅ Wiki cloné avec succès"
else
    echo "⚠️  Le wiki n'existe pas encore ou n'est pas accessible."
    echo "   Création d'un nouveau wiki..."
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
    git init
    git remote add origin "$WIKI_URL"
fi

# Copier les fichiers
echo "📋 Copie des fichiers wiki..."
cp -v wiki/*.md "$TEMP_DIR/"

# Commit et push
cd "$TEMP_DIR"
git add .
if git diff --staged --quiet; then
    echo "ℹ️  Aucun changement à committer."
else
    echo "💾 Commit des changements..."
    git commit -m "Import/mise à jour du wiki depuis le dépôt principal

- Guide complet d'analyse thermique des moteurs-fusées
- 11 pages avec navigation complète
- Tables des matières interactives
- Exemples de calcul et formules de référence
"
    
    echo "📤 Push vers GitHub..."
    git push -u origin master 2>/dev/null || git push -u origin main
    
    echo "✅ Wiki déployé avec succès!"
fi

# Nettoyer
cd -
rm -rf "$TEMP_DIR"

echo ""
echo "✨ Déploiement terminé!"
echo ""
echo "📖 Accédez à votre wiki ici:"
echo "   ${REPO_URL%.git}/wiki"
echo ""
echo "💡 Conseil: Activez le wiki dans Settings > Options > Features si ce n'est pas déjà fait."
