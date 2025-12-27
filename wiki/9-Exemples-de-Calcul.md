# 9. EXEMPLES DE CALCUL COMPLETS

[← Section précédente : Design](5-Design-et-Dimensionnement.md) | [Retour à l'accueil](Home.md) | [Section suivante : Formules Rapides →](10-Formules-Rapides.md)

---

## Table des matières
- [9.1 Exemple 1 : Moteur LOX/RP-1 petit poussée](#91-exemple-1--moteur-loxrp-1-petit-poussée)
- [9.2 Exemple 2 : Moteur LOX/LH2 haute performance](#92-exemple-2--moteur-loxlh2-haute-performance)
- [9.3 Exemple 3 : Moteur LOX/CH4 (méthane)](#93-exemple-3--moteur-loxch4-méthane)
- [9.4 Exemple 4 : Vérification coefficient h_c requis](#94-exemple-4--vérification-coefficient-h_c-requis)
- [9.5 Exemple 5 : Calcul élévation température coolant](#95-exemple-5--calcul-élévation-température-coolant)
- [9.6 Exemple 6 : Analyse dimensionnelle rapide](#96-exemple-6--analyse-dimensionnelle-rapide)
- [9.7 Tableau récapitulatif des exemples](#97-tableau-récapitulatif-des-exemples)
- [9.8 Exercices d'application](#98-exercices-dapplication)

---

  ┌────────────────────────┬──────────────────────────────────┐
  │ Propriété              │ Valeur                           │
  ├────────────────────────┼──────────────────────────────────┤
  │ Masse molaire          │ 16.04 g/mol                      │
  │ Température ébullition │ 111.7 K (-161°C) @ 1 bar         │
  │ Température critique   │ 190.6 K                          │
  │ Pression critique      │ 46.0 bar                         │
  │ Densité liquide        │ 422 kg/m³ @ 112 K                │
  │ Cp liquide             │ 3,500 J/kg·K                     │
  │ Conductivité (liq)     │ 0.19 W/m·K                       │
  │ Viscosité (liq)        │ 120 μPa·s                        │
  │ Prandtl                │ 2.2                              │
  │ Chaleur latente        │ 510 kJ/kg                        │
  └────────────────────────┴──────────────────────────────────┘

✅ AVANTAGES:
  - Cp élevé (meilleur que RP-1)
  - Température modérée (112 K)
  - PAS DE COKÉFACTION! (propre)
  - Compatible avec O2 (ISRU Mars)
  - Densité acceptable
  - Viscosité faible → bon Re

❌ INCONVÉNIENTS:
  - Moins dense que RP-1
  - Cryogénique (infrastructure)
  - Plage de T plus étroite que H2

AVANTAGE CLÉ - PAS DE COKE:
  Le méthane ne forme PAS de dépôts carbonés 
  contrairement au RP-1/kérosène. Les moteurs peuvent 
  être réutilisés sans nettoyage des canaux!

MOTEURS UTILISANT CH4:
  - Raptor (SpaceX) - full-flow staged combustion
  - BE-4 (Blue Origin) - oxygen-rich staged combustion
  - Prometheus (ESA)
  - Vulcan Centaur (ULA, via BE-4)


8.5 RP-1 / KÉROSÈNE
───────────────────────────────────────────────────────────────

Le RP-1 est le fuel hydrocarbure le plus utilisé historiquement.

PROPRIÉTÉS DÉTAILLÉES:
  ┌────────────────────────┬──────────────────────────────────┐
  │ Propriété              │ Valeur (typique @ 300K)          │
  ├────────────────────────┼──────────────────────────────────┤
  │ Composition            │ C12H24 (moyenne)                 │
  │ Masse molaire          │ ~170 g/mol                       │
  │ Point éclair           │ 316 K (43°C)                     │
  │ Température ébullition │ 490-540 K (plage)                │
  │ Température critique   │ ~678 K                           │
  │ Densité @ 288 K        │ 799-815 kg/m³                    │
  │ Cp @ 300 K             │ 2,000 J/kg·K                     │
  │ Cp @ 400 K             │ 2,300 J/kg·K                     │
  │ Cp @ 500 K             │ 2,800 J/kg·K                     │
  │ Conductivité @ 300 K   │ 0.12 W/m·K                       │
  │ Conductivité @ 400 K   │ 0.10 W/m·K                       │
  │ Viscosité @ 300 K      │ 1.2 mPa·s                        │
  │ Viscosité @ 400 K      │ 0.4 mPa·s                        │
  │ Prandtl @ 300 K        │ 20                               │
  │ Prandtl @ 400 K        │ 9                                │
  └────────────────────────┴──────────────────────────────────┘

✅ AVANTAGES:
  - Stockable à température ambiante!
  - Haute densité → réservoirs compacts
  - Infrastructure existante (aviation)
  - Non toxique (relativement)
  - Économique

❌ INCONVÉNIENTS MAJEURS:

  ⚠️ COKÉFACTION (problème critique!):
  
  À T > 450-500 K, le RP-1 se décompose et dépose du 
  carbone (coke) sur les parois des canaux:
  
    - Réduit la section de passage
    - Réduit le transfert thermique
    - Peut boucher les canaux!
    - Limite la réutilisabilité
  
  TEMPÉRATURE LIMITE:
    T_paroi_froid < 480 K (idéal < 420 K)
  
  SOLUTIONS:
    - RP-2 (version purifiée, moins de soufre)
    - Additifs anti-coke
    - Vitesses élevées (moins de temps de résidence)
    - Canaux larges (plus faciles à nettoyer)

VARIATION DES PROPRIÉTÉS AVEC T:
  ┌────────────┬────────┬────────┬────────┬────────┐
  │ T (K)      │  300   │  350   │  400   │  450   │
  ├────────────┼────────┼────────┼────────┼────────┤
  │ ρ (kg/m³)  │  810   │  775   │  740   │  700   │
  │ Cp (J/kg·K)│  2000  │  2150  │  2300  │  2500  │
  │ k (W/m·K)  │  0.12  │  0.11  │  0.10  │  0.09  │
  │ μ (mPa·s)  │  1.2   │  0.65  │  0.40  │  0.28  │
  │ Pr         │  20    │  12.7  │  9.2   │  7.8   │
  └────────────┴────────┴────────┴────────┴────────┘

MOTEURS UTILISANT RP-1:
  - Merlin (SpaceX Falcon 9)
  - RD-180, RD-191 (Atlas V, Angara)
  - NK-33 (N1)
  - RS-27 (Delta II)
  - F-1 (Saturn V)
  - Rutherford (Rocket Lab) - électropompe


8.6 ÉTHANOL (C2H5OH)
───────────────────────────────────────────────────────────────

Utilisé historiquement et par certains nouveaux acteurs.

PROPRIÉTÉS DÉTAILLÉES:
  ┌────────────────────────┬──────────────────────────────────┐
  │ Propriété              │ Valeur @ 300 K                   │
  ├────────────────────────┼──────────────────────────────────┤
  │ Masse molaire          │ 46.07 g/mol                      │
  │ Température ébullition │ 351.4 K (78°C)                   │
  │ Température critique   │ 514 K                            │
  │ Pression critique      │ 63 bar                           │
  │ Densité                │ 789 kg/m³                        │
  │ Cp                     │ 2,440 J/kg·K                     │
  │ Conductivité           │ 0.17 W/m·K                       │
  │ Viscosité              │ 1.1 mPa·s                        │
  │ Prandtl                │ 16                               │
  │ Chaleur latente        │ 838 kJ/kg                        │
  └────────────────────────┴──────────────────────────────────┘

✅ AVANTAGES:
  - Stockable, non cryogénique
  - Non toxique, biodégradable
  - Bonne capacité de refroidissement
  - Peut contenir de l'eau (refroidissement film)
  - Production renouvelable possible

❌ INCONVÉNIENTS:
  - Point d'ébullition bas (78°C)
  - Risque d'ébullition dans les canaux
  - Isp inférieure au RP-1
  - Hygroscopique (absorbe l'eau)

UTILISATION HISTORIQUE:
  - V-2 (Allemagne WWII)
  - Redstone (USA)
  - Moteurs amateurs/universitaires

MOTEURS MODERNES:
  - MIRA (Espagne)
  - Copenhagen Suborbitals
  - Nombreux projets New Space


8.7 HYDRAZINE ET DÉRIVÉS (N2H4, MMH, UDMH)
───────────────────────────────────────────────────────────────

⚠️ TOXIQUES ET DANGEREUX - Usage spatial principalement

A) HYDRAZINE (N2H4)

  ┌────────────────────────┬──────────────────────────────────┐
  │ Propriété              │ Valeur                           │
  ├────────────────────────┼──────────────────────────────────┤
  │ Masse molaire          │ 32.05 g/mol                      │
  │ Température fusion     │ 274.7 K (1.5°C)                  │
  │ Température ébullition │ 387 K (114°C)                    │
  │ Densité                │ 1,004 kg/m³                      │
  │ Cp                     │ 3,100 J/kg·K                     │
  │ Conductivité           │ 0.35 W/m·K (élevé!)              │
  │ Viscosité              │ 0.97 mPa·s                       │
  └────────────────────────┴──────────────────────────────────┘

  ✅ Avantages: Stockable, hypergolique avec N2O4
  ❌ Inconvénients: TRÈS TOXIQUE, cancérigène

B) MMH (Monométhylhydrazine - CH3NHNH2)

  Densité: 874 kg/m³
  T_boil: 360.5 K
  Cp: 2,900 J/kg·K
  
  Moins toxique que N2H4, plus stable.
  Utilisé: Apollo LM, systèmes orbitaux.

C) UDMH (Diméthylhydrazine asymétrique)

  Densité: 791 kg/m³
  T_boil: 336 K
  Cp: 2,750 J/kg·K
  
  Plus stable au stockage.
  Utilisé: Proton (Russie), Longue Marche (Chine).

UTILISATION:
  - Systèmes orbitaux et interplanétaires
  - Moteurs vernier et RCS
  - En diminution (toxicité)


8.8 EAU (H2O)
───────────────────────────────────────────────────────────────

L'eau est un EXCELLENT coolant mais rarement utilisée seule.

PROPRIÉTÉS:
  ┌────────────────────────┬──────────────────────────────────┐
  │ Propriété              │ Valeur @ 300 K                   │
  ├────────────────────────┼──────────────────────────────────┤
  │ Masse molaire          │ 18.02 g/mol                      │
  │ Température ébullition │ 373.2 K (100°C)                  │
  │ Température critique   │ 647.1 K                          │
  │ Pression critique      │ 220.6 bar                        │
  │ Densité                │ 1,000 kg/m³                      │
  │ Cp                     │ 4,186 J/kg·K (très élevé!)       │
  │ Conductivité           │ 0.60 W/m·K (excellent!)          │
  │ Viscosité              │ 1.0 mPa·s                        │
  │ Prandtl                │ 7                                │
  │ Chaleur latente        │ 2,257 kJ/kg (énorme!)            │
  └────────────────────────┴──────────────────────────────────┘

✅ AVANTAGES:
  - Cp très élevé (4,186 J/kg·K)
  - Conductivité excellente (0.60 W/m·K)
  - Chaleur latente énorme (ébullition = super refroidissement)
  - Non toxique, disponible
  - Économique

❌ INCONVÉNIENTS:
  - Point d'ébullition bas (100°C @ 1 bar)
  - Gel à 0°C (problème spatial)
  - Corrosif si impuretés
  - Non utilisé comme propergol directement

UTILISATION:
  - Tests au sol (refroidissement auxiliaire)
  - Injection pour refroidissement film (mélange éthanol-eau)
  - Systèmes terrestres


8.9 AMMONIAC (NH3)
───────────────────────────────────────────────────────────────

Utilisé dans certaines applications spatiales.

PROPRIÉTÉS:
  ┌────────────────────────┬──────────────────────────────────┐
  │ Propriété              │ Valeur                           │
  ├────────────────────────┼──────────────────────────────────┤
  │ Masse molaire          │ 17.03 g/mol                      │
  │ Température ébullition │ 239.8 K (-33°C)                  │
  │ Température critique   │ 405.4 K                          │
  │ Densité liquide        │ 682 kg/m³                        │
  │ Cp                     │ 4,700 J/kg·K (très élevé!)       │
  │ Conductivité           │ 0.52 W/m·K                       │
  │ Viscosité              │ 0.26 mPa·s                       │
  │ Prandtl                │ 2.4                              │
  │ Chaleur latente        │ 1,370 kJ/kg                      │
  └────────────────────────┴──────────────────────────────────┘

✅ AVANTAGES:
  - Cp élevé (4,700 J/kg·K)
  - Bonne conductivité
  - Stockable sous pression modérée
  - Utilisable comme propergol (avec décomposition)

❌ INCONVÉNIENTS:
  - Toxique (irritant)
  - Odeur forte
  - Corrosif pour cuivre et laiton

UTILISATION:
  - Systèmes de contrôle thermique (boucles)
  - Propulsion électrique (résistojets)
  - ISS (système de refroidissement)


8.10 COMPARAISON ET SÉLECTION DU COOLANT
───────────────────────────────────────────────────────────────

CLASSEMENT PAR CAPACITÉ DE REFROIDISSEMENT:

  ┌────────────────┬────────────┬──────────────────────────────┐
  │ Rang │ Coolant │ Cp×k/μ     │ Commentaire                  │
  ├──────┼─────────┼────────────┼──────────────────────────────┤
  │  1   │ LH2     │ 110,000    │ Le meilleur, mais cryogénique│
  │  2   │ H2O     │ 2,500      │ Excellent mais T_boil basse  │
  │  3   │ NH3     │ 1,900      │ Très bon, stockable          │
  │  4   │ LCH4    │ 550        │ Bon compromis, propre        │
  │  5   │ LOX     │ 130        │ Correct, mais réactif        │
  │  6   │ C2H5OH  │ 75         │ Acceptable, non toxique      │
  │  7   │ RP-1    │ 20         │ Médiocre mais stockable      │
  └──────┴─────────┴────────────┴──────────────────────────────┘

ARBRE DE DÉCISION:

  ┌─ Cycle propulsif ? ─────────────────────────────────────────┐
  │                                                              │
  │ LOX/LH2  → Utiliser LH2 comme coolant (toujours)            │
  │ LOX/CH4  → Utiliser CH4 comme coolant                        │
  │ LOX/RP-1 → Utiliser RP-1 (attention cokéfaction)            │
  │ N2O4/MMH → Utiliser MMH (fuel côté refroidissement)         │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘

  ┌─ Fuel ou Ox pour refroidir ? ───────────────────────────────┐
  │                                                              │
  │ FUEL PRÉFÉRÉ (99% des cas):                                  │
  │  - Moins réactif que l'oxydant                               │
  │  - Généralement meilleur Cp                                  │
  │  - Pas de risque d'ignition avec matériaux                   │
  │                                                              │
  │ OX UTILISÉ (rare):                                           │
  │  - Cycles oxydizer-rich (RD-170)                             │
  │  - Nécessite matériaux spéciaux (Monel, Inconel)            │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘

DIMENSIONNEMENT DU DÉBIT COOLANT:

  Le débit de coolant doit absorber toute la chaleur:
  
  Q_total = ṁ_coolant × Cp × ΔT_coolant
  
  ṁ_coolant = Q_total / (Cp × ΔT_max_admissible)
  
  Typiquement: ΔT_coolant = 100-300 K selon le fluide

EXEMPLE:
  Q_total = 5 MW (intégrale du flux sur la surface)
  Coolant: RP-1, Cp = 2100 J/kg·K, ΔT = 150 K
  
  ṁ_coolant = 5×10⁶ / (2100 × 150) = 15.9 kg/s
  
  Si ratio O/F = 2.5, et ṁ_total = 50 kg/s:
  ṁ_fuel = 50/3.5 = 14.3 kg/s
  
  → ATTENTION: ṁ_coolant > ṁ_fuel disponible!
  → Il faut réduire Q ou augmenter h_c


8.11 PROPRIÉTÉS EN FONCTION DE LA TEMPÉRATURE
───────────────────────────────────────────────────────────────

Les propriétés des fluides varient significativement avec T.
Cela affecte les calculs de h_c.

MÉTHANE (LCH4):
  ┌──────────┬────────┬────────┬────────┬────────┬────────┐
  │ T (K)    │  115   │  130   │  150   │  170   │  190   │
  ├──────────┼────────┼────────┼────────┼────────┼────────┤
  │ ρ (kg/m³)│  420   │  400   │  370   │  330   │  260   │
  │ Cp J/kg·K│  3450  │  3600  │  3900  │  4500  │  6000  │
  │ k W/m·K  │  0.19  │  0.17  │  0.14  │  0.11  │  0.08  │
  │ μ (μPa·s)│  115   │  90    │  65    │  45    │  30    │
  └──────────┴────────┴────────┴────────┴────────┴────────┘

HYDROGÈNE (LH2):
  ┌──────────┬────────┬────────┬────────┬────────┐
  │ T (K)    │   20   │   25   │   30   │   33   │
  ├──────────┼────────┼────────┼────────┼────────┤
  │ ρ (kg/m³)│   71   │   65   │   50   │   31   │
  │ Cp J/kg·K│  9700  │ 12000  │ 19000  │   ∞    │
  │ k W/m·K  │  0.10  │  0.10  │  0.09  │  0.07  │
  │ μ (μPa·s)│   13   │   11   │    8   │    5   │
  └──────────┴────────┴────────┴────────┴────────┘

Note: À T_critique, Cp → ∞ (transition de phase)

CONSEIL:
  Toujours utiliser les propriétés à T_film:
  
  T_film = (T_wall_cold + T_bulk) / 2


9. EXEMPLES DE CALCUL COMPLETS
═══════════════════════════════════════════════════════════════

Cette section présente plusieurs exemples de calcul détaillés pour
illustrer l'application des équations thermiques aux moteurs-fusées.
Chaque exemple suit une méthodologie complète et vérifie les résultats.


9.1 EXEMPLE 1 : PETIT MOTEUR LOX/RP-1 (TYPE AMATEUR AVANCÉ)
───────────────────────────────────────────────────────────────

DONNÉES DU PROBLÈME:
  ┌─────────────────────────────────────────────────────────┐
  │ PARAMÈTRES DE CONCEPTION                                │
  ├─────────────────────────────────────────────────────────┤
  │ Propergols:        LOX / RP-1                           │
  │ Pression chambre:  25 bar (2.5 MPa)                     │
  │ Rapport O/F:       2.4                                  │
  │ Débit total:       0.8 kg/s                             │
  │ Diamètre col:      30 mm                                │
  │ Ratio expansion:   8:1                                  │
  │ T chambre:         3200 K (calculé CEA)                 │
  │ γ gaz:             1.21                                 │
  │ M gaz:             22.5 kg/kmol                         │
  │ μ gaz:             8.2×10⁻⁵ Pa·s                        │
  │ Cp gaz:            2100 J/kg·K                          │
  ├─────────────────────────────────────────────────────────┤
  │ SYSTÈME DE REFROIDISSEMENT                              │
  ├─────────────────────────────────────────────────────────┤
  │ Coolant:           RP-1                                 │
  │ T entrée coolant:  300 K                                │
  │ Pression coolant:  30 bar                               │
  │ Vitesse coolant:   20 m/s                               │
  │ Dh canal:          4 mm                                 │
  ├─────────────────────────────────────────────────────────┤
  │ PAROI                                                   │
  ├─────────────────────────────────────────────────────────┤
  │ Matériau:          CuCr1Zr                              │
  │ Conductivité:      320 W/m·K                            │
  │ T limite:          723 K (450°C)                        │
  │ T fusion:          1350 K                               │
  │ Épaisseur:         3 mm                                 │
  └─────────────────────────────────────────────────────────┘

ÉTAPE 1 - CALCUL DU COEFFICIENT h_g (ÉQUATION DE BARTZ)
─────────────────────────────────────────────────────────

Données nécessaires:
  • Dt = 0.030 m (diamètre col)
  • At = π × (0.030)² / 4 = 7.07×10⁻⁴ m²
  • Pc = 25×10⁵ Pa
  • c* = 1650 m/s (calculé ou table CEA)
  • Tc = 3200 K
  • M = 22.5 kg/kmol
  • γ = 1.21
  • μ = 8.2×10⁻⁵ Pa·s
  • Cp = 2100 J/kg·K
  • Pr = μ × Cp / k_gaz ≈ 0.72

Calcul du nombre de Prandtl:
  Pr = Cp × μ / k_gaz
  k_gaz ≈ Cp × μ / Pr = 2100 × 8.2×10⁻⁵ / 0.72 = 0.239 W/m·K

Facteur de correction σ (Bartz):
  T_wall estimée ≈ 900 K (première itération)
  T_aw = Tc × [1 + (γ-1)/2 × r × M²]
  Au col (M=1): T_aw ≈ 0.91 × Tc = 2912 K
  
  σ = [0.5 × (T_wall/Tc) × (1 + (γ-1)/2 × M²) + 0.5]^(-0.68)
  σ = [0.5 × (900/3200) × 1.105 + 0.5]^(-0.68)
  σ = [0.655]^(-0.68) = 1.38

Équation de Bartz au col:
  h_g = (0.026 / Dt^0.2) × (μ^0.2 × Cp / Pr^0.6) × (Pc/c*)^0.8 × (Dt/Rc)^0.1 × σ

  Avec Rc = 1.5 × Dt = 0.045 m (rayon de courbure standard):
  
  h_g = (0.026 / 0.030^0.2) × (8.2×10⁻⁵)^0.2 × 2100 / 0.72^0.6 
        × (25×10⁵ / 1650)^0.8 × (0.030/0.045)^0.1 × 1.38
  
  Calcul terme par terme:
    • 0.026 / 0.030^0.2 = 0.026 / 0.494 = 0.0527
    • (8.2×10⁻⁵)^0.2 = 0.0972
    • 0.72^0.6 = 0.823
    • (25×10⁵ / 1650)^0.8 = (1515)^0.8 = 405.7
    • (0.030/0.045)^0.1 = 0.667^0.1 = 0.960
    • σ = 1.38
  
  h_g = 0.0527 × 0.0972 × 2100 / 0.823 × 405.7 × 0.960 × 1.38
  
  h_g = 0.0527 × 247.5 × 405.7 × 0.960 × 1.38
  
  h_g ≈ 7,020 W/m²·K

  ⚠️ RÉSULTAT: h_g au col ≈ 7,000 W/m²·K


ÉTAPE 2 - CALCUL DU COEFFICIENT h_c (DITTUS-BOELTER)
─────────────────────────────────────────────────────

Propriétés du RP-1 à T_film ≈ 350 K (estimation):
  • ρ = 780 kg/m³
  • μ = 1.2×10⁻³ Pa·s
  • k = 0.11 W/m·K
  • Cp = 2100 J/kg·K
  • Pr = Cp × μ / k = 2100 × 1.2×10⁻³ / 0.11 = 22.9

Nombre de Reynolds:
  Re = ρ × v × Dh / μ
  Re = 780 × 20 × 0.004 / (1.2×10⁻³)
  Re = 52,000

  ✅ Re > 10,000 → Écoulement turbulent, Dittus-Boelter applicable

Nombre de Nusselt (Dittus-Boelter, chauffage):
  Nu = 0.023 × Re^0.8 × Pr^0.4
  Nu = 0.023 × (52,000)^0.8 × (22.9)^0.4
  Nu = 0.023 × 5,893 × 4.05
  Nu = 549

Coefficient de transfert:
  h_c = Nu × k / Dh
  h_c = 549 × 0.11 / 0.004
  h_c = 15,100 W/m²·K

  ⚠️ RÉSULTAT: h_c ≈ 15,100 W/m²·K


ÉTAPE 3 - CALCUL DU FLUX THERMIQUE ET TEMPÉRATURES
──────────────────────────────────────────────────

Résistance thermique totale:
  R_total = 1/h_g + e/k + 1/h_c
  
  R_gaz    = 1/7,000 = 1.43×10⁻⁴ m²·K/W
  R_paroi  = 0.003/320 = 9.38×10⁻⁶ m²·K/W
  R_cool   = 1/15,100 = 6.62×10⁻⁵ m²·K/W
  
  R_total = 1.43×10⁻⁴ + 9.38×10⁻⁶ + 6.62×10⁻⁵
  R_total = 2.19×10⁻⁴ m²·K/W

  Note: La résistance dominante est R_gaz (65% du total)

Flux thermique:
  ΔT = T_aw - T_coolant = 2912 - 300 = 2612 K
  
  q = ΔT / R_total
  q = 2612 / 2.19×10⁻⁴
  q = 11.93×10⁶ W/m²
  
  ⚠️ RÉSULTAT: q ≈ 12 MW/m²

Distribution des températures:
  T_wall_cold = T_coolant + q / h_c
  T_wall_cold = 300 + 11.93×10⁶ / 15,100
  T_wall_cold = 300 + 790 = 1090 K   ❌ TROP ÉLEVÉ!

  T_wall_hot = T_wall_cold + q × e / k
  T_wall_hot = 1090 + 11.93×10⁶ × 0.003 / 320
  T_wall_hot = 1090 + 112 = 1202 K


ÉTAPE 4 - ANALYSE ET ITÉRATION
─────────────────────────────

⚠️ PROBLÈME DÉTECTÉ:
  T_wall_cold = 1090 K >> T_limite (723 K)
  La conception actuelle NE FONCTIONNE PAS!

SOLUTIONS POSSIBLES:
  1. Augmenter la vitesse du coolant
  2. Augmenter le débit du coolant
  3. Réduire le diamètre hydraulique
  4. Ajouter du refroidissement par film
  5. Changer de coolant (LH2 beaucoup plus efficace)

ITÉRATION - Augmentation vitesse à 40 m/s:
  Re = 780 × 40 × 0.004 / (1.2×10⁻³) = 104,000
  Nu = 0.023 × (104,000)^0.8 × (22.9)^0.4 = 956
  h_c = 956 × 0.11 / 0.004 = 26,300 W/m²·K
  
  R_cool = 1/26,300 = 3.80×10⁻⁵ m²·K/W
  R_total = 1.43×10⁻⁴ + 9.38×10⁻⁶ + 3.80×10⁻⁵ = 1.90×10⁻⁴ m²·K/W
  
  q = 2612 / 1.90×10⁻⁴ = 13.7 MW/m²
  
  T_wall_cold = 300 + 13.7×10⁶ / 26,300 = 821 K   ❌ Encore trop!

ITÉRATION - Avec refroidissement par film (15% fuel):
  Efficacité film: η_film ≈ 0.60
  T_aw_effective = T_coolant + η_film × (T_aw - T_coolant)
  T_aw_effective = 300 + 0.60 × (2912 - 300) = 1867 K
  
  q = (1867 - 300) / 1.90×10⁻⁴ = 8.2 MW/m²
  
  T_wall_cold = 300 + 8.2×10⁶ / 26,300 = 612 K   ✅ OK!
  T_wall_hot = 612 + 8.2×10⁶ × 0.003 / 320 = 689 K   ✅ OK!

  ⚠️ SOLUTION: Vitesse 40 m/s + film cooling 15% → T_wall < T_limite


ÉTAPE 5 - CALCUL ÉPAISSEUR CRITIQUE
───────────────────────────────────

Avec la configuration finale (v=40 m/s, film 15%):

Épaisseur de fusion:
  e_melt = k × (T_fusion - T_wall_cold) / q
  e_melt = 320 × (1350 - 612) / 8.2×10⁶
  e_melt = 320 × 738 / 8.2×10⁶
  e_melt = 0.0288 m = 28.8 mm

Épaisseur limite opérationnelle:
  e_max = k × (T_limite - T_wall_cold) / q
  e_max = 320 × (723 - 612) / 8.2×10⁶
  e_max = 320 × 111 / 8.2×10⁶
  e_max = 0.00433 m = 4.33 mm

  ✅ Épaisseur 3 mm < e_max (4.33 mm) → Conception valide

Marge de sécurité sur épaisseur:
  Marge = (e_max - e_actuelle) / e_actuelle × 100
  Marge = (4.33 - 3) / 3 × 100 = 44%   ✅ Marge acceptable


ÉTAPE 6 - RÉCAPITULATIF CONCEPTION FINALE
─────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────┐
  │ RÉSUMÉ DE LA CONCEPTION VALIDÉE                         │
  ├─────────────────────────────────────────────────────────┤
  │ Vitesse coolant:      40 m/s                            │
  │ Film cooling:         15% du débit fuel                 │
  │ h_g:                  7,000 W/m²·K                      │
  │ h_c:                  26,300 W/m²·K                     │
  │ Flux thermique:       8.2 MW/m²                         │
  │ T_wall_hot:           689 K                             │
  │ T_wall_cold:          612 K                             │
  │ Marge vs T_limite:    34 K (5%)                         │
  │ Épaisseur:            3 mm (marge 44%)                  │
  └─────────────────────────────────────────────────────────┘


9.2 EXEMPLE 2 : MOTEUR LOX/LH2 HAUTE PERFORMANCE
───────────────────────────────────────────────────────────────

DONNÉES DU PROBLÈME:
  ┌─────────────────────────────────────────────────────────┐
  │ PARAMÈTRES DE CONCEPTION                                │
  ├─────────────────────────────────────────────────────────┤
  │ Propergols:        LOX / LH2                            │
  │ Pression chambre:  100 bar (10 MPa)                     │
  │ Rapport O/F:       6.0                                  │
  │ Débit total:       25 kg/s                              │
  │ Diamètre col:      80 mm                                │
  │ Ratio expansion:   40:1                                 │
  │ T chambre:         3550 K (calculé CEA)                 │
  │ γ gaz:             1.14                                 │
  │ M gaz:             13.5 kg/kmol                         │
  │ c*:                2350 m/s                             │
  ├─────────────────────────────────────────────────────────┤
  │ SYSTÈME DE REFROIDISSEMENT                              │
  ├─────────────────────────────────────────────────────────┤
  │ Coolant:           LH2 supercritique                    │
  │ T entrée coolant:  40 K                                 │
  │ Pression coolant:  150 bar                              │
  │ Débit H2:          3.57 kg/s (mdot_fuel)                │
  │ Dh canal:          2 mm                                 │
  │ Nombre canaux:     200                                  │
  ├─────────────────────────────────────────────────────────┤
  │ PAROI                                                   │
  ├─────────────────────────────────────────────────────────┤
  │ Matériau:          NARloy-Z (Cu-Ag-Zr)                  │
  │ Conductivité:      340 W/m·K                            │
  │ T limite:          810 K                                │
  │ T fusion:          1355 K                               │
  │ Épaisseur:         1.5 mm                               │
  └─────────────────────────────────────────────────────────┘

ÉTAPE 1 - CALCUL h_g (BARTZ)
────────────────────────────

  μ_gaz ≈ 7.5×10⁻⁵ Pa·s (à Tc)
  Cp_gaz = 3800 J/kg·K (H2O/H2 dominant)
  Pr = 0.68

  σ ≈ 1.42 (avec T_wall estimée 600 K)

  h_g = (0.026 / 0.080^0.2) × (7.5×10⁻⁵)^0.2 × 3800 / 0.68^0.6 
        × (100×10⁵ / 2350)^0.8 × σ
  
  Calcul:
    • 0.026 / 0.080^0.2 = 0.026 / 0.574 = 0.0453
    • (7.5×10⁻⁵)^0.2 = 0.0948
    • 0.68^0.6 = 0.796
    • (100×10⁵ / 2350)^0.8 = (4255)^0.8 = 846
  
  h_g = 0.0453 × 0.0948 × 3800 / 0.796 × 846 × 1.42
  
  h_g ≈ 24,600 W/m²·K

  Note: Plus élevé que LOX/RP-1 car Pc plus haute et Cp gaz plus élevé


ÉTAPE 2 - CALCUL h_c (LH2 SUPERCRITIQUE)
────────────────────────────────────────

L'hydrogène supercritique (P > 13 bar, T > 33 K) a des propriétés
exceptionnelles mais qui varient fortement avec la température.

Propriétés LH2 à 100 K, 150 bar:
  • ρ = 45 kg/m³
  • μ = 5.5×10⁻⁶ Pa·s
  • k = 0.12 W/m·K
  • Cp = 14,500 J/kg·K (pic pseudo-critique)
  • Pr = 0.67

Section canal (rectangulaire 2×4 mm):
  A_canal = 8 mm² = 8×10⁻⁶ m²
  Périmètre = 12 mm
  Dh = 4A/P = 4×8/12 = 2.67 mm

Débit par canal:
  mdot_canal = 3.57 / 200 = 0.0179 kg/s
  v = mdot / (ρ × A) = 0.0179 / (45 × 8×10⁻⁶) = 49.7 m/s

Nombre de Reynolds:
  Re = ρ × v × Dh / μ
  Re = 45 × 49.7 × 0.00267 / (5.5×10⁻⁶)
  Re = 1,086,000   (très turbulent!)

Corrélation Gnielinski (recommandée pour grandes variations Pr):
  f = (0.79 × ln(Re) - 1.64)^(-2)
  f = (0.79 × 13.9 - 1.64)^(-2) = (9.34)^(-2) = 0.0115
  
  Nu = (f/8) × (Re - 1000) × Pr / [1 + 12.7×(f/8)^0.5 × (Pr^(2/3) - 1)]
  Nu = (0.0115/8) × (1,085,000) × 0.67 / [1 + 12.7×(0.0379) × (-0.24)]
  Nu = 0.00144 × 727,000 / 0.884
  Nu = 1,183

Coefficient de transfert:
  h_c = Nu × k / Dh
  h_c = 1,183 × 0.12 / 0.00267
  h_c = 53,200 W/m²·K

  ⚠️ RÉSULTAT: h_c ≈ 53,000 W/m²·K (excellent!)


ÉTAPE 3 - FLUX ET TEMPÉRATURES
─────────────────────────────

Résistances thermiques:
  R_gaz    = 1/24,600 = 4.07×10⁻⁵ m²·K/W
  R_paroi  = 0.0015/340 = 4.41×10⁻⁶ m²·K/W
  R_cool   = 1/53,200 = 1.88×10⁻⁵ m²·K/W
  
  R_total = 6.39×10⁻⁵ m²·K/W

  Note: Distribution plus équilibrée grâce au h_c élevé

T_aw au col:
  r = Pr^0.33 = 0.68^0.33 = 0.88
  T_aw = Tc × [1 + r×(γ-1)/2] = 3550 × [1 + 0.88×0.07] = 3769 K
  
  (Pour LOX/LH2, T_aw ≈ 0.90 × Tc au col)

Flux thermique:
  ΔT = T_aw - T_bulk = 3769 - 100 = 3669 K
  
  q = 3669 / 6.39×10⁻⁵ = 57.4 MW/m²

  ⚠️ FLUX TRÈS ÉLEVÉ - typique des moteurs LOX/LH2

Températures paroi:
  T_wall_cold = 100 + 57.4×10⁶ / 53,200 = 1,179 K   ❌ PROBLÈME!
  
  La température dépasse la limite (810 K) et même approche la fusion!


ÉTAPE 4 - OPTIMISATION NÉCESSAIRE
─────────────────────────────────

Le flux de 57 MW/m² est trop intense. Solutions:

1. AUGMENTER LE NOMBRE DE CANAUX:
   N = 400 canaux → v = 99 m/s → Re = 2.17×10⁶
   Nu = 2,100 → h_c = 94,400 W/m²·K
   T_wall_cold = 100 + 57.4×10⁶ / 94,400 = 708 K   ✅ OK!

2. OU RÉDUIRE LE DIAMÈTRE HYDRAULIQUE:
   Dh = 1.5 mm → Re augmente → h_c augmente

3. OU AJOUTER FILM COOLING:
   Film H2 5% → efficacité 0.40
   T_aw_eff = 100 + 0.40×(3769-100) = 1568 K
   q = (1568-100) / 6.39×10⁻⁵ = 23.0 MW/m²
   T_wall_cold = 100 + 23.0×10⁶ / 53,200 = 533 K   ✅

CONCEPTION FINALE RETENUE: 400 canaux
  ┌─────────────────────────────────────────────────────────┐
  │ RÉSUMÉ LOX/LH2                                          │
  ├─────────────────────────────────────────────────────────┤
  │ h_g:                  24,600 W/m²·K                     │
  │ h_c:                  94,400 W/m²·K                     │
  │ Flux thermique:       50.2 MW/m² (avec 400 canaux)      │
  │ T_wall_cold:          632 K                             │
  │ T_wall_hot:           854 K                             │
  │ Marge vs T_limite:    -44 K ❌ (besoin film cooling)    │
  │                                                         │
  │ AVEC FILM COOLING 3%:                                   │
  │ Flux effectif:        32 MW/m²                          │
  │ T_wall_hot:           615 K   ✅                        │
  └─────────────────────────────────────────────────────────┘


9.3 EXEMPLE 3 : MOTEUR LOX/CH4 (NOUVELLE GÉNÉRATION)
───────────────────────────────────────────────────────────────

Le méthane est un compromis entre RP-1 et LH2, offrant de bonnes
propriétés de refroidissement sans les contraintes cryogéniques extrêmes.

DONNÉES:
  ┌─────────────────────────────────────────────────────────┐
  │ Propergols:        LOX / LCH4                           │
  │ Pression chambre:  80 bar                               │
  │ Rapport O/F:       3.6                                  │
  │ Diamètre col:      150 mm                               │
  │ T chambre:         3450 K                               │
  │ Coolant:           LCH4 supercritique (120 K, 100 bar)  │
  │ Matériau:          C-103 (Nb alloy, k=42 W/m·K)         │
  │ Épaisseur:         2 mm                                 │
  └─────────────────────────────────────────────────────────┘

CALCULS RAPIDES:

h_g (Bartz):
  h_g ≈ 18,500 W/m²·K (estimé avec corrélation)

h_c (CH4 supercritique à 150 K):
  Propriétés CH4: ρ=200 kg/m³, μ=30×10⁻⁶ Pa·s, k=0.15 W/m·K, Cp=4000 J/kg·K
  Avec v=30 m/s, Dh=3 mm:
  Re = 200 × 30 × 0.003 / 30×10⁻⁶ = 600,000
  Nu = 1,850 (Gnielinski)
  h_c = 1,850 × 0.15 / 0.003 = 92,500 W/m²·K

Flux et températures:
  R_total = 1/18,500 + 0.002/42 + 1/92,500 = 1.12×10⁻⁴ m²·K/W
  T_aw ≈ 0.92 × 3450 = 3174 K
  q = (3174 - 150) / 1.12×10⁻⁴ = 27.0 MW/m²
  
  T_wall_cold = 150 + 27.0×10⁶ / 92,500 = 442 K
  T_wall_hot = 442 + 27.0×10⁶ × 0.002 / 42 = 1,728 K   ❌

  ⚠️ Le niobium (T_fusion = 2750 K) supporte cette température, mais
     la durée de vie serait limitée. Une liner en cuivre serait préférable.

SOLUTION: Liner CuCrZr + coque Nb
  Liner 0.8 mm CuCrZr (k=320) + coque 2 mm Nb
  R_total = 1/18,500 + 0.0008/320 + 0.002/42 + 1/92,500 = 1.14×10⁻⁴
  T_wall_hot = 150 + 27×10⁶ × (1/92,500 + 0.0008/320) = 511 K   ✅


9.4 EXEMPLE 4 : DIMENSIONNEMENT CANAUX DE REFROIDISSEMENT
───────────────────────────────────────────────────────────────

Cet exemple montre comment dimensionner les canaux pour atteindre
un h_c cible avec un Δp acceptable.

OBJECTIF:
  Atteindre h_c = 50,000 W/m²·K avec RP-1
  Contrainte: Δp < 10 bar sur 200 mm de longueur

DONNÉES:
  • Coolant: RP-1 @ 350 K
  • ρ = 750 kg/m³, μ = 8×10⁻⁴ Pa·s, k = 0.10 W/m·K, Pr = 17
  • Débit disponible: 2 kg/s
  • Circonférence col: π × 0.050 = 0.157 m

MÉTHODE DE RÉSOLUTION:

1. Déterminer Nu nécessaire:
   h_c = Nu × k / Dh
   50,000 = Nu × 0.10 / Dh
   Nu × Dh = 5000   ... (Eq. 1)

2. Exprimer Nu en fonction de Re (Dittus-Boelter):
   Nu = 0.023 × Re^0.8 × 17^0.4 = 0.023 × Re^0.8 × 3.65
   Nu = 0.084 × Re^0.8   ... (Eq. 2)

3. Exprimer Re en fonction de Dh:
   Soit N canaux de largeur w et profondeur d
   Dh = 4×w×d / (2w + 2d)
   
   Pour w = 2×d: Dh = 4×2d² / 6d = 1.33d
   
   Débit par canal: mdot_c = 2/N
   Vitesse: v = mdot_c / (ρ × w × d) = 2 / (N × 750 × 2d²)
   
   Re = 750 × v × Dh / 8×10⁻⁴

4. Itération:
   Essai N = 80, d = 1.5 mm, w = 3 mm:
   Dh = 4×3×1.5 / 9 = 2 mm
   A_canal = 4.5 mm²
   v = 2 / (80 × 750 × 4.5×10⁻⁶) = 7.4 m/s
   Re = 750 × 7.4 × 0.002 / 8×10⁻⁴ = 13,900
   Nu = 0.084 × 13,900^0.8 = 213
   h_c = 213 × 0.10 / 0.002 = 10,650 W/m²·K   ❌ Trop bas!

   Essai N = 120, d = 1 mm, w = 2 mm:
   Dh = 4×2×1 / 6 = 1.33 mm
   A_canal = 2 mm²
   v = 2 / (120 × 750 × 2×10⁻⁶) = 11.1 m/s
   Re = 750 × 11.1 × 0.00133 / 8×10⁻⁴ = 13,850
   Nu = 0.084 × 13,850^0.8 = 212
   h_c = 212 × 0.10 / 0.00133 = 15,940 W/m²·K   ❌ Encore trop bas

   Essai N = 150, d = 0.8 mm, w = 1.6 mm (canaux fins):
   Dh = 4×1.6×0.8 / 4.8 = 1.07 mm
   v = 2 / (150 × 750 × 1.28×10⁻⁶) = 13.9 m/s
   Re = 750 × 13.9 × 0.00107 / 8×10⁻⁴ = 13,940
   h_c = 14,000 W/m²·K   ❌
   
   PROBLÈME: avec RP-1, difficile d'atteindre h_c > 30,000 W/m²·K
   sans pertes de charge excessives.

5. Vérification perte de charge:
   f = 0.316 / Re^0.25 = 0.316 / 13,940^0.25 = 0.029
   Δp = f × L/Dh × ρ × v² / 2
   Δp = 0.029 × 0.2/0.00107 × 750 × 13.9² / 2
   Δp = 5.42 × 72,560 = 3.93 bar   ✅ OK

CONCLUSION:
  h_c_max réaliste avec RP-1 ≈ 25,000 W/m²·K
  Pour h_c = 50,000 W/m²·K, utiliser LH2 ou LCH4


9.5 EXEMPLE 5 : CALCUL ÉLÉVATION TEMPÉRATURE COOLANT
───────────────────────────────────────────────────────────────

Vérifier que le coolant ne surchauffe pas en traversant les canaux.

DONNÉES:
  • Q_total = 850 kW (puissance thermique totale)
  • Coolant: RP-1
  • Débit: 2 kg/s
  • Cp = 2100 J/kg·K
  • T_entrée = 300 K
  • T_ébullition = 490 K à 30 bar

CALCUL:
  ΔT_coolant = Q_total / (mdot × Cp)
  ΔT_coolant = 850,000 / (2 × 2100)
  ΔT_coolant = 202 K
  
  T_sortie = 300 + 202 = 502 K   ⚠️ > T_ébullition!

PROBLÈME: Le RP-1 risque de bouillir et former des dépôts (coking)

SOLUTIONS:
  1. Augmenter le débit coolant (si possible)
  2. Augmenter la pression coolant pour élever T_ébullition
  3. Utiliser du refroidissement par film pour réduire Q_total
  4. Multi-pass cooling (entrée au col, zones froides vers chambre)

AVEC FILM COOLING 20%:
  Q_effectif = 0.65 × 850 = 552 kW (réduction typique avec film)
  ΔT_coolant = 552,000 / (2 × 2100) = 132 K
  T_sortie = 300 + 132 = 432 K   ✅ < T_ébullition


9.6 EXEMPLE 6 : ANALYSE DIMENSIONNELLE RAPIDE
───────────────────────────────────────────────────────────────

Méthode simplifiée pour estimation préliminaire.

RÈGLES EMPIRIQUES (moteurs conventionnels):

  ┌──────────────────────────────────────────────────────────┐
  │ ESTIMATIONS RAPIDES                                      │
  ├──────────────────────────────────────────────────────────┤
  │ h_g au col ≈ 5000 × (Pc/20)^0.8 × (30/Dt)^0.8 W/m²·K    │
  │   où Pc en bar, Dt en mm                                 │
  │                                                          │
  │ q_col ≈ 0.4 × h_g × Tc  (en W/m²)                       │
  │   approximation avec T_wall typique                      │
  │                                                          │
  │ Q_total ≈ q_col × 0.3 × A_totale                        │
  │   car flux moyen ≈ 30% du flux au col                    │
  │                                                          │
  │ ΔT_coolant ≈ Q_total / (mdot_fuel × Cp_fuel)            │
  └──────────────────────────────────────────────────────────┘

EXEMPLE RAPIDE:
  Pc = 50 bar, Dt = 60 mm, Tc = 3400 K, LOX/RP-1
  
  h_g ≈ 5000 × (50/20)^0.8 × (30/60)^0.8
  h_g ≈ 5000 × 2.0 × 0.57 = 5,700 W/m²·K
  
  q_col ≈ 0.4 × 5700 × 3400 = 7.8 MW/m²
  
  Cette estimation est généralement à ±30% de la valeur réelle.


9.7 TABLEAU RÉCAPITULATIF DES EXEMPLES
───────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │ COMPARAISON DES EXEMPLES DE CALCUL                                      │
  ├───────────┬──────────┬──────────┬──────────┬─────────┬─────────────────┤
  │ Exemple   │ Pc (bar) │ Dt (mm)  │ q (MW/m²)│ h_g     │ Solution        │
  ├───────────┼──────────┼──────────┼──────────┼─────────┼─────────────────┤
  │ LOX/RP-1  │ 25       │ 30       │ 8.2      │ 7,000   │ Film 15% + v↑   │
  │ LOX/LH2   │ 100      │ 80       │ 32       │ 24,600  │ 400 can + film  │
  │ LOX/CH4   │ 80       │ 150      │ 27       │ 18,500  │ Liner Cu + Nb   │
  └───────────┴──────────┴──────────┴──────────┴─────────┴─────────────────┘

TENDANCES OBSERVÉES:
  • q augmente avec Pc (quasi-linéairement)
  • h_g augmente quand Dt diminue
  • LOX/LH2 requiert le refroidissement le plus intense
  • Le film cooling est souvent nécessaire pour Pc > 50 bar


9.8 EXERCICES D'APPLICATION
───────────────────────────────────────────────────────────────

EXERCICE 1 - Calcul basique:
  Un moteur LOX/Ethanol a: Pc=15 bar, Dt=25 mm, Tc=3000 K
  Calculer h_g au col avec l'équation de Bartz.
  (Réponse: ≈ 4,800 W/m²·K)

EXERCICE 2 - Dimensionnement coolant:
  Avec q=5 MW/m² et h_c requis=20,000 W/m²·K
  Quelle élévation de température paroi côté froid?
  (Réponse: ΔT = q/h_c = 250 K)

EXERCICE 3 - Épaisseur critique:
  Paroi cuivre (k=360 W/m·K), T_limite=700 K, T_cold=400 K
  Flux q=15 MW/m². Quelle épaisseur maximale?
  (Réponse: e_max = k×ΔT/q = 7.2 mm)

EXERCICE 4 - Puissance thermique:
  Moteur 5 kN de poussée, Isp=280s, Tc=3200 K
  Estimer la puissance thermique à évacuer.
  (Réponse: Q ≈ 0.5-1 MW, selon géométrie et flux)



---

[← Section précédente : Design](5-Design-et-Dimensionnement.md) | [Retour à l'accueil](Home.md) | [Section suivante : Formules Rapides →](10-Formules-Rapides.md)
