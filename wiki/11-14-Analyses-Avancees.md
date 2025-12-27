# 11-14. ANALYSES AVANCÉES

[← Section précédente : Formules](10-Formules-Rapides.md) | [Retour à l'accueil](Home.md) | [Section suivante : Simulation Transitoire →](15-Simulation-Transitoire.md)

---

## Table des matières
- [11. Carte thermique et analyse 2D/3D](#11-carte-thermique-et-analyse-2d3d)
  - [11.1 Effet d'ailette (fin effect)](#111-effet-dailette-fin-effect)
  - [11.2 Interpolation thermique 2D](#112-interpolation-thermique-2d)
  - [11.3 Visualisations disponibles](#113-visualisations-disponibles)
- [12. Export CAD et géométrie](#12-export-cad-et-géométrie)
  - [12.1 Génération du profil (Laval)](#121-génération-du-profil-laval)
  - [12.2 Modélisation des canaux](#122-modélisation-des-canaux)
  - [12.3 Formats d'export](#123-formats-dexport)
- [13. Optimisation automatique (algorithme)](#13-optimisation-automatique-algorithme)
  - [13.1 Fonction objectif (cost function)](#131-fonction-objectif-cost-function)
  - [13.2 Variables de décision (x)](#132-variables-de-décision-x)
  - [13.3 Contraintes (constraints)](#133-contraintes-constraints)
  - [13.4 Algorithme SLSQP](#134-algorithme-slsqp)
- [14. Analyse des contraintes mécaniques](#14-analyse-des-contraintes-mécaniques)
  - [14.1 Contraintes primaires (pression)](#141-contraintes-primaires-pression)
  - [14.2 Contraintes thermiques (secondaires)](#142-contraintes-thermiques-secondaires)
  - [14.3 Critère de von Mises](#143-critère-de-von-mises)
  - [14.4 Fatigue oligocyclique (LCF)](#144-fatigue-oligocyclique-lcf)

---


11. CARTE THERMIQUE ET ANALYSE 2D/3D
═══════════════════════════════════════════════════════════════

L'analyse thermique 1D (Bartz + Dittus-Boelter) donne une moyenne.
L'onglet "Heatmap" permet d'affiner cette analyse en visualisant
les gradients locaux, notamment entre les canaux de refroidissement.

11.1 EFFET D'AILETTE (FIN EFFECT)
───────────────────────────────────────────────────────────────
Dans un moteur à canaux fraisés, la "nervure" (rib) entre deux
canaux agit comme une ailette de refroidissement.

EFFICACITÉ DE L'AILETTE (η_fin):
  ┌─────────────────────────────────────────────────────────┐
  │ η_fin = tanh(m × H) / (m × H)                          │
  │                                                         │
  │ où: m = sqrt(2 × h_c / (k × w_rib))                    │
  │     H = hauteur du canal                                │
  │     w_rib = largeur de la nervure                       │
  └─────────────────────────────────────────────────────────┘

CONSÉQUENCE:
  - Le sommet de la nervure (côté chaud) est plus chaud que
    le fond du canal.
  - Si la nervure est trop fine ou trop haute, le sommet peut
    fondre même si le calcul 1D semble correct.

11.2 INTERPOLATION THERMIQUE 2D
───────────────────────────────────────────────────────────────
Le logiciel génère une carte de température T(x,y) en résolvant
l'équation de la chaleur simplifiée sur la surface développée.

MODÈLE:
  T_paroi(θ) = T_base + ΔT_rib × cos(N_canaux × θ)

  - T_base: Température au-dessus du canal (zone la mieux refroidie)
  - T_peak: Température entre deux canaux (zone la plus chaude)
  - ΔT_rib: Gradient thermique latéral

CRITÈRE DE CONCEPTION:
  Il faut vérifier que T_peak < T_limite_matériau.
  Le calcul 1D donne souvent une valeur entre T_base et T_peak.

11.3 VISUALISATIONS DISPONIBLES
───────────────────────────────────────────────────────────────
A) VUE EN COUPE RADIALE (Cross-Section):
   Montre la distribution T dans l'épaisseur de la paroi.
   Permet de voir le gradient radial (T_hot vers T_cold).

B) VUE DÉVELOPPÉE (Unrolled Surface):
   "Déroule" le cylindre/cône du moteur à plat.
   - Axe X: Position axiale (z)
   - Axe Y: Position circonférentielle (θ)
   - Couleur: Température locale

   Permet d'identifier les "Hot Spots" thermiques situés
   généralement au col et ENTRE les canaux.

C) SURFACE 3D:
   Projection de la carte thermique sur la géométrie réelle.
   Utile pour vérifier la continuité du refroidissement.


12. EXPORT CAD ET GÉOMÉTRIE
═══════════════════════════════════════════════════════════════

L'onglet "CAD" génère la géométrie solide du moteur pour la
fabrication (CAM) ou l'intégration (CAD).

12.1 GÉNÉRATION DU PROFIL (LAVAL)
───────────────────────────────────────────────────────────────
Le profil interne est généré par des courbes mathématiques:

1. CONVERGENT:
   - Arc de cercle ou courbe cubique
   - Angle d'entrée (typiquement 30-45°)
   - Rayon de courbure amont (R1 = 1.5 × Rt)

2. COL (THROAT):
   - Arc de cercle
   - Rayon de courbure aval (R2 = 0.382 × Rt)

3. DIVERGENT:
   - Parabole (Méthode de Rao approximée) ou Conique
   - Angle initial (θ_n) et angle de sortie (θ_e)
   - L = (R_e - R_t) / tan(θ_moyen)

12.2 MODÉLISATION DES CANAUX
───────────────────────────────────────────────────────────────
Les canaux sont générés par soustraction booléenne:
  Volume_Final = Volume_Paroi - Σ(Volume_Canaux)

GÉOMÉTRIE DES CANAUX:
  - Section rectangulaire variable
  - Profondeur (d) et largeur (w) évoluent le long de l'axe Z
  - Suivent la courbure de la tuyère (conformal cooling)

12.3 FORMATS D'EXPORT
───────────────────────────────────────────────────────────────
A) STEP (.stp / .step) - RECOMMANDÉ:
   - Format vectoriel standard ISO 10303
   - Géométrie exacte (NURBS)
   - Compatible: SolidWorks, Fusion 360, CATIA, FreeCAD
   - Idéal pour l'usinage CNC 5 axes

B) STL (.stl):
   - Maillage triangulaire
   - Résolution dépend du paramètre "Mesh Resolution"
   - Idéal pour l'impression 3D (Slicers: Cura, PrusaSlicer)
   - Difficile à modifier en CAD

C) DXF (.dxf):
   - Profil 2D (coupe longitudinale)
   - Utile pour le tournage (Lathe) ou la découpe jet d'eau


13. OPTIMISATION AUTOMATIQUE (ALGORITHME)
═══════════════════════════════════════════════════════════════

L'optimiseur cherche la "meilleure" configuration de refroidissement
sans intervention manuelle, en résolvant un problème mathématique.

13.1 FONCTION OBJECTIF (COST FUNCTION)
───────────────────────────────────────────────────────────────
On cherche à minimiser une fonction de coût J(x):

  J(x) = w_M × (Masse/M_ref) + w_P × (ΔP/P_ref) + w_T × Penalté_T

  Où:
  - Masse: Masse totale du moteur (cuivre + liner)
  - ΔP: Perte de charge totale dans les canaux
  - Penalté_T: Augmente exponentiellement si T_paroi > T_cible

  Les poids (w) sont ajustables:
  - "Masse Min": w_M élevé
  - "Performance": w_P élevé (minimiser perte de charge)
  - "Sécurité": w_T élevé (maximiser marge thermique)

13.2 VARIABLES DE DÉCISION (x)
───────────────────────────────────────────────────────────────
L'algorithme modifie itérativement:
  1. Nombre de canaux (N)
  2. Largeur des canaux (w)
  3. Profondeur des canaux (d)
  4. Épaisseur de paroi côté gaz (e_wg)

13.3 CONTRAINTES (CONSTRAINTS)
───────────────────────────────────────────────────────────────
Le design doit respecter:
  g1(x): T_wall_hot < T_max_matériau (ex: 900K pour Cu)
  g2(x): ΔP < ΔP_max_disponible (ex: 20% de Pc)
  g3(x): e_wg > e_min_fabrication (ex: 0.8 mm)
  g4(x): w_rib > w_min_fabrication (ex: 1.0 mm)

13.4 ALGORITHME SLSQP
───────────────────────────────────────────────────────────────
Utilise "Sequential Least Squares Programming" (SciPy):
  1. Calcule le gradient de J(x)
  2. Projette vers la direction de descente
  3. Vérifie les contraintes
  4. Converge quand J(x) ne diminue plus

RÉSULTAT:
  L'optimiseur trouve souvent des solutions non-intuitives,
  comme des canaux très profonds et fins au col (haute efficacité)
  et larges dans le divergent (faible perte de charge).


14. ANALYSE DES CONTRAINTES MÉCANIQUES
═══════════════════════════════════════════════════════════════

La paroi du moteur subit des charges extrêmes combinant pression
et dilatation thermique.

14.1 CONTRAINTES PRIMAIRES (PRESSION)
───────────────────────────────────────────────────────────────
Modèle du tube à paroi mince (Thin-walled pressure vessel):

  σ_hoop = (P_int - P_ext) × R / e

  - σ_hoop: Contrainte circonférentielle (traction)
  - P_int: Pression gaz (chambre)
  - P_ext: Pression coolant (canaux)
  - R: Rayon moyen
  - e: Épaisseur effective

  Note: Si P_coolant > P_gaz (cycle expander/staged), la paroi
  interne est en COMPRESSION (risque de flambage/buckling).

14.2 CONTRAINTES THERMIQUES (SECONDAIRES)
───────────────────────────────────────────────────────────────
Dues au gradient de température ΔT = T_hot - T_cold.
La face chaude veut se dilater mais est retenue par la face froide.

  σ_thermal = ± [E × α × ΔT] / [2 × (1 - ν)]

  - E: Module de Young (GPa)
  - α: Coefficient de dilatation thermique (K⁻¹)
  - ν: Coefficient de Poisson (~0.3)

  DISTRIBUTION:
  - Face Chaude: COMPRESSION (σ < 0) car dilatation empêchée
  - Face Froide: TRACTION (σ > 0)

  ⚠️ C'est souvent la contrainte dominante (peut dépasser 500 MPa)!

14.3 CRITÈRE DE VON MISES
───────────────────────────────────────────────────────────────
Pour prédire la plastification, on combine les contraintes:

  σ_vm = sqrt(σ_hoop² + σ_long² + σ_radial² - ...)

  Simplifié (état plan):
  σ_vm ≈ sqrt(σ_hoop² + σ_thermal² - σ_hoop×σ_thermal)

  CRITÈRE DE SÉCURITÉ:
  FoS (Factor of Safety) = σ_yield / σ_vm

  - FoS > 1.0 : Domaine élastique (OK)
  - FoS < 1.0 : Plastification (Déformation permanente)

14.4 FATIGUE OLIGOCYCLIQUE (LCF)
───────────────────────────────────────────────────────────────
Dans un moteur fusée, il est courant que σ_vm > σ_yield localement
(FoS < 1). La paroi plastifie à chaque allumage.

LOI DE COFFIN-MANSON:
  N_cycles = C × (Δε_plastique)^(-k)

  - Si on plastifie beaucoup, la durée de vie est courte (ex: 50 cycles).
  - C'est acceptable pour un moteur jetable (ELV).
  - Pour du réutilisable (RLV), il faut viser FoS > 1.2.




---

[← Section précédente : Formules](10-Formules-Rapides.md) | [Retour à l'accueil](Home.md) | [Section suivante : Simulation Transitoire →](15-Simulation-Transitoire.md)
