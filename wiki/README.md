# Wiki Documentation Structure

This directory contains the improved wiki documentation for SITH MISCHUNG COMBUSTION.

## 📁 Structure

The wiki is organized into 5 main parts:

### Part 1: Les Bases (Basics) - Beginner Level
- `1-Introduction.md` - Action-Reaction principle
- `2-Tuyere-de-Laval.md` - Supersonic nozzle
- `3-Probleme-Thermique.md` - Extreme temperatures
- `4-Refroidissement-Regeneratif.md` - Regenerative cooling

### Part 2: Théorie Avancée (Advanced Theory) - Engineer Level
- `5-Chimie-Combustion.md` - NASA CEA and combustion chemistry
- `6-Equation-Bartz.md` - Bartz equation for heat transfer
- `7-Canaux-Refroidissement.md` - Cooling channel design
- `8-Mecanique-Fluides.md` - Fluid mechanics and pressure drops

### Part 3: Science des Matériaux (Materials Science)
- `9-Criteres-Selection.md` - Material selection criteria
- `10-Base-Donnees-Materiaux.md` - Material properties database

### Part 4: Guide du Logiciel (Software Guide)
- `11-Utilisation-Optimiseur.md` - How to use the optimizer
- `12-Export-Fabrication.md` - CAD export and manufacturing

### Part 5: Documentation Technique (Technical Documentation)
- `13-Concepts-Fondamentaux.md` - Fundamental concepts
- `14-Transfert-Thermique.md` - Detailed thermal transfer theory
- `15-Modele-Bartz.md` - Complete Bartz model derivation
- `16-Temperatures-Paroi.md` - Wall temperature calculations
- `17-Correlations-Coolant.md` - Coolant-side correlations
- `18-Design-Canaux.md` - Channel design and dimensioning
- `19-Proprietes-Materiaux.md` - Detailed material properties
- `20-Proprietes-Coolants.md` - Coolant properties guide
- `21-Exemples-Calculs.md` - Complete calculation examples

## 🎨 Improvements Made

The new wiki features:

### Better Visual Structure
- ✅ Clean Markdown formatting with headers, tables, and lists
- ✅ Emoji icons for better visual hierarchy
- ✅ Code blocks for formulas and equations
- ✅ Professional tables for data presentation

### Enhanced Navigation
- ✅ Home page with complete table of contents
- ✅ Part overview pages with section summaries
- ✅ Navigation links at the bottom of each page
- ✅ Clear breadcrumbs (Home → Part → Section)

### Better Content Organization
- ✅ Logical progression from beginner to advanced
- ✅ Separate pages for each topic (not one huge file)
- ✅ Consistent formatting across all pages
- ✅ Clear learning objectives for each part

### Improved Readability
- ✅ Shorter paragraphs
- ✅ Bullet points and numbered lists
- ✅ Visual callouts (notes, warnings, tips)
- ✅ Example tables and calculations

## 🚀 Deployment

To deploy this wiki to GitHub Wiki:

```bash
./deploy-wiki.sh
```

This script will:
1. Clone the GitHub Wiki repository
2. Copy all markdown files
3. Commit and push to the wiki

## 📝 Maintenance

To add new pages:
1. Create a new `.md` file in the `/wiki` directory
2. Follow the existing naming convention
3. Add navigation links at the bottom
4. Update the relevant Part overview page
5. Update `Home.md` if needed
6. Run the deploy script

## 🔗 Original Content

The original content from `wiki.txt` has been preserved and reorganized into these Markdown files with improved formatting and structure.
