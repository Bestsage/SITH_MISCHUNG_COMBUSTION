# 💻 Partie 4 : Guide du Logiciel

> Utilisation pratique de SITH MISCHUNG COMBUSTION pour la conception et l'optimisation.

---

## 📑 Sections de cette Partie

### [11. Utilisation de l'Optimiseur](11-Utilisation-Optimiseur)
Comment configurer et lancer une optimisation automatique.
- Sélection des variables de design
- Définition des contraintes
- Choix de la fonction objectif
- Interprétation des résultats

### [12. Export & Fabrication](12-Export-Fabrication)
Préparer les fichiers pour la fabrication.
- Export des profils CAD (DXF, STEP, IGES)
- Génération de dessins techniques
- Liste des canaux et dimensions
- Considérations de fabrication

---

## 🎯 Objectifs d'Apprentissage

À la fin de cette partie, vous serez capable de :
- ✅ Configurer une optimisation multi-objectifs
- ✅ Définir des contraintes de design réalistes
- ✅ Interpréter les résultats d'optimisation
- ✅ Exporter les fichiers CAD pour la fabrication

---

## 🚀 Workflow Typique

### 1️⃣ Configuration Initiale
- Définir la géométrie de base (diamètres, longueurs)
- Choisir les propergols (LOX/RP-1, LOX/CH4, etc.)
- Définir les conditions de fonctionnement (P_c, ṁ, O/F)

### 2️⃣ Optimisation
- Sélectionner les variables libres (épaisseur paroi, nombre de canaux, etc.)
- Définir les contraintes (T_wall_max, σ_max, ΔP_coolant_max)
- Lancer l'optimisation
- Analyser le front de Pareto (si multi-objectifs)

### 3️⃣ Validation
- Vérifier les profils de température
- Vérifier les contraintes mécaniques
- Vérifier la faisabilité de fabrication

### 4️⃣ Export
- Générer les fichiers CAD
- Créer la documentation technique
- Préparer pour la fabrication

---

## 🎨 Interface Utilisateur

Le logiciel affiche plusieurs graphiques interactifs :

### Graphiques Principaux
1. **Profil de Température** (T_wall, T_gaz, T_coolant vs position)
2. **Profil de Flux Thermique** (q vs position)
3. **Géométrie de la Tuyère** (avec zones de refroidissement)
4. **Propriétés du Coolant** (P, T, v vs position)
5. **Contraintes Mécaniques** (σ_hoop, σ_thermal vs position)

### Panneaux de Contrôle
- Variables d'entrée (sliders/inputs)
- Contraintes (checkboxes avec limites)
- Résultats numériques (tableau)
- Statut d'optimisation

---

## 🔄 Navigation

- 🏠 [Retour à l'Accueil](Home)
- ⬅️ [Partie Précédente : Science des Matériaux](Partie-3-Materiaux)
- ➡️ [Commencer : Utilisation de l'Optimiseur](11-Utilisation-Optimiseur)
- ⏭️ [Partie Suivante : Documentation Technique](Partie-5-Documentation-Technique)
