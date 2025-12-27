# Guide d'utilisation du Wiki

Ce dossier contient la documentation complète sur l'analyse thermique des moteurs-fusées, organisée en pages wiki.

## 📋 Structure du Wiki

Le contenu est organisé en 11 pages principales:

1. **[Home.md](Home.md)** - Page d'accueil avec table des matières complète
2. **[1-Introduction-et-Concepts-Fondamentaux.md](1-Introduction-et-Concepts-Fondamentaux.md)** - Introduction et concepts de base
3. **[2-Theorie-Detaillee-du-Transfert-Thermique.md](2-Theorie-Detaillee-du-Transfert-Thermique.md)** - Théorie détaillée
4. **[3-Modele-de-Bartz.md](3-Modele-de-Bartz.md)** - Modèle de Bartz pour h_g
5. **[4-Calcul-des-Temperatures-de-Paroi.md](4-Calcul-des-Temperatures-de-Paroi.md)** - Calcul des températures
6. **[5-Design-et-Dimensionnement.md](5-Design-et-Dimensionnement.md)** - Design et dimensionnement (sections 5-8)
7. **[9-Exemples-de-Calcul.md](9-Exemples-de-Calcul.md)** - Exemples de calcul complets
8. **[10-Formules-Rapides.md](10-Formules-Rapides.md)** - Aide-mémoire des formules
9. **[11-14-Analyses-Avancees.md](11-14-Analyses-Avancees.md)** - Analyses avancées (sections 11-14)
10. **[15-Simulation-Transitoire.md](15-Simulation-Transitoire.md)** - Simulation transitoire
11. **[References.md](References.md)** - Références bibliographiques

## 🚀 Comment utiliser ces fichiers

### Option 1: Copier vers le Wiki GitHub (Recommandé)

Pour activer le wiki GitHub de ce dépôt:

1. Allez dans les **Settings** du dépôt
2. Activez la section **Wiki** 
3. Clonez le wiki repository:
   ```bash
   git clone https://github.com/Bestsage/SITH_MISCHUNG_COMBUSTION.wiki.git
   ```
4. Copiez tous les fichiers .md de ce dossier dans le wiki cloné:
   ```bash
   cp wiki/*.md SITH_MISCHUNG_COMBUSTION.wiki/
   cd SITH_MISCHUNG_COMBUSTION.wiki
   git add .
   git commit -m "Import wiki from wiki.txt"
   git push
   ```

### Option 2: Utiliser comme documentation dans le dépôt

Ces fichiers peuvent également servir de documentation directement dans le dépôt principal. GitHub affichera automatiquement le contenu markdown formaté.

### Option 3: Générer un site de documentation

Utilisez un générateur de site statique comme MkDocs ou Jekyll:

```bash
# Exemple avec MkDocs
pip install mkdocs
mkdocs new docs
# Copiez les fichiers dans docs/
mkdocs serve
```

## 📖 Navigation

Chaque page contient:
- Une **table des matières** locale pour naviguer dans les sections
- Des **liens de navigation** vers la page précédente et suivante
- Un **lien de retour** vers la page d'accueil (Home.md)

## ✨ Fonctionnalités

- ✅ Tables des matières interactives avec ancres
- ✅ Navigation entre les pages
- ✅ Tableaux formatés
- ✅ Code et formules mathématiques
- ✅ Diagrammes ASCII art
- ✅ Organisation logique et progressive

## 📝 Note sur le contenu

Ce guide couvre:
- Les fondements théoriques du transfert thermique
- Les équations de Bartz et autres corrélations
- Le dimensionnement des canaux de refroidissement
- Des exemples de calcul détaillés
- Les formules rapides pour l'estimation
- Les analyses avancées (2D/3D, CAD, optimisation)
- La simulation transitoire

Le contenu est basé sur le fichier `wiki.txt` original et a été organisé pour une meilleure navigation et utilisation dans un wiki GitHub.
