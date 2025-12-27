# 5-8. DESIGN ET DIMENSIONNEMENT DES CANAUX

[← Section précédente : Températures de Paroi](4-Calcul-des-Temperatures-de-Paroi.md) | [Retour à l'accueil](Home.md) | [Section suivante : Exemples de Calcul →](9-Exemples-de-Calcul.md)

---

## Table des matières
- [5. Coefficient de convection côté coolant](#5-coefficient-de-convection-côté-coolant)
- [6. Dimensionnement des canaux de refroidissement](#6-dimensionnement-des-canaux-de-refroidissement)
- [7. Pertes de charge hydrauliques](#7-pertes-de-charge-hydrauliques)
- [8. Choix des matériaux](#8-choix-des-matériaux)

---

  ┌──────────────────┬────────────┬─────────────────────┐
  │ Matériau         │ α (mm²/s)  │ τ pour e=2mm (s)    │
  ├──────────────────┼────────────┼─────────────────────┤
  │ Cuivre           │   117      │     0.034           │
  │ CuCr             │   104      │     0.038           │
  │ Inconel 718      │    3.1     │     1.3             │
  │ Inox 316L        │    4.0     │     1.0             │
  │ Niobium          │   24.3     │     0.16            │
  │ Molybdène        │   53.7     │     0.074           │
  │ Tungstène        │   68.3     │     0.058           │
  └──────────────────┴────────────┴─────────────────────┘

IMPLICATIONS:
  - Cuivre: réponse très rapide (~35 ms)
  - Superalliages: réponse lente (~1 s)
  - Pendant le transitoire, T_wall_hot peut DÉPASSER la valeur 
    en régime permanent (overshoot)!

⚠️ RISQUE AU DÉMARRAGE:
Le coolant peut ne pas être à plein débit quand les gaz 
chauds arrivent → surchauffe critique possible!


4.7 TEMPÉRATURE ADIABATIQUE DE PAROI
───────────────────────────────────────────────────────────────

En réalité, on n'utilise pas directement T_chambre mais la 
température adiabatique de paroi T_aw.

DÉFINITION:
T_aw est la température qu'atteindrait une paroi parfaitement 
isolée (adiabatique) exposée à l'écoulement.

CALCUL:
                          γ - 1
  T_aw = T_statique × (1 + r × ───── × M²)
                            2

Où:
  r = facteur de récupération ≈ Pr^(1/3) pour turbulent
  γ = rapport des chaleurs spécifiques
  M = nombre de Mach local

VALEURS DE r:
  - Écoulement laminaire:  r ≈ Pr^(1/2) ≈ 0.85
  - Écoulement turbulent:  r ≈ Pr^(1/3) ≈ 0.89

EFFET:
  T_aw < T_stagnation (à cause des frottements visqueux)
  
Typiquement: T_aw ≈ 0.9 × T_stagnation au col


4.8 CALCUL ITÉRATIF COMPLET
───────────────────────────────────────────────────────────────

En pratique, le calcul est itératif car h_g et h_c dépendent 
des températures (via les propriétés des fluides).

ALGORITHME:
  1. Estimer T_wall_hot_init (e.g., 800 K)
  2. Calculer T_film_gaz = (T_aw + T_wall_hot)/2
  3. Calculer propriétés gaz à T_film_gaz
  4. Calculer h_g (Bartz)
  5. Estimer T_wall_cold
  6. Calculer T_film_cool = (T_wall_cold + T_cool)/2
  7. Calculer propriétés coolant à T_film_cool
  8. Calculer h_c (Dittus-Boelter ou Gnielinski)
  9. Calculer q = (T_aw - T_cool) / (1/h_g + e/k + 1/h_c)
  10. Calculer nouvelles T_wall_hot et T_wall_cold
  11. Si |T_new - T_old| > tolérance: retour à 2
  12. Sinon: CONVERGÉ!

CRITÈRE DE CONVERGENCE:
  |T_wall_hot_new - T_wall_hot_old| < 1 K

Typiquement convergence en 3-5 itérations.


5. CORRÉLATIONS CÔTÉ COOLANT - ANALYSE DÉTAILLÉE
═══════════════════════════════════════════════════════════════

Le calcul précis de h_c est crucial pour une conception fiable.
Cette section détaille les principales corrélations utilisées.


5.1 CORRÉLATION DE DITTUS-BOELTER
───────────────────────────────────────────────────────────────

C'est la corrélation la plus utilisée pour l'écoulement 
turbulent en convection forcée dans des tubes.

HISTORIQUE:
  Publiée en 1930 par F.W. Dittus et L.M.K. Boelter.
  Basée sur des expériences avec de l'eau et de l'huile.

ÉQUATION:
  Nu = 0.023 × Re^0.8 × Pr^n

Où:
  n = 0.4 si le fluide est CHAUFFÉ (T_paroi > T_fluide)
  n = 0.3 si le fluide est REFROIDI (T_paroi < T_fluide)

Dans le cas du refroidissement régénératif:
  Le coolant est chauffé → n = 0.4

DONC:
  Nu = 0.023 × Re^0.8 × Pr^0.4

CONDITIONS DE VALIDITÉ:
  ┌────────────────────────────────────────────────────────────┐
  │ • Re > 10,000 (écoulement pleinement turbulent)            │
  │ • 0.6 < Pr < 160                                           │
  │ • L/D > 10 (écoulement développé)                          │
  │ • Propriétés évaluées à T_bulk (température moyenne)       │
  │ • Flux de chaleur modéré                                   │
  │ • Parois lisses                                            │
  └────────────────────────────────────────────────────────────┘

CALCUL DE h_c:
              Nu × k_coolant
  h_c = ─────────────────────
               D_h

EXEMPLE DÉTAILLÉ:
  Données:
    Coolant: RP-1 à 350 K
    ρ = 780 kg/m³
    μ = 0.0008 Pa·s
    Cp = 2100 J/kg·K
    k = 0.12 W/m·K
    v = 25 m/s
    D_h = 3 mm = 0.003 m

  Calculs:
    Re = ρ×v×D_h/μ = 780×25×0.003/0.0008 = 73,125
    Pr = μ×Cp/k = 0.0008×2100/0.12 = 14.0
    Nu = 0.023 × 73125^0.8 × 14.0^0.4
    Nu = 0.023 × 8,547 × 2.92 = 573
    h_c = 573 × 0.12 / 0.003 = 22,920 W/m²·K

CORRECTIONS POUR CAS PARTICULIERS:

a) Correction pour L/D court (effets d'entrée):
   Nu_corrigé = Nu × (1 + (D/L)^0.7)
   
b) Correction pour T_paroi ≠ T_bulk:
   Nu_corrigé = Nu × (μ_bulk/μ_paroi)^0.14
   
c) Correction pour canaux non-circulaires:
   Utiliser D_h hydraulique, mais précision réduite.


5.2 CORRÉLATION DE GNIELINSKI
───────────────────────────────────────────────────────────────

Plus précise que Dittus-Boelter, surtout en régime transitoire.
Publiée par V. Gnielinski en 1976.

ÉQUATION PRINCIPALE:

        (f/8) × (Re - 1000) × Pr
  Nu = ─────────────────────────────────────────
        1 + 12.7 × (f/8)^0.5 × (Pr^(2/3) - 1)

Où f est le facteur de frottement de Darcy:

  f = (0.79 × ln(Re) - 1.64)^(-2)    [Équation de Petukhov]

Ou avec l'équation explicite de Colebrook-White simplifiée:

  f = 0.316 × Re^(-0.25)    [Équation de Blasius, Re < 10⁵]

CONDITIONS DE VALIDITÉ:
  ┌────────────────────────────────────────────────────────────┐
  │ • 2300 < Re < 5×10⁶                                        │
  │ • 0.5 < Pr < 2000                                          │
  │ • Plus précise que Dittus-Boelter                          │
  │ • Valide aussi en régime transitoire (Re > 2300)           │
  │ • Propriétés évaluées à T_bulk                             │
  └────────────────────────────────────────────────────────────┘

EXEMPLE DÉTAILLÉ:
  Reprenons l'exemple précédent (RP-1, Re = 73,125, Pr = 14.0)

  Calculs:
    f = (0.79×ln(73125) - 1.64)^(-2)
    f = (0.79×11.2 - 1.64)^(-2)
    f = (8.85 - 1.64)^(-2)
    f = 7.21^(-2) = 0.0192

    Numérateur = (0.0192/8) × (73125-1000) × 14.0
                = 0.0024 × 72125 × 14.0 = 2424

    Dénominateur = 1 + 12.7 × (0.0024)^0.5 × (14.0^0.667 - 1)
                 = 1 + 12.7 × 0.049 × (5.19 - 1)
                 = 1 + 12.7 × 0.049 × 4.19
                 = 1 + 2.61 = 3.61

    Nu = 2424 / 3.61 = 671

    h_c = 671 × 0.12 / 0.003 = 26,840 W/m²·K

COMPARAISON:
  Dittus-Boelter: h_c = 22,920 W/m²·K
  Gnielinski:     h_c = 26,840 W/m²·K (17% plus élevé)

Gnielinski est généralement plus précise (+/-10% vs +/-25%).


5.3 RÉGIME LAMINAIRE (Re < 2300)
───────────────────────────────────────────────────────────────

⚠️ À ÉVITER DANS LES MOTEURS-FUSÉES!
Le transfert thermique est très faible en laminaire.

CAS DU FLUX CONSTANT:
  Nu = 4.36 (tube circulaire)
  Nu = 3.66 (température de paroi constante)

POUR CANAUX RECTANGULAIRES:
  ┌────────────────┬───────────────────────────────────────────┐
  │ Rapport a/b    │ Nu (flux constant)                        │
  ├────────────────┼───────────────────────────────────────────┤
  │ 1.0 (carré)    │ 3.61                                      │
  │ 2.0            │ 4.12                                      │
  │ 4.0            │ 5.35                                      │
  │ 8.0            │ 6.49                                      │
  │ ∞ (plaques)    │ 8.24                                      │
  └────────────────┴───────────────────────────────────────────┘

CONSÉQUENCE:
En laminaire: h_c ≈ 100-500 W/m²·K seulement!
C'est 10 à 100 fois moins qu'en turbulent.

→ Toujours concevoir pour Re > 10,000 minimum.


5.4 RÉGIME TRANSITOIRE (2300 < Re < 10000)
───────────────────────────────────────────────────────────────

Zone difficile à prédire avec précision.

APPROCHE RECOMMANDÉE:
  Utiliser Gnielinski (valide dès Re > 2300).

ALTERNATIVE - Interpolation:
  Nu = Nu_lam + (Nu_turb - Nu_lam) × ((Re - 2300)/(10000 - 2300))

RECOMMANDATION:
  Éviter cette zone! Concevoir pour Re > 10,000.


5.5 ÉBULLITION SOUS-REFROIDIE (SUBCOOLED BOILING)
───────────────────────────────────────────────────────────────

Si T_paroi > T_saturation mais T_bulk < T_saturation:
  → Formation de bulles à la paroi
  → Les bulles se condensent dans le cœur du fluide
  → Transfert thermique AMÉLIORÉ!

CORRÉLATION DE CHEN (1966):
  h_total = h_convection + h_ébullition

  h_ébullition = S × h_nucleation

Où S est un facteur de suppression tenant compte de la 
turbulence qui inhibe la nucléation.

AVANTAGES:
  ✅ h peut augmenter de 2 à 5 fois
  ✅ Utilisé intentionnellement dans certains moteurs

RISQUES:
  ❌ Si T_bulk approche T_sat → ébullition en masse
  ❌ DNB (Departure from Nucleate Boiling) → destruction
  ❌ Instabilités hydrauliques possibles


5.6 EFFETS DE LA GÉOMÉTRIE DES CANAUX
───────────────────────────────────────────────────────────────

La géométrie des canaux influence fortement h_c.

TYPES DE CANAUX COURANTS:
  ┌────────────────────────────────────────────────────────────┐
  │                                                            │
  │  ┌──┐  ┌──┐  ┌──┐     Canaux rectangulaires               │
  │  │  │  │  │  │  │     (fraisage ou impression 3D)         │
  │  │  │  │  │  │  │                                          │
  │  └──┘  └──┘  └──┘                                          │
  │                                                            │
  │  ╭──╮  ╭──╮  ╭──╮     Canaux circulaires                  │
  │  │  │  │  │  │  │     (perçage ou tubes)                  │
  │  ╰──╯  ╰──╯  ╰──╯                                          │
  │                                                            │
  │  /\/\/\/\/\/\/\/\     Canaux hélicoïdaux                  │
  │  \/\/\/\/\/\/\/\/     (meilleur mélange)                  │
  │                                                            │
  └────────────────────────────────────────────────────────────┘

DIAMÈTRE HYDRAULIQUE:
  Canal rectangulaire:  D_h = 4×w×h / (2w + 2h) = 2wh/(w+h)
  Canal circulaire:     D_h = D
  Anneau:               D_h = D_ext - D_int

EFFET DU RAPPORT D'ASPECT (h/w):
  ┌────────────────┬───────────────────────────────────────────┐
  │ h/w            │ Effet                                     │
  ├────────────────┼───────────────────────────────────────────┤
  │ h/w ≈ 1        │ Optimal pour h_c                          │
  │ h/w > 3        │ Canaux étroits, h_c réduit aux coins      │
  │ h/w < 0.3      │ Canaux larges/plats, efficace             │
  └────────────────┴───────────────────────────────────────────┘

EFFET DU NOMBRE DE CANAUX:
  Plus de canaux → Plus petits D_h → Re plus bas MAIS D_h plus petit
  
  h_c ∝ Nu × k / D_h
  
  Si D_h ↓ de moitié:
    - Re ↓ de moitié
    - Nu ↓ d'environ 40% (∝ Re^0.8)
    - Mais D_h ↓ de 50%
    - Net: h_c ↑ d'environ 20%

OPTIMISATION:
  Compromis entre:
  - h_c élevé (petits canaux)
  - Pertes de charge acceptables (grands canaux)
  - Fabricabilité (dépend du procédé)


5.7 PERTES DE CHARGE DANS LES CANAUX
───────────────────────────────────────────────────────────────

Les pertes de charge sont liées au transfert thermique:
  Plus de turbulence → meilleur h_c MAIS plus de ΔP

ÉQUATION DE DARCY-WEISBACH:
            f × L × ρ × v²
  ΔP = ─────────────────────
             2 × D_h

Où:
  f = facteur de frottement (Darcy)
  L = longueur du canal [m]
  ρ = masse volumique [kg/m³]
  v = vitesse [m/s]
  D_h = diamètre hydraulique [m]

FACTEUR DE FROTTEMENT:
  Laminaire:    f = 64/Re
  Turbulent:    f ≈ 0.316 × Re^(-0.25)  (Blasius)
  Turbulent:    f = (0.79×ln(Re) - 1.64)^(-2)  (Petukhov)

ORDRES DE GRANDEUR:
  ┌────────────────────┬──────────────────────────────────┐
  │ Configuration      │ ΔP typique (bar)                 │
  ├────────────────────┼──────────────────────────────────┤
  │ RP-1 dans canaux   │ 10 - 50                          │
  │ LH2 dans canaux    │ 5 - 30                           │
  │ LOX dans canaux    │ 10 - 40                          │
  └────────────────────┴──────────────────────────────────┘

PUISSANCE DE POMPAGE:
  P_pompe = ΔP × Q = ΔP × A × v

Cette puissance est "perdue" et doit être fournie par la 
turbopompe → impact sur les performances globales.


5.8 VALEURS TYPIQUES DE h_c - TABLEAU COMPLET
───────────────────────────────────────────────────────────────

  ┌────────────────┬──────────────┬───────────┬───────────────┐
  │ Coolant        │ T (K)        │ v (m/s)   │ h_c (W/m²·K)  │
  ├────────────────┼──────────────┼───────────┼───────────────┤
  │ LH2            │ 25           │ 50        │ 50,000-150,000│
  │ LH2            │ 30           │ 100       │ 80,000-200,000│
  │ LOX            │ 100          │ 20        │ 15,000-40,000 │
  │ LOX            │ 100          │ 40        │ 25,000-60,000 │
  │ CH4            │ 150          │ 20        │ 10,000-30,000 │
  │ CH4            │ 150          │ 40        │ 18,000-50,000 │
  │ RP-1           │ 300          │ 15        │ 5,000-15,000  │
  │ RP-1           │ 350          │ 25        │ 10,000-25,000 │
  │ RP-1           │ 400          │ 30        │ 15,000-35,000 │
  │ C2H5OH         │ 300          │ 20        │ 8,000-20,000  │
  │ H2O            │ 350          │ 10        │ 15,000-40,000 │
  │ H2O            │ 350          │ 30        │ 30,000-80,000 │
  │ N2H4           │ 320          │ 15        │ 8,000-22,000  │
  └────────────────┴──────────────┴───────────┴───────────────┘

CLASSEMENT PAR CAPACITÉ DE REFROIDISSEMENT:
  1. LH2 (meilleur! Cp très élevé, k élevé, μ faible)
  2. H2O (excellent mais T_boil basse)
  3. LOX (bon mais corrosif, limites de T)
  4. CH4 (très bon, propre, compatible)
  5. C2H5OH (bon, simple)
  6. RP-1 (correct mais cokéfaction)
  7. N2H4 (toxique, éviter si possible)


6. ÉPAISSEUR CRITIQUE, SERVICE ET ABLATION
═══════════════════════════════════════════════════════════════

Cette section traite des critères d'épaisseur et du 
phénomène d'ablation pour les parois trop épaisses.


6.1 ÉPAISSEUR CRITIQUE DE FUSION (e_melt)
───────────────────────────────────────────────────────────────

L'épaisseur critique est l'épaisseur MAXIMALE pour laquelle 
T_wall_hot reste inférieure à T_melt (température de fusion).

DÉRIVATION:
  En régime permanent: T_wall_hot = T_wall_cold + q×e/k
  
  Pour éviter la fusion: T_wall_hot ≤ T_melt
  
  Donc: T_wall_cold + q×e/k ≤ T_melt
  
  Résolvant pour e:
  
         k × (T_melt - T_wall_cold)
  e ≤ ───────────────────────────────
                    q

FORMULE FINALE:
  ┌─────────────────────────────────────────────────────────┐
  │                                                         │
  │              k × (T_melt - T_wall_cold)                 │
  │   e_melt = ─────────────────────────────────            │
  │                        q                                │
  │                                                         │
  └─────────────────────────────────────────────────────────┘

INTERPRÉTATION:
  - Si e < e_melt: la paroi NE FOND PAS ✅
  - Si e = e_melt: T_wall_hot = T_melt exactement (limite)
  - Si e > e_melt: la surface FOND ❌

FACTEURS FAVORABLES (e_melt élevé = plus de marge):
  ✅ k élevé (bonne conductivité)
  ✅ T_melt élevé (matériau réfractaire)
  ✅ T_wall_cold bas (bon refroidissement)
  ✅ q faible (position loin du col)

EXEMPLE NUMÉRIQUE - CuCr:
  k = 320 W/m·K
  T_melt = 1350 K
  T_wall_cold = 600 K
  q = 25 MW/m² (au col)

  e_melt = 320 × (1350 - 600) / 25×10⁶
  e_melt = 320 × 750 / 25×10⁶
  e_melt = 240,000 / 25×10⁶
  e_melt = 0.0096 m = 9.6 mm

  → La paroi peut faire jusqu'à 9.6 mm avant de fondre.

EXEMPLE - COMPARAISON MATÉRIAUX:
  Même conditions: T_wc = 600 K, q = 25 MW/m²
  
  ┌──────────────────┬────────┬─────────┬──────────────────┐
  │ Matériau         │ k      │ T_melt  │ e_melt (mm)      │
  ├──────────────────┼────────┼─────────┼──────────────────┤
  │ Cuivre           │ 385    │ 1358 K  │ 11.7             │
  │ CuCr             │ 320    │ 1350 K  │ 9.6              │
  │ Inconel 718      │ 11.4   │ 1609 K  │ 0.46             │
  │ Inox 316L        │ 16.3   │ 1673 K  │ 0.70             │
  │ AlSi10Mg         │ 130    │ 870 K   │ 1.4              │
  │ Niobium          │ 53.7   │ 2750 K  │ 4.6              │
  │ Molybdène        │ 138    │ 2896 K  │ 12.7             │
  │ Tungstène        │ 173    │ 3695 K  │ 21.4             │
  └──────────────────┴────────┴─────────┴──────────────────┘

OBSERVATIONS:
  - Cuivre et alliages: e_melt ≈ 10 mm (excellent)
  - Superalliages: e_melt < 1 mm (faible conductivité!)
  - Réfractaires: e_melt élevé grâce à T_melt très haut


6.2 ÉPAISSEUR DE SERVICE (e_max)
───────────────────────────────────────────────────────────────

En pratique, on ne veut pas atteindre T_melt mais rester 
en dessous de T_max_service pour éviter:
  - Perte de propriétés mécaniques
  - Fluage (déformation lente sous charge)
  - Oxydation accélérée
  - Changements métallurgiques

FORMULE:

         k × (T_max_service - T_wall_cold)
  e_max = ───────────────────────────────────
                        q

TEMPÉRATURES MAX DE SERVICE:
  ┌──────────────────┬──────────────────────────────────────┐
  │ Matériau         │ T_max_service (K) et raison          │
  ├──────────────────┼──────────────────────────────────────┤
  │ Cuivre           │ 800-900 K (ramollissement)           │
  │ CuCr             │ 1000-1050 K (perte de dureté)        │
  │ CuCrZr           │ 1050-1100 K                          │
  │ GRCop-84         │ 1100-1200 K (excellent!)             │
  │ Inconel 718      │ 1100-1200 K (fluage)                 │
  │ Inconel 625      │ 1150-1250 K                          │
  │ Inox 316L        │ 1000-1100 K                          │
  │ AlSi10Mg         │ 500-573 K (très bas!)                │
  │ Niobium          │ 2000-2200 K (oxydation si pas vide)  │
  │ Molybdène        │ 2200-2400 K                          │
  │ Tungstène        │ 2800-3000 K                          │
  └──────────────────┴──────────────────────────────────────┘

MARGE DE SÉCURITÉ:
  Typiquement: T_design = T_max_service - 50 à 100 K

EXEMPLE - CuCr:
  k = 320 W/m·K
  T_max = 1050 K
  T_wall_cold = 600 K
  q = 25 MW/m²

  e_max = 320 × (1050 - 600) / 25×10⁶
  e_max = 320 × 450 / 25×10⁶
  e_max = 5.76 mm

  → Épaisseur max pour rester sous T_max = 5.76 mm


6.3 PROCESSUS D'ABLATION
───────────────────────────────────────────────────────────────

Que se passe-t-il si l'épaisseur initiale e₀ > e_melt?

RÉPONSE: La surface fond et s'érode jusqu'à atteindre e_melt.

MÉCANISME PHYSIQUE DÉTAILLÉ:

  INSTANT t = 0 (allumage):
  ┌────────────────────────────────────────────────────────────┐
  │  Gaz chauds arrivent                                       │
  │  T_wall_hot commence à monter rapidement                   │
  │  (régime transitoire)                                      │
  └────────────────────────────────────────────────────────────┘
           ↓
  INSTANT t = τ (temps caractéristique):
  ┌────────────────────────────────────────────────────────────┐
  │  T_wall_hot atteint le régime "quasi-permanent"            │
  │  Si e₀ > e_melt: T_wall_hot > T_melt                       │
  │  → La surface commence à FONDRE                            │
  └────────────────────────────────────────────────────────────┘
           ↓
  PHASE D'ABLATION:
  ┌────────────────────────────────────────────────────────────┐
  │  • Métal fondu à la surface                                │
  │  • Gouttelettes emportées par le flux gazeux               │
  │  • Épaisseur diminue progressivement                       │
  │  • T_wall_hot reste ≈ T_melt (latent heat)                 │
  └────────────────────────────────────────────────────────────┘
           ↓
  ÉQUILIBRE (t >> τ):
  ┌────────────────────────────────────────────────────────────┐
  │  e final = e_melt                                          │
  │  T_wall_hot = T_melt                                       │
  │  Plus de fusion, état stable                               │
  └────────────────────────────────────────────────────────────┘


6.4 ÉPAISSEUR SACRIFICIELLE ET MASSE PERDUE
───────────────────────────────────────────────────────────────

DÉFINITION:

  e_sacrificielle = e₀ - e_melt   (si e₀ > e_melt)
  e_sacrificielle = 0             (si e₀ ≤ e_melt)

C'est l'épaisseur qui va fondre et être emportée.

MASSE PERDUE PAR UNITÉ DE SURFACE:

  Δm/A = ρ_métal × e_sacrificielle   [kg/m²]

MASSE TOTALE PERDUE:

  Δm = ρ_métal × A_surface × e_sacrificielle   [kg]

EXEMPLE NUMÉRIQUE:
  Données:
    Matériau: CuCr
    ρ = 8900 kg/m³
    e₀ = 12 mm (épaisseur initiale)
    e_melt = 9.6 mm (calculé précédemment)
    A_surface = 0.05 m² (surface au col)

  Calculs:
    e_sacrificielle = 12 - 9.6 = 2.4 mm = 0.0024 m
    Δm = 8900 × 0.05 × 0.0024 = 1.07 kg

  → 1.07 kg de cuivre va fondre et être éjecté!


6.5 TEMPS D'ABLATION
───────────────────────────────────────────────────────────────

Combien de temps dure l'ablation?

BILAN ÉNERGÉTIQUE:
L'énergie pour fondre e_sac d'épaisseur sur 1 m² est:

  E_fusion = ρ × e_sac × (Cp × (T_melt - T₀) + L_fusion)

Où L_fusion est la chaleur latente de fusion.

CHALEUR LATENTE DE FUSION:
  ┌──────────────────┬──────────────────────────────────────┐
  │ Matériau         │ L_fusion (kJ/kg)                     │
  ├──────────────────┼──────────────────────────────────────┤
  │ Cuivre           │ 205                                  │
  │ Aluminium        │ 397                                  │
  │ Fer/Acier        │ 247                                  │
  │ Nickel           │ 298                                  │
  │ Niobium          │ 285                                  │
  │ Molybdène        │ 390                                  │
  │ Tungstène        │ 192                                  │
  └──────────────────┴──────────────────────────────────────┘

FLUX DISPONIBLE POUR LA FUSION:
Le flux "excédentaire" qui cause la fusion est:

  q_fusion = q_entrant - q_évacué_à_T_melt

TEMPS D'ABLATION (approximation):

  t_ablation ≈ ρ × e_sac × L_fusion / q_fusion

En pratique: quelques secondes à quelques dizaines de secondes.


6.6 QUAND L'ABLATION EST-ELLE ACCEPTABLE?
───────────────────────────────────────────────────────────────

L'ablation peut être:
  - ACCEPTÉE volontairement (moteurs ablatifs)
  - TOLÉRÉE accidentellement
  - CATASTROPHIQUE

CAS 1 - MOTEURS ABLATIFS (acceptable):
  ┌────────────────────────────────────────────────────────────┐
  │ • Conception prévue pour l'ablation                        │
  │ • Matériau sacrificiel (phénolique, silice)               │
  │ • Durée de fonctionnement limitée (quelques secondes)      │
  │ • Pas de refroidissement régénératif                       │
  │ • Simple, léger, fiable                                    │
  │ • Exemple: moteurs de missiles, boosters                   │
  └────────────────────────────────────────────────────────────┘

CAS 2 - ABLATION TOLÉRÉE:
  ┌────────────────────────────────────────────────────────────┐
  │ • Légère sur-épaisseur de sécurité                         │
  │ • Ablation minime (< 0.5 mm)                               │
  │ • Moteur reste fonctionnel après ablation                  │
  │ • Vérifié par calcul et tests                              │
  └────────────────────────────────────────────────────────────┘

CAS 3 - ABLATION CATASTROPHIQUE (à éviter!):
  ┌────────────────────────────────────────────────────────────┐
  │ ❌ Percement de la paroi → fuite de gaz chauds             │
  │ ❌ Contamination du coolant par métal fondu                │
  │ ❌ Modification de la géométrie → perte de performances    │
  │ ❌ Débris métalliques endommageant l'injecteur             │
  │ ❌ Explosion possible!                                      │
  └────────────────────────────────────────────────────────────┘


6.7 DIMENSIONNEMENT POUR ÉVITER L'ABLATION
───────────────────────────────────────────────────────────────

RÈGLE DE CONCEPTION:

  e_design < e_max < e_melt

Où:
  e_design = épaisseur choisie
  e_max = épaisseur pour T_wall_hot = T_max_service
  e_melt = épaisseur pour T_wall_hot = T_melt

MARGES RECOMMANDÉES:

  e_design = 0.7 à 0.8 × e_max

Cette marge couvre:
  - Incertitudes sur h_g (±20-30%)
  - Variations locales de flux
  - Transitoires (démarrage/arrêt)
  - Vieillissement du matériau

PROCÉDURE DE DIMENSIONNEMENT:
  1. Calculer q_max (au col)
  2. Choisir le matériau (k, T_melt, T_max)
  3. Calculer e_melt et e_max
  4. Choisir e_design avec marge
  5. Vérifier résistance mécanique (pression)
  6. Vérifier stress thermique
  7. Itérer si nécessaire


6.8 CARTE THERMIQUE ET VARIATION AXIALE
───────────────────────────────────────────────────────────────

Le flux q varie le long du moteur:
  - Maximum au COL
  - Décroissant vers la chambre et le divergent

CONSÉQUENCE:
  e_melt et e_max VARIENT aussi le long du moteur!

APPROCHE DE CONCEPTION:
  ┌────────────────────────────────────────────────────────────┐
  │ OPTION 1: Épaisseur constante                              │
  │  + Simple à fabriquer                                      │
  │  - Sur-dimensionné dans chambre et divergent               │
  │  - Sous-dimensionné potentiel au col                       │
  ├────────────────────────────────────────────────────────────┤
  │ OPTION 2: Épaisseur variable                               │
  │  + Optimisé thermiquement                                  │
  │  + Masse minimale                                          │
  │  - Fabrication plus complexe                               │
  │  - Usinage ou impression 3D                                │
  ├────────────────────────────────────────────────────────────┤
  │ OPTION 3: Matériau variable (hybride)                      │
  │  + Optimal pour chaque zone                                │
  │  + CuCr au col, Inconel dans divergent, etc.               │
  │  - Joints complexes                                        │
  │  - Dilatation différentielle                               │
  └────────────────────────────────────────────────────────────┘

PROFIL TYPIQUE D'UN MOTEUR MODERNE:
  - Chambre: e = 3-5 mm (CuCr ou GRCop)
  - Convergent/Col: e = 1.5-3 mm (minimum pour q max)
  - Divergent: e = 2-4 mm (CuCr) ou transition vers acier


7. PROPRIÉTÉS DES MATÉRIAUX POUR MOTEURS-FUSÉES
═══════════════════════════════════════════════════════════════

Cette section détaille les matériaux utilisés pour les parois 
de chambres de combustion et tuyères à refroidissement régénératif.


7.1 TABLEAU RÉCAPITULATIF DES PROPRIÉTÉS
───────────────────────────────────────────────────────────────

  ┌──────────────────┬───────┬─────────┬─────────┬─────────┐
  │ Matériau         │k W/m·K│T_melt K │T_max K  │ρ kg/m³  │
  ├──────────────────┼───────┼─────────┼─────────┼─────────┤
  │ Cuivre (Cu)      │  385  │  1358   │   900   │  8960   │
  │ CuCr (C18200)    │  320  │  1350   │  1050   │  8900   │
  │ CuCrZr (C18150)  │  315  │  1355   │  1100   │  8890   │
  │ GRCop-84 (NASA)  │  298  │  1350   │  1200   │  8870   │
  │ GRCop-42         │  310  │  1355   │  1150   │  8850   │
  │ AlSi10Mg (SLM)   │  130  │   870   │   573   │  2670   │
  │ Al 6061-T6       │  167  │   925   │   573   │  2700   │
  │ Inconel 718      │ 11.4  │  1609   │  1200   │  8190   │
  │ Inconel 625      │  9.8  │  1623   │  1250   │  8440   │
  │ Inconel X-750    │ 12.0  │  1620   │  1150   │  8280   │
  │ Haynes 230       │  8.9  │  1635   │  1350   │  8970   │
  │ Haynes 188       │ 10.4  │  1635   │  1320   │  8980   │
  │ Inox 316L        │ 16.3  │  1673   │  1100   │  8000   │
  │ Inox 304L        │ 16.2  │  1673   │  1050   │  7900   │
  │ Ti-6Al-4V        │  6.7  │  1933   │   700   │  4430   │
  │ Niobium (Nb)     │ 53.7  │  2750   │  2200   │  8570   │
  │ C103 (Nb alloy)  │ 44.2  │  2685   │  2000   │  8860   │
  │ Molybdène (Mo)   │  138  │  2896   │  2400   │ 10280   │
  │ TZM (Mo alloy)   │  120  │  2895   │  2500   │ 10220   │
  │ Tungstène (W)    │  173  │  3695   │  3000   │ 19300   │
  │ W-Re (W alloy)   │  100  │  3450   │  2800   │ 19700   │
  │ Rhénium (Re)     │ 47.9  │  3459   │  2800   │ 21020   │
  │ Tantale (Ta)     │ 57.5  │  3290   │  2600   │ 16650   │
  │ Graphite         │  120  │  3900*  │  3500   │  2200   │
  │ C/C Composite    │ 50-150│  3900*  │  3200   │  1800   │
  │ SiC (CVD)        │  120  │  3100*  │  2000   │  3210   │
  └──────────────────┴───────┴─────────┴─────────┴─────────┘
  * Sublime au lieu de fondre


7.2 ALLIAGES DE CUIVRE - LES CHAMPIONS DU REFROIDISSEMENT
───────────────────────────────────────────────────────────────

Les alliages de cuivre sont les matériaux de choix pour les 
zones à haut flux thermique (chambre, col) grâce à leur 
excellente conductivité thermique.

A) CUIVRE PUR (Cu - C10200, OFHC)

  Composition: Cu > 99.95%
  
  Propriétés:
    k = 385-401 W/m·K (le meilleur!)
    T_melt = 1358 K (1085°C)
    T_max = 800-900 K (ramollissement)
    σ_yield @ 20°C = 70 MPa (très faible)
    σ_yield @ 500°C = 35 MPa
  
  ✅ Avantages:
    - Conductivité maximale
    - Facile à usiner
    - Bon marché
  
  ❌ Inconvénients:
    - Très faible résistance mécanique
    - Ramollit rapidement à T > 500 K
    - Fluage important
  
  Utilisation:
    - Rarement seul pour moteurs haute pression
    - Parfois pour petits moteurs < 10 bar
    - Inserts ou revêtements

B) CUIVRE-CHROME (CuCr - C18200)

  Composition: Cu + 0.6-1.2% Cr
  
  Propriétés:
    k = 315-324 W/m·K
    T_melt = 1350 K
    T_max = 1000-1050 K
    σ_yield @ 20°C = 310-450 MPa (traité)
    σ_yield @ 500°C = 180 MPa
    E = 130 GPa
    α = 16.5 × 10⁻⁶ /K
  
  ✅ Avantages:
    - Excellent compromis k / résistance
    - Très bien maîtrisé industriellement
    - Soudable (TIG, EBW, FSW)
    - Disponible et économique
  
  ❌ Inconvénients:
    - Perd sa dureté si surchauffe > 800 K
    - Recristallisation possible
  
  Traitement thermique:
    - Mise en solution: 980°C, trempe eau
    - Vieillissement: 450-500°C, 2-4h
  
  Utilisation:
    - Merlin (SpaceX)
    - RS-25 SSME (NASA/Aerojet)
    - Vulcain (ESA)
    - RD-180, RD-191 (Energomash)
    - TRÈS COURANT!

C) CUIVRE-CHROME-ZIRCONIUM (CuCrZr - C18150)

  Composition: Cu + 0.5-1.5% Cr + 0.05-0.15% Zr
  
  Propriétés:
    k = 310-320 W/m·K
    T_melt = 1355 K
    T_max = 1050-1100 K
    σ_yield @ 20°C = 380-500 MPa
    σ_yield @ 600°C = 220 MPa
  
  ✅ Avantages:
    - Meilleure tenue à chaud que CuCr
    - Résistance au fluage améliorée
    - Zr stabilise les précipités de Cr
  
  ❌ Inconvénients:
    - Plus cher que CuCr
    - Traitement thermique critique
  
  Utilisation:
    - RD-170/171 (Energomash)
    - Moteurs russes haute performance
    - Réacteurs de fusion (ITER)

D) GRCop-84 (NASA Glenn Research Center)

  Composition: Cu + 8% Cr + 4% Nb (nano-dispersions)
  
  Propriétés:
    k = 285-300 W/m·K
    T_melt = 1350 K
    T_max = 1150-1200 K
    σ_yield @ 20°C = 250 MPa
    σ_yield @ 800°C = 150 MPa (EXCELLENT!)
    Résistance au fluage: 100× meilleure que CuCr
  
  ✅ Avantages:
    - Excellente résistance à haute T
    - Résistance au fluage exceptionnelle
    - Stable microstructuralement
    - Idéal pour impression 3D (SLM/DMLS)
  
  ❌ Inconvénients:
    - Développé par NASA, accès limité
    - Fabrication spécialisée
    - Plus cher
  
  Fabrication:
    - Atomisation plasma
    - Impression 3D (SLM avec laser 400W+)
    - HIP (Hot Isostatic Pressing)
  
  Utilisation:
    - RS-25 upgrades (SLS)
    - Relativity Space (Terran 1, Aeon)
    - Virgin Orbit (NewtonThree)
    - Aerojet Rocketdyne (RL10 upgrades)

E) GRCop-42 (variante)

  Composition: Cu + 4% Cr + 2% Nb
  
  Propriétés:
    k = 305-315 W/m·K (meilleur que GRCop-84)
    T_max = 1100-1150 K
    Compromis entre k et résistance haute T
  
  Utilisation:
    - Applications où k est prioritaire
    - Développement en cours


7.3 SUPERALLIAGES BASE NICKEL
───────────────────────────────────────────────────────────────

Les superalliages sont utilisés pour les zones moins sollicitées 
thermiquement mais nécessitant haute résistance mécanique.

A) INCONEL 718

  Composition: Ni-52%, Cr-19%, Fe-18%, Nb-5%, Mo-3%
  
  Propriétés:
    k = 11.4 W/m·K (faible!)
    T_melt = 1609 K
    T_max = 1100-1200 K
    σ_yield @ 20°C = 1035-1240 MPa (très élevé!)
    σ_yield @ 650°C = 1000 MPa
    E = 200 GPa
  
  ✅ Avantages:
    - Excellente résistance mécanique
    - Bonne résistance à l'oxydation
    - Soudable
    - Bien maîtrisé pour impression 3D
  
  ❌ Inconvénients:
    - Conductivité très faible (11× moins que CuCr)
    - Limite thermique malgré T_melt élevé
    - Usinage difficile
  
  Utilisation:
    - Structures de tuyères
    - Brides, collecteurs
    - Divergent (partie froide)
    - Chambres basse pression

B) INCONEL 625

  Composition: Ni-62%, Cr-22%, Mo-9%, Nb-3.5%
  
  Propriétés:
    k = 9.8 W/m·K
    T_melt = 1623 K
    T_max = 1200-1250 K
    σ_yield @ 20°C = 460-760 MPa
    Excellente résistance à la corrosion
  
  ✅ Avantages:
    - Meilleure résistance corrosion que 718
    - Soudable sans traitement post-soudure
    - Bon pour environnements agressifs
  
  Utilisation:
    - Divergent de tuyères
    - Environnements corrosifs
    - Propergols agressifs (N2O4, HNO3)

C) HAYNES 230

  Composition: Ni-57%, Cr-22%, W-14%, Mo-2%
  
  Propriétés:
    k = 8.9 W/m·K
    T_melt = 1635 K
    T_max = 1300-1350 K (excellent!)
    σ_yield @ 20°C = 390 MPa
    Résistance à l'oxydation exceptionnelle
  
  Utilisation:
    - Tuyères haute température
    - Applications spatiales réutilisables
    - Turbines, échangeurs

D) HAYNES 188

  Composition: Co-39%, Ni-22%, Cr-22%, W-14%
  
  Propriétés:
    k = 10.4 W/m·K
    T_max = 1300-1320 K
    Excellente résistance à l'oxydation
  
  Utilisation:
    - Tuyères pour moteurs réutilisables
    - Applications haute température longue durée


7.4 ALLIAGES D'ALUMINIUM
───────────────────────────────────────────────────────────────

Utilisés pour les petits moteurs ou prototypes grâce à leur 
légèreté et facilité d'usinage/impression 3D.

A) AlSi10Mg (impression 3D)

  Composition: Al + 10% Si + 0.3% Mg
  
  Propriétés:
    k = 120-140 W/m·K
    T_melt = 870 K (597°C) - TRÈS BAS!
    T_max = 473-573 K (200-300°C)
    ρ = 2670 kg/m³ (léger!)
    σ_yield @ 20°C = 230-280 MPa (SLM)
  
  ✅ Avantages:
    - Très léger (3× moins que CuCr)
    - Excellente imprimabilité 3D
    - Conductivité correcte
    - Économique
    - Prototypage rapide
  
  ❌ Inconvénients:
    - T_max TRÈS BASSE! (~300°C)
    - Fond facilement
    - Limité aux faibles flux
    - Résistance chute rapidement avec T
  
  ⚠️ ATTENTION:
    SEULEMENT pour moteurs faible pression/flux
    ou zones très bien refroidies!
  
  Utilisation:
    - Prototypes
    - Petits moteurs (< 5 kN)
    - Moteurs basse pression
    - Zones froides (divergent loin)

B) Al 6061-T6

  Composition: Al + 1% Mg + 0.6% Si + 0.3% Cu
  
  Propriétés:
    k = 167 W/m·K
    T_melt = 925 K
    T_max = 473-573 K
    σ_yield = 275 MPa
  
  Utilisation:
    - Structures, brides
    - Pas pour parois chaudes!


7.5 MÉTAUX RÉFRACTAIRES
───────────────────────────────────────────────────────────────

Pour les tuyères à rayonnement ou hautes températures extrêmes.
Utilisés principalement pour les divergents non refroidis.

A) NIOBIUM (Nb) et C103

  Nb pur:
    k = 53.7 W/m·K
    T_melt = 2750 K
    T_max = 2000-2200 K (sous vide!)
    ρ = 8570 kg/m³
  
  C103 (Nb-10Hf-1Ti):
    k = 44 W/m·K
    T_melt = 2685 K
    T_max = 1800-2000 K
    σ_yield @ 20°C = 310 MPa
    σ_yield @ 1200°C = 140 MPa
  
  ⚠️ OXYDATION:
    Nb s'oxyde catastrophiquement à T > 700 K dans l'air!
    → Utilisable uniquement dans le VIDE spatial
    → Ou avec revêtement siliciure (MoSi2, WSi2)
  
  Revêtements protecteurs:
    - R512E (Si-20Cr-20Fe)
    - R512A (Si-20Cr-5Ti-5Fe)
    - Durée: quelques heures à 1600 K
  
  Utilisation:
    - Divergents de moteurs spatiaux
    - Apollo LM Descent Engine
    - RL10 (extension de tuyère)
    - Moteurs d'apogée

B) MOLYBDÈNE (Mo) et TZM

  Mo pur:
    k = 138 W/m·K (excellent pour réfractaire!)
    T_melt = 2896 K
    T_max = 2200-2400 K
    ρ = 10280 kg/m³
  
  TZM (Mo-0.5Ti-0.08Zr):
    k = 115-125 W/m·K
    T_melt = 2895 K
    T_max = 2300-2500 K
    σ_yield @ 20°C = 700 MPa
    σ_yield @ 1000°C = 420 MPa
  
  ⚠️ OXYDATION:
    Forme MoO3 volatil à T > 800 K dans l'air
    → "Peste du molybdène"
    → Vide ou atmosphère inerte obligatoire
  
  Utilisation:
    - Inserts de col (vide spatial)
    - Tuyères haute température
    - Propulsion électrique (résistojets)

C) TUNGSTÈNE (W) et W-Re

  W pur:
    k = 173 W/m·K
    T_melt = 3695 K (le plus haut des métaux!)
    T_max = 2800-3000 K
    ρ = 19300 kg/m³ (très lourd!)
    σ_yield @ 20°C = 700-1000 MPa
  
  W-Re (W + 3-25% Re):
    k = 80-120 W/m·K
    T_melt = 3200-3450 K
    Meilleure ductilité que W pur
    σ_yield @ 1500°C = 300 MPa
  
  ⚠️ CARACTÉRISTIQUES:
    - Très fragile à température ambiante
    - DBTT (ductile-brittle) ≈ 400°C
    - Usinage très difficile (EDM)
    - Oxyde à T > 700 K dans l'air
  
  Utilisation:
    - Inserts de col (cas extrêmes)
    - Propulsion électrique (résistojets, arcjets)
    - Protection thermique

D) RHÉNIUM (Re)

  Propriétés:
    k = 47.9 W/m·K
    T_melt = 3459 K
    T_max = 2600-2800 K
    ρ = 21020 kg/m³ (2ème plus dense)
  
  ✅ Avantages:
    - Ductile à toutes températures
    - Pas de DBTT comme W
    - Excellente résistance au fluage
  
  ❌ Inconvénients:
    - EXTRÊMEMENT cher (~5000 $/kg)
    - Rare (production mondiale: 50 tonnes/an)
    - Lourd
  
  Utilisation:
    - Revêtement sur W ou Ir
    - Applications spatiales critiques
    - Très limité (coût prohibitif)


7.6 MATÉRIAUX CÉRAMIQUES ET COMPOSITES
───────────────────────────────────────────────────────────────

A) GRAPHITE

  Propriétés:
    k = 80-150 W/m·K (selon orientation)
    T_sublime = 3900 K (pas de fusion!)
    T_max = 3200-3500 K (vide)
    ρ = 1800-2200 kg/m³ (léger!)
  
  ⚠️ OXYDATION:
    Brûle à T > 700 K dans l'air!
    → Vide spatial uniquement
    → Ou revêtement SiC
  
  Utilisation:
    - Insertions de col (moteurs solides)
    - Tuyères de rentrée atmosphérique

B) COMPOSITE CARBONE-CARBONE (C/C)

  Propriétés:
    k = 50-150 W/m·K (selon orientation)
    T_max = 3000-3200 K
    ρ = 1600-1900 kg/m³
    σ_tension = 200-400 MPa
  
  ✅ Avantages:
    - Très léger
    - k augmente avec T (!!)
    - Résistance maintenue à haute T
  
  ❌ Inconvénients:
    - Oxydation catastrophique si air
    - Fabrication longue et coûteuse
    - Anisotrope
  
  Utilisation:
    - Navette spatiale (bords d'attaque)
    - Tuyères de moteurs solides
    - Freins d'avions (non-spatial)

C) CARBURE DE SILICIUM (SiC)

  Propriétés:
    k = 120 W/m·K
    T_décompose = 3100 K
    T_max = 1900-2000 K
    ρ = 3210 kg/m³
  
  ✅ Avantages:
    - Résistant à l'oxydation
    - Dur et résistant à l'érosion
  
  Utilisation:
    - Revêtements protecteurs
    - Échangeurs de chaleur


7.7 CRITÈRES DE SÉLECTION DES MATÉRIAUX
───────────────────────────────────────────────────────────────

POUR LA CHAMBRE ET LE COL (flux max):
  
  Priorité 1: k élevé (évacuer la chaleur)
  Priorité 2: T_max adéquat
  Priorité 3: Résistance mécanique
  
  → CHOIX: CuCr, CuCrZr, GRCop-84
  
POUR LE DIVERGENT (flux modéré):
  
  Option A: Refroidissement régénératif
    → CuCr ou transition vers Inconel
  
  Option B: Rayonnement (spatial)
    → Nb/C103, Mo/TZM, ou composites
  
POUR PROTOTYPES/TESTS:
  
  → AlSi10Mg (impression 3D, économique)
  → Durée de vie limitée acceptable

ARBRE DE DÉCISION:

  ┌─ Flux > 20 MW/m² ? ─────────────────────────────────────┐
  │                                                          │
  │ OUI                              NON                     │
  │  │                                │                      │
  │  ↓                                ↓                      │
  │ CuCr/CuCrZr/GRCop              Inconel ou                │
  │ (OBLIGATOIRE)                   matériau économique      │
  │                                                          │
  └──────────────────────────────────────────────────────────┘
  
  ┌─ Réutilisable ? ────────────────────────────────────────┐
  │                                                          │
  │ OUI → GRCop-84 (résistance fluage)                       │
  │ NON → CuCr (économique)                                  │
  │                                                          │
  └──────────────────────────────────────────────────────────┘
  
  ┌─ Impression 3D ? ───────────────────────────────────────┐
  │                                                          │
  │ OUI → GRCop-84 (optimal)                                 │
  │       Inconel 718 (structures)                           │
  │       AlSi10Mg (prototypes)                              │
  │                                                          │
  │ NON → CuCr forgé/usiné (économique)                      │
  │                                                          │
  └──────────────────────────────────────────────────────────┘


7.8 EXEMPLES DE MOTEURS RÉELS
───────────────────────────────────────────────────────────────

MERLIN 1D (SpaceX):
  - Chambre/col: CuCr (usiné)
  - Divergent: Nb-C103 (rayonnement)
  - Épaisseur: 1.5-3 mm
  - Pression: 97 bar

RS-25 / SSME (NASA/Aerojet):
  - Chambre: CuCr (fraisé + électroformé Ni)
  - Col: CuCr
  - Divergent: Inconel 718
  - Canaux: 430 canaux de refroidissement
  - Pression: 206 bar

RAPTOR (SpaceX):
  - Chambre/col: GRCop-84 ou variante (SLM)
  - Fabrication additive
  - Pression: 300+ bar

RD-170/180 (Energomash):
  - Chambre: CuCrZr (brasé)
  - Col: CuCrZr
  - Divergent: Inox + Nb
  - Canaux: tubes enroulés

BE-4 (Blue Origin):
  - Chambre: CuCr ou GRCop
  - Fabrication hybride (SLM + traditionnel)
  - Pression: 135 bar

VULCAIN 2 (ESA):
  - Chambre: CuCr (fraisé)
  - Divergent: Inconel + tubes
  - Pression: 115 bar


8. PROPRIÉTÉS DES COOLANTS - GUIDE COMPLET
═══════════════════════════════════════════════════════════════

Cette section détaille les propriétés thermophysiques des 
fluides utilisés pour le refroidissement régénératif.


8.1 TABLEAU RÉCAPITULATIF DES COOLANTS
───────────────────────────────────────────────────────────────

  ┌──────────────┬────────┬────────┬────────┬────────┬────────┐
  │ Coolant      │Cp J/kg·K│T_boil K│T_crit K│ρ kg/m³ │μ mPa·s │
  ├──────────────┼────────┼────────┼────────┼────────┼────────┤
  │ LH2          │ 14300  │  20.3  │  33.2  │   71   │  0.013 │
  │ LOX          │  1700  │  90.2  │  154.6 │  1141  │  0.19  │
  │ LN2          │  2040  │  77.4  │  126.2 │   808  │  0.16  │
  │ CH4 (LCH4)   │  3500  │  111.7 │  190.6 │   422  │  0.12  │
  │ C2H6 (éthane)│  2500  │  184.6 │  305.3 │   544  │  0.18  │
  │ C3H8 (propane│  2500  │  231.1 │  369.8 │   582  │  0.20  │
  │ RP-1         │  2000  │  490   │  678   │   810  │  1.2   │
  │ Jet-A        │  2100  │  450   │  650   │   800  │  1.5   │
  │ C2H5OH       │  2440  │  351.4 │  514.0 │   789  │  1.1   │
  │ CH3OH        │  2530  │  337.8 │  512.6 │   791  │  0.55  │
  │ N2H4         │  3100  │  387.0 │  653.0 │  1004  │  0.97  │
  │ MMH          │  2900  │  360.5 │  585.0 │   874  │  0.78  │
  │ UDMH         │  2750  │  336.0 │  523.0 │   791  │  0.51  │
  │ H2O          │  4186  │  373.2 │  647.1 │  1000  │  1.0   │
  │ H2O2 (90%)   │  2800  │  423.0 │  730   │  1390  │  1.2   │
  │ NH3          │  4700  │  239.8 │  405.4 │   682  │  0.26  │
  │ N2O          │  1900  │  184.7 │  309.6 │  1220  │  0.14  │
  └──────────────┴────────┴────────┴────────┴────────┴────────┘

Note: Propriétés au point d'ébullition @ 1 bar sauf indication.


8.2 HYDROGÈNE LIQUIDE (LH2) - LE MEILLEUR COOLANT
───────────────────────────────────────────────────────────────

L'hydrogène liquide est le MEILLEUR coolant pour plusieurs raisons:

PROPRIÉTÉS DÉTAILLÉES:
  ┌────────────────────────┬──────────────────────────────────┐
  │ Propriété              │ Valeur                           │
  ├────────────────────────┼──────────────────────────────────┤
  │ Masse molaire          │ 2.016 g/mol                      │
  │ Température ébullition │ 20.3 K (-253°C) @ 1 bar          │
  │ Température critique   │ 33.2 K                           │
  │ Pression critique      │ 13.0 bar                         │
  │ Densité liquide        │ 70.8 kg/m³ @ 20 K                │
  │ Densité gaz            │ 1.34 kg/m³ @ NBP                 │
  │ Cp liquide             │ 9,700-14,300 J/kg·K              │
  │ Cp gaz                 │ 14,300 J/kg·K                    │
  │ Conductivité (liq)     │ 0.10 W/m·K                       │
  │ Conductivité (gaz)     │ 0.017 W/m·K                      │
  │ Viscosité (liq)        │ 13 μPa·s (très faible!)          │
  │ Prandtl                │ 0.7-1.3                          │
  │ Chaleur latente        │ 448 kJ/kg                        │
  └────────────────────────┴──────────────────────────────────┘

✅ AVANTAGES THERMIQUES:
  - Cp ÉNORME (14,300 J/kg·K) → absorbe beaucoup d'énergie
  - Viscosité très faible → Re élevé → h_c élevé
  - k/μ élevé → excellent transfert
  - h_c typique: 50,000-200,000 W/m²·K!

❌ INCONVÉNIENTS:
  - Très basse température → isolation critique
  - Densité très faible → gros réservoirs
  - Fuit facilement (petite molécule)
  - Fragilisation hydrogène des métaux
  - Coût de production/stockage

⚠️ PRÉCAUTIONS:
  - Matériaux compatibles: Al, Inox 304/316, Inconel
  - Éviter: aciers au carbone (fragilisation)
  - Joints: PTFE, Indium, soudures
  - Risque d'explosion si mélange avec O2!

MOTEURS UTILISANT LH2:
  - RS-25 / SSME (NASA)
  - RL10 (Aerojet Rocketdyne)
  - J-2, J-2X (Saturn V, SLS)
  - Vulcain (Ariane)
  - LE-7, LE-9 (Japon)
  - CE-20 (Inde)


8.3 OXYGÈNE LIQUIDE (LOX)
───────────────────────────────────────────────────────────────

Le LOX est parfois utilisé comme coolant (cycles oxydizer-rich).

PROPRIÉTÉS DÉTAILLÉES:
  ┌────────────────────────┬──────────────────────────────────┐
  │ Propriété              │ Valeur                           │
  ├────────────────────────┼──────────────────────────────────┤
  │ Masse molaire          │ 32.0 g/mol                       │
  │ Température ébullition │ 90.2 K (-183°C) @ 1 bar          │
  │ Température critique   │ 154.6 K                          │
  │ Pression critique      │ 50.4 bar                         │
  │ Densité liquide        │ 1141 kg/m³ @ 90 K                │
  │ Cp liquide             │ 1,700 J/kg·K                     │
  │ Conductivité (liq)     │ 0.15 W/m·K                       │
  │ Viscosité (liq)        │ 190 μPa·s                        │
  │ Prandtl                │ 2.2                              │
  │ Chaleur latente        │ 213 kJ/kg                        │
  └────────────────────────┴──────────────────────────────────┘

✅ AVANTAGES:
  - Disponible (c'est l'oxydant!)
  - Bonne densité → compact
  - Température modérée (90 K vs 20 K pour LH2)

❌ INCONVÉNIENTS:
  - Cp modéré seulement
  - TRÈS réactif → risques d'ignition
  - Incompatible avec hydrocarbures chauds
  - Corrosif à haute température

⚠️ ATTENTION EXTRÊME:
  - LOX + matière organique = EXPLOSION
  - Nettoyage LOX obligatoire (dégraissage)
  - Matériaux: Inox, Monel, Inconel
  - Éviter: Al (sauf alliages spéciaux), Ti

UTILISATION:
  - RD-170/180 (cycle oxidizer-rich)
  - Quelques moteurs à cycle ox-rich
  - Généralement le FUEL est préféré comme coolant


8.4 MÉTHANE LIQUIDE (LCH4)
───────────────────────────────────────────────────────────────

Le méthane gagne en popularité (Raptor, BE-4, etc.)

PROPRIÉTÉS DÉTAILLÉES:


---

[← Section précédente : Températures de Paroi](4-Calcul-des-Temperatures-de-Paroi.md) | [Retour à l'accueil](Home.md) | [Section suivante : Exemples de Calcul →](9-Exemples-de-Calcul.md)
