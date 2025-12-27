# 📚 Partie 5 : Documentation Technique Approfondie

> Analyses détaillées, formules complètes et exemples de calculs pour les ingénieurs.

---

## 📑 Sections de cette Partie

### Section A : Fondamentaux
- **[13. Introduction et Concepts Fondamentaux](13-Concepts-Fondamentaux)**
  - Pourquoi le refroidissement est critique
  - Différentes stratégies de refroidissement
  - Schéma du transfert thermique

### Section B : Modèles Thermiques
- **[14. Théorie Détaillée du Transfert Thermique](14-Transfert-Thermique)**
  - Équations fondamentales
  - Analogie électrique des résistances thermiques
  - Température adiabatique de paroi

- **[15. Modèle de Bartz pour h_g](15-Modele-Bartz)**
  - Dérivation complète de l'équation
  - Facteur de correction σ(x)
  - Limites et validité

- **[16. Calcul des Températures de Paroi](16-Temperatures-Paroi)**
  - Méthode de résolution itérative
  - Distribution spatiale T(x)
  - Zones critiques

### Section C : Coolant et Canaux
- **[17. Corrélations Côté Coolant](17-Correlations-Coolant)**
  - Nombre de Nusselt (Dittus-Boelter, Gnielinski)
  - Régimes d'écoulement
  - Facteurs de correction

- **[18. Design et Dimensionnement des Canaux](18-Design-Canaux)**
  - Géométries (rectangulaires, trapézoïdaux, circulaires)
  - Optimisation du nombre de canaux
  - Compromis performance/fabrication

### Section D : Propriétés des Matériaux
- **[19. Propriétés des Matériaux pour Moteurs-Fusées](19-Proprietes-Materiaux)**
  - Tables complètes (k, Cp, ρ, α vs T)
  - Dépendance en température
  - Sources et références

- **[20. Propriétés des Coolants](20-Proprietes-Coolants)**
  - RP-1, Méthane, Hydrogène, Éthanol
  - Propriétés thermophysiques
  - Risques (cokéfaction, ébullition)

### Section E : Applications
- **[21. Exemples de Calcul Complets](21-Exemples-Calculs)**
  - Moteur LOX/RP-1 (50 kN)
  - Moteur LOX/CH4 (100 kN)
  - Validation des résultats

---

## 🎯 Pour qui est cette partie ?

Cette section s'adresse aux :
- 🎓 **Étudiants en ingénierie aérospatiale** (niveau Master/Doctorat)
- 👨‍🔬 **Ingénieurs R&D** en propulsion spatiale
- 🔬 **Chercheurs** travaillant sur les moteurs-fusées
- 📖 **Autodidactes avancés** avec bases solides en thermodynamique

---

## 📐 Niveau de Détail

Cette partie contient :
- ✅ **Dérivations mathématiques complètes**
- ✅ **Tables de propriétés détaillées**
- ✅ **Exemples numériques avec toutes les étapes**
- ✅ **Références bibliographiques**
- ✅ **Formules dans le système SI avec unités**

---

## 🔬 Contenu Technique

### Équations Principales Couvertes

1. **Conservation de l'énergie**
   ```
   q = h_g × (T_aw - T_wh) = k/e × (T_wh - T_wc) = h_c × (T_wc - T_cool)
   ```

2. **Bartz (forme complète)**
   ```
   h_g = [(0.026/D_t^0.2) × (μ^0.2×Cp/Pr^0.6) × (P_c/c*)^0.8] × σ(x)
   ```

3. **Nusselt côté coolant**
   ```
   Nu = 0.023 × Re^0.8 × Pr^0.4  (Dittus-Boelter)
   ```

4. **Contraintes mécaniques**
   ```
   σ_hoop = P × R / e
   σ_thermal = E × α × ΔT / (2(1-ν))
   ```

---

## 📊 Format des Données

Les tables de propriétés sont présentées sous forme de tableaux Markdown clairs avec :
- Températures de référence
- Valeurs numériques précises
- Sources des données
- Incertitudes typiques

---

## 🔄 Navigation

- 🏠 [Retour à l'Accueil](Home)
- ⬅️ [Partie Précédente : Guide du Logiciel](Partie-4-Guide-Logiciel)
- ➡️ [Commencer : Concepts Fondamentaux](13-Concepts-Fondamentaux)

---

## 📚 Note sur les Références

Cette documentation s'appuie sur :
- Publications NASA (NASA SP-8087, etc.)
- Textbooks de référence (Huzel & Huang, Sutton)
- Articles de recherche peer-reviewed
- Données expérimentales validées
