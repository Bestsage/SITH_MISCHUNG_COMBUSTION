# 10. FORMULES RAPIDES (AIDE-MÉMOIRE COMPLET)

[← Section précédente : Exemples](9-Exemples-de-Calcul.md) | [Retour à l'accueil](Home.md) | [Section suivante : Analyses Avancées →](11-14-Analyses-Avancees.md)

---

## Table des matières
- [10.1 Équations fondamentales du transfert thermique](#101-équations-fondamentales-du-transfert-thermique)
- [10.2 Équation de Bartz](#102-équation-de-bartz-côté-gaz-chaud)
- [10.3 Nombres adimensionnels](#103-nombres-adimensionnels)
- [10.4 Corrélations de convection forcée](#104-corrélations-de-convection-forcée)
- [10.5 Équations de température de paroi](#105-équations-de-température-de-paroi)
- [10.6 Épaisseur de paroi](#106-épaisseur-de-paroi)
- [10.7 Puissance et énergie thermique](#107-puissance-et-énergie-thermique)
- [10.8 Pertes de charge](#108-pertes-de-charge)
- [10.9 Film cooling](#109-film-cooling)
- [10.10 Propriétés des gaz de combustion](#1010-propriétés-des-gaz-de-combustion)
- [10.11 Tableau récapitulatif](#1011-tableau-récapitulatif-des-formules)
- [10.12 Ordres de grandeur typiques](#1012-ordres-de-grandeur-typiques)
- [10.13 Conversions utiles](#1013-conversions-utiles)
- [10.14 Constantes physiques](#1014-constantes-physiques)

---


10. FORMULES RAPIDES (AIDE-MÉMOIRE COMPLET)
═══════════════════════════════════════════════════════════════

Cette section rassemble toutes les formules essentielles pour
la conception thermique des moteurs-fusées, organisées par thème.


10.1 ÉQUATIONS FONDAMENTALES DU TRANSFERT THERMIQUE
───────────────────────────────────────────────────────────────

FLUX THERMIQUE (LOI DE FOURIER):
  ┌─────────────────────────────────────────────────────────┐
  │ q = -k × (dT/dx)        [W/m²]                         │
  │                                                         │
  │ Pour une paroi plane:                                   │
  │ q = k × (T₁ - T₂) / e   [W/m²]                         │
  │                                                         │
  │ où: k = conductivité thermique [W/m·K]                  │
  │     e = épaisseur [m]                                   │
  │     T₁, T₂ = températures aux faces [K]                 │
  └─────────────────────────────────────────────────────────┘

CONVECTION (LOI DE NEWTON):
  ┌─────────────────────────────────────────────────────────┐
  │ q = h × (T_fluide - T_paroi)    [W/m²]                 │
  │                                                         │
  │ où: h = coefficient de convection [W/m²·K]              │
  │     T_fluide = température du fluide [K]                │
  │     T_paroi = température de la paroi [K]               │
  └─────────────────────────────────────────────────────────┘

RÉSISTANCES THERMIQUES EN SÉRIE:
  ┌─────────────────────────────────────────────────────────┐
  │ R_total = R_gaz + R_paroi + R_coolant                   │
  │                                                         │
  │ R_gaz = 1/h_g           [m²·K/W]                       │
  │ R_paroi = e/k           [m²·K/W]                       │
  │ R_coolant = 1/h_c       [m²·K/W]                       │
  │                                                         │
  │ Flux: q = ΔT_total / R_total                           │
  └─────────────────────────────────────────────────────────┘

COEFFICIENT GLOBAL DE TRANSFERT:
  ┌─────────────────────────────────────────────────────────┐
  │ U = 1 / R_total = 1 / (1/h_g + e/k + 1/h_c)            │
  │                                                         │
  │ q = U × (T_gaz - T_coolant)                            │
  └─────────────────────────────────────────────────────────┘


10.2 ÉQUATION DE BARTZ (CÔTÉ GAZ CHAUD)
───────────────────────────────────────────────────────────────

FORME COMPLÈTE:
  ┌─────────────────────────────────────────────────────────┐
  │                     0.026      μ^0.2 × Cp              │
  │ h_g = σ × ─────── × ────────── × (Pc/c*)^0.8 ×        │
  │                     Dt^0.2      Pr^0.6                  │
  │                                                         │
  │           × (Dt/R_c)^0.1 × (At/A)^0.9                  │
  └─────────────────────────────────────────────────────────┘

FACTEUR DE CORRECTION σ:
  ┌─────────────────────────────────────────────────────────┐
  │ σ = [½(Tw/Tc)(1 + (γ-1)/2 × M²) + ½]^(-0.68) ×        │
  │     × [1 + (γ-1)/2 × M²]^(-0.12)                       │
  │                                                         │
  │ Approximation au col (M=1):                             │
  │ σ ≈ [0.5 × Tw/Tc × (γ+1)/2 + 0.5]^(-0.68)             │
  └─────────────────────────────────────────────────────────┘

FORME SIMPLIFIÉE AU COL:
  ┌─────────────────────────────────────────────────────────┐
  │ h_g,throat = C × (Pc^0.8 / Dt^1.8) × σ                 │
  │                                                         │
  │ où C dépend des propriétés du gaz                       │
  │                                                         │
  │ Estimation rapide:                                      │
  │ h_g ≈ 5000 × (Pc/20)^0.8 × (30/Dt_mm)^1.8 [W/m²·K]    │
  └─────────────────────────────────────────────────────────┘

VARIATION LE LONG DE LA TUYÈRE:
  ┌─────────────────────────────────────────────────────────┐
  │ h_g(x) = h_g,throat × (Dt / D(x))^1.8                  │
  │                                                         │
  │ Au col:     h_g = h_g,throat (maximum)                  │
  │ Chambre:    h_g ≈ 0.3 × h_g,throat                     │
  │ Sortie:     h_g ≈ 0.05 × h_g,throat                    │
  └─────────────────────────────────────────────────────────┘


10.3 NOMBRES ADIMENSIONNELS
───────────────────────────────────────────────────────────────

NOMBRE DE REYNOLDS:
  ┌─────────────────────────────────────────────────────────┐
  │ Re = ρ × v × D_h / μ = v × D_h / ν                     │
  │                                                         │
  │ où: ρ = masse volumique [kg/m³]                         │
  │     v = vitesse [m/s]                                   │
  │     D_h = diamètre hydraulique [m]                      │
  │     μ = viscosité dynamique [Pa·s]                      │
  │     ν = viscosité cinématique [m²/s]                    │
  │                                                         │
  │ Régimes:                                                │
  │   Re < 2300      : Laminaire                            │
  │   2300 < Re < 10⁴: Transition                          │
  │   Re > 10⁴       : Turbulent                           │
  └─────────────────────────────────────────────────────────┘

NOMBRE DE PRANDTL:
  ┌─────────────────────────────────────────────────────────┐
  │ Pr = μ × Cp / k = ν / α                                │
  │                                                         │
  │ où: Cp = capacité thermique [J/kg·K]                    │
  │     k = conductivité thermique [W/m·K]                  │
  │     α = diffusivité thermique [m²/s]                    │
  │                                                         │
  │ Valeurs typiques:                                       │
  │   Gaz combustion : Pr ≈ 0.7-0.8                        │
  │   Eau           : Pr ≈ 7 (à 20°C)                      │
  │   RP-1          : Pr ≈ 15-25                           │
  │   LH2           : Pr ≈ 0.7-1.5                         │
  │   Huiles        : Pr ≈ 100-1000                        │
  └─────────────────────────────────────────────────────────┘

NOMBRE DE NUSSELT:
  ┌─────────────────────────────────────────────────────────┐
  │ Nu = h × D_h / k                                       │
  │                                                         │
  │ Interprétation: Nu = transfert convectif / conductif    │
  │                                                         │
  │ Pour obtenir h:                                         │
  │ h = Nu × k / D_h    [W/m²·K]                           │
  └─────────────────────────────────────────────────────────┘

DIAMÈTRE HYDRAULIQUE:
  ┌─────────────────────────────────────────────────────────┐
  │ D_h = 4 × A / P                                        │
  │                                                         │
  │ où: A = aire de la section [m²]                         │
  │     P = périmètre mouillé [m]                           │
  │                                                         │
  │ Cas particuliers:                                       │
  │   Tube circulaire:    D_h = D                          │
  │   Rectangle (a×b):    D_h = 2ab/(a+b)                  │
  │   Annulaire:          D_h = D_ext - D_int              │
  │   Carré (côté a):     D_h = a                          │
  └─────────────────────────────────────────────────────────┘


10.4 CORRÉLATIONS DE CONVECTION FORCÉE
───────────────────────────────────────────────────────────────

DITTUS-BOELTER (turbulent, fluides simples):
  ┌─────────────────────────────────────────────────────────┐
  │ Nu = 0.023 × Re^0.8 × Pr^n                             │
  │                                                         │
  │ n = 0.4  (chauffage du fluide)                         │
  │ n = 0.3  (refroidissement du fluide)                   │
  │                                                         │
  │ Validité: Re > 10,000                                   │
  │           0.6 < Pr < 160                                │
  │           L/D > 10                                      │
  └─────────────────────────────────────────────────────────┘

SIEDER-TATE (correction viscosité):
  ┌─────────────────────────────────────────────────────────┐
  │ Nu = 0.027 × Re^0.8 × Pr^(1/3) × (μ_bulk/μ_wall)^0.14 │
  │                                                         │
  │ Recommandé quand:                                       │
  │   T_wall >> T_bulk (grande variation de μ)             │
  └─────────────────────────────────────────────────────────┘

GNIELINSKI (transition + turbulent):
  ┌─────────────────────────────────────────────────────────┐
  │       (f/8) × (Re - 1000) × Pr                         │
  │ Nu = ─────────────────────────────────────             │
  │       1 + 12.7 × (f/8)^0.5 × (Pr^(2/3) - 1)            │
  │                                                         │
  │ avec f = (0.79 × ln(Re) - 1.64)^(-2)                   │
  │                                                         │
  │ Validité: 2300 < Re < 5×10⁶                            │
  │           0.5 < Pr < 2000                               │
  └─────────────────────────────────────────────────────────┘

PETUKHOV (haute précision, turbulent):
  ┌─────────────────────────────────────────────────────────┐
  │       (f/8) × Re × Pr                                  │
  │ Nu = ──────────────────────────────────────            │
  │       1.07 + 12.7 × (f/8)^0.5 × (Pr^(2/3) - 1)         │
  │                                                         │
  │ avec f = (0.790 × ln(Re) - 1.64)^(-2)                  │
  │                                                         │
  │ Précision: ±5% pour 10⁴ < Re < 5×10⁶                   │
  └─────────────────────────────────────────────────────────┘

LAMINAIRE (Re < 2300):
  ┌─────────────────────────────────────────────────────────┐
  │ Tube long, T_wall constante:                           │
  │   Nu = 3.66                                             │
  │                                                         │
  │ Tube long, flux constant:                              │
  │   Nu = 4.36                                             │
  │                                                         │
  │ Tube court (développement thermique):                  │
  │   Nu = 1.86 × (Re × Pr × D/L)^(1/3) × (μ_b/μ_w)^0.14  │
  └─────────────────────────────────────────────────────────┘


10.5 ÉQUATIONS DE TEMPÉRATURE DE PAROI
───────────────────────────────────────────────────────────────

PROFIL DE TEMPÉRATURE À TRAVERS LA PAROI:
  ┌─────────────────────────────────────────────────────────┐
  │ T_gaz ──────▶ T_wall_hot ──────▶ T_wall_cold ──────▶ T_coolant │
  │         h_g           k/e              h_c              │
  │                                                         │
  │ T_wall_hot = T_gaz - q/h_g                             │
  │                                                         │
  │ T_wall_cold = T_wall_hot - q×e/k                       │
  │              = T_coolant + q/h_c                        │
  │                                                         │
  │ Vérification: T_wall_hot = T_coolant + q×(1/h_c + e/k) │
  └─────────────────────────────────────────────────────────┘

TEMPÉRATURE ADIABATIQUE DE PAROI (T_aw):
  ┌─────────────────────────────────────────────────────────┐
  │ T_aw = T_statique × [1 + r × (γ-1)/2 × M²]             │
  │                                                         │
  │ Facteur de récupération r:                              │
  │   r = Pr^(1/2)  pour laminaire                         │
  │   r = Pr^(1/3)  pour turbulent                         │
  │                                                         │
  │ Au col (M=1):                                           │
  │   T_aw ≈ 0.90 × T_c  (gaz combustion typique)          │
  └─────────────────────────────────────────────────────────┘

TEMPÉRATURE CRITIQUE DE PAROI:
  ┌─────────────────────────────────────────────────────────┐
  │ Marge thermique:                                        │
  │   Marge = T_limite - T_wall_hot                        │
  │                                                         │
  │ Condition de sécurité:                                  │
  │   T_wall_hot < T_limite  (typiquement 20% de marge)    │
  │                                                         │
  │ Limite absolue:                                         │
  │   T_wall_hot << T_fusion  (facteur 1.5 minimum)        │
  └─────────────────────────────────────────────────────────┘


10.6 ÉPAISSEUR DE PAROI
───────────────────────────────────────────────────────────────

ÉPAISSEUR MAXIMALE (critère thermique):
  ┌─────────────────────────────────────────────────────────┐
  │ e_max = k × (T_limite - T_wall_cold) / q               │
  │                                                         │
  │ Si e > e_max: T_wall_hot > T_limite → Défaillance!     │
  └─────────────────────────────────────────────────────────┘

ÉPAISSEUR DE FUSION:
  ┌─────────────────────────────────────────────────────────┐
  │ e_melt = k × (T_fusion - T_wall_cold) / q              │
  │                                                         │
  │ Si e > e_melt: La paroi fond côté gaz!                 │
  └─────────────────────────────────────────────────────────┘

ÉPAISSEUR SACRIFICIELLE:
  ┌─────────────────────────────────────────────────────────┐
  │ e_sacrif = e_initial - e_melt                          │
  │                                                         │
  │ Épaisseur de matériau qui peut fondre sans             │
  │ compromettre l'intégrité structurelle.                 │
  │                                                         │
  │ Condition: e_sacrif > 0 et e_restante > e_min_struct   │
  └─────────────────────────────────────────────────────────┘

ÉPAISSEUR MINIMALE (critère mécanique):
  ┌─────────────────────────────────────────────────────────┐
  │ e_min = Pc × r / σ_admissible                          │
  │                                                         │
  │ où: Pc = pression chambre [Pa]                          │
  │     r = rayon local [m]                                 │
  │     σ_admissible = contrainte admissible à T [Pa]       │
  │                                                         │
  │ Note: σ_admissible diminue avec T!                     │
  └─────────────────────────────────────────────────────────┘


10.7 PUISSANCE ET ÉNERGIE THERMIQUE
───────────────────────────────────────────────────────────────

PUISSANCE THERMIQUE TOTALE:
  ┌─────────────────────────────────────────────────────────┐
  │ Q_total = ∫ q(x) × dA                                  │
  │                                                         │
  │ Approximation:                                          │
  │ Q_total ≈ q_moyen × A_totale                           │
  │                                                         │
  │ où: q_moyen ≈ 0.3 × q_col (valeur typique)             │
  └─────────────────────────────────────────────────────────┘

ÉLÉVATION DE TEMPÉRATURE DU COOLANT:
  ┌─────────────────────────────────────────────────────────┐
  │ ΔT_coolant = Q_total / (ṁ_coolant × Cp_coolant)        │
  │                                                         │
  │ T_sortie = T_entrée + ΔT_coolant                       │
  │                                                         │
  │ Condition: T_sortie < T_ébullition ou T_décomposition  │
  └─────────────────────────────────────────────────────────┘

FRACTION DE CHALEUR ABSORBÉE:
  ┌─────────────────────────────────────────────────────────┐
  │ η_thermique = Q_total / Q_combustion                   │
  │                                                         │
  │ Q_combustion = ṁ_propergols × ΔH_combustion            │
  │                                                         │
  │ Typiquement: η_thermique ≈ 1-5%                        │
  └─────────────────────────────────────────────────────────┘


10.8 PERTES DE CHARGE
───────────────────────────────────────────────────────────────

ÉQUATION DE DARCY-WEISBACH:
  ┌─────────────────────────────────────────────────────────┐
  │ Δp = f × (L/D_h) × (ρ × v²) / 2                        │
  │                                                         │
  │ où: f = facteur de friction                             │
  │     L = longueur du canal [m]                           │
  │     D_h = diamètre hydraulique [m]                      │
  └─────────────────────────────────────────────────────────┘

FACTEUR DE FRICTION:
  ┌─────────────────────────────────────────────────────────┐
  │ Laminaire (Re < 2300):                                  │
  │   f = 64 / Re                                           │
  │                                                         │
  │ Turbulent lisse (Blasius, Re < 10⁵):                   │
  │   f = 0.316 / Re^0.25                                  │
  │                                                         │
  │ Turbulent (Petukhov, Re > 3000):                       │
  │   f = (0.790 × ln(Re) - 1.64)^(-2)                     │
  │                                                         │
  │ Avec rugosité (Colebrook-White):                       │
  │   1/√f = -2×log₁₀(ε/3.7D + 2.51/(Re×√f))              │
  └─────────────────────────────────────────────────────────┘

PUISSANCE DE POMPAGE:
  ┌─────────────────────────────────────────────────────────┐
  │ P_pompe = Δp × Q_volumique / η_pompe                   │
  │         = Δp × ṁ / (ρ × η_pompe)                       │
  │                                                         │
  │ où: Q_volumique = débit volumique [m³/s]                │
  │     η_pompe = rendement de la pompe                     │
  └─────────────────────────────────────────────────────────┘


10.9 FILM COOLING
───────────────────────────────────────────────────────────────

EFFICACITÉ DU FILM:
  ┌─────────────────────────────────────────────────────────┐
  │ η_film = (T_aw - T_aw,film) / (T_aw - T_coolant)       │
  │                                                         │
  │ où: T_aw,film = température adiabatique avec film       │
  │     T_coolant = température du film injecté             │
  │                                                         │
  │ T_aw,effective = T_coolant + η_film × (T_aw - T_coolant)│
  └─────────────────────────────────────────────────────────┘

DÉBIT DE FILM:
  ┌─────────────────────────────────────────────────────────┐
  │ Règle empirique:                                        │
  │   ṁ_film = 2-5% du débit fuel pour protection locale   │
  │   ṁ_film = 10-20% pour protection chambre complète     │
  │                                                         │
  │ Efficacité typique:                                     │
  │   η_film ≈ 0.3 - 0.6 selon injection et géométrie      │
  └─────────────────────────────────────────────────────────┘

RÉDUCTION DE FLUX EFFECTIVE:
  ┌─────────────────────────────────────────────────────────┐
  │ q_avec_film = h_g × (T_aw,effective - T_wall_hot)      │
  │                                                         │
  │ Réduction typique: 30-60% du flux sans film            │
  └─────────────────────────────────────────────────────────┘


10.10 PROPRIÉTÉS DES GAZ DE COMBUSTION
───────────────────────────────────────────────────────────────

ESTIMATION DES PROPRIÉTÉS:
  ┌─────────────────────────────────────────────────────────┐
  │ Viscosité dynamique (loi de Sutherland):               │
  │   μ = μ₀ × (T/T₀)^1.5 × (T₀ + S)/(T + S)               │
  │                                                         │
  │ Pour gaz de combustion (approximation):                │
  │   μ ≈ 3×10⁻⁷ × T^0.7  [Pa·s]                          │
  │                                                         │
  │ Conductivité thermique:                                │
  │   k = Cp × μ / Pr                                      │
  │   k ≈ Cp × μ / 0.72  [W/m·K]                          │
  │                                                         │
  │ Cp (J/kg·K) typique:                                   │
  │   LOX/RP-1: 2000-2200                                  │
  │   LOX/LH2:  3500-4000                                  │
  │   LOX/CH4:  2400-2800                                  │
  └─────────────────────────────────────────────────────────┘


10.11 TABLEAU RÉCAPITULATIF DES FORMULES
───────────────────────────────────────────────────────────────

  ┌──────────────────────────────┬────────────────────────────────────────┐
  │ GRANDEUR                     │ FORMULE                                │
  ├──────────────────────────────┼────────────────────────────────────────┤
  │ Flux thermique               │ q = ΔT / R_total                       │
  │ Résistance totale            │ R = 1/h_g + e/k + 1/h_c                │
  │ Coefficient global           │ U = 1/R_total                          │
  │ T paroi chaude               │ T_hot = T_gaz - q/h_g                  │
  │ T paroi froide               │ T_cold = T_coolant + q/h_c             │
  │ Gradient dans paroi          │ ΔT_paroi = q × e / k                   │
  ├──────────────────────────────┼────────────────────────────────────────┤
  │ Reynolds                     │ Re = ρ·v·D_h / μ                       │
  │ Prandtl                      │ Pr = μ·Cp / k                          │
  │ Nusselt (Dittus-Boelter)     │ Nu = 0.023·Re^0.8·Pr^0.4               │
  │ h depuis Nu                  │ h = Nu·k / D_h                         │
  │ Diamètre hydraulique         │ D_h = 4·A / P                          │
  ├──────────────────────────────┼────────────────────────────────────────┤
  │ Épaisseur max thermique      │ e_max = k·(T_lim - T_cold) / q         │
  │ Épaisseur fusion             │ e_melt = k·(T_fus - T_cold) / q        │
  │ Épaisseur min mécanique      │ e_min = P·r / σ_adm                    │
  ├──────────────────────────────┼────────────────────────────────────────┤
  │ Puissance thermique          │ Q = ∫q·dA ≈ q_moy × A                  │
  │ ΔT coolant                   │ ΔT = Q / (ṁ·Cp)                        │
  │ Perte de charge              │ Δp = f·(L/D_h)·ρ·v²/2                  │
  └──────────────────────────────┴────────────────────────────────────────┘


10.12 ORDRES DE GRANDEUR TYPIQUES
───────────────────────────────────────────────────────────────

FLUX THERMIQUE AU COL:
  ┌─────────────────────────────────────────────────────────┐
  │ Moteur amateur (Pc < 10 bar):      1 - 5 MW/m²         │
  │ Petit moteur (Pc ~ 20-50 bar):     5 - 20 MW/m²        │
  │ Moteur orbital (Pc ~ 50-100 bar):  15 - 50 MW/m²       │
  │ Moteur haute Pc (> 150 bar):       30 - 80 MW/m²       │
  │ Record (SSME au col):              130 MW/m²           │
  └─────────────────────────────────────────────────────────┘

COEFFICIENTS DE TRANSFERT:
  ┌─────────────────────────────────────────────────────────┐
  │ h_g au col:                                             │
  │   Pc = 20 bar:     3,000 - 8,000 W/m²·K                │
  │   Pc = 50 bar:     8,000 - 20,000 W/m²·K               │
  │   Pc = 100 bar:    15,000 - 40,000 W/m²·K              │
  │   Pc = 200 bar:    30,000 - 80,000 W/m²·K              │
  │                                                         │
  │ h_c (coolant):                                          │
  │   RP-1:            5,000 - 30,000 W/m²·K               │
  │   LCH4:            20,000 - 80,000 W/m²·K              │
  │   LH2:             50,000 - 200,000 W/m²·K             │
  │   Eau:             5,000 - 50,000 W/m²·K               │
  └─────────────────────────────────────────────────────────┘

TEMPÉRATURES:
  ┌─────────────────────────────────────────────────────────┐
  │ T chambre:                                              │
  │   LOX/RP-1:        3200 - 3500 K                       │
  │   LOX/LH2:         3400 - 3600 K                       │
  │   LOX/CH4:         3300 - 3500 K                       │
  │   N2O4/UDMH:       3000 - 3200 K                       │
  │                                                         │
  │ T paroi hot typique:                                    │
  │   Cuivre allié:    500 - 800 K                         │
  │   Ni superalliage: 800 - 1100 K                        │
  │   Réfractaires:    1200 - 2000 K                       │
  └─────────────────────────────────────────────────────────┘

GÉOMÉTRIE:
  ┌─────────────────────────────────────────────────────────┐
  │ Épaisseur paroi:   0.5 - 10 mm                         │
  │ Largeur canal:     1 - 5 mm                            │
  │ Profondeur canal:  1 - 10 mm                           │
  │ Nombre canaux:     20 - 500                            │
  │ Vitesse coolant:   5 - 50 m/s                          │
  │ Δp canaux:         2 - 20 bar                          │
  └─────────────────────────────────────────────────────────┘


10.13 CONVERSIONS UTILES
───────────────────────────────────────────────────────────────

  ┌────────────────────────────────────────────────────────────────┐
  │ TEMPÉRATURE                                                     │
  │   K = °C + 273.15                                               │
  │   °C = (°F - 32) × 5/9                                         │
  │   K = (°F + 459.67) × 5/9                                      │
  ├────────────────────────────────────────────────────────────────┤
  │ PRESSION                                                        │
  │   1 bar = 100,000 Pa = 0.1 MPa                                 │
  │   1 bar = 14.504 psi                                           │
  │   1 atm = 101,325 Pa = 1.01325 bar                             │
  ├────────────────────────────────────────────────────────────────┤
  │ ÉNERGIE / PUISSANCE                                            │
  │   1 MW = 10⁶ W                                                 │
  │   1 kW = 1.341 hp                                              │
  │   1 BTU/s = 1055 W                                             │
  ├────────────────────────────────────────────────────────────────┤
  │ FLUX THERMIQUE                                                  │
  │   1 MW/m² = 10⁶ W/m²                                           │
  │   1 BTU/(h·ft²) = 3.155 W/m²                                   │
  ├────────────────────────────────────────────────────────────────┤
  │ COEFFICIENT DE TRANSFERT                                        │
  │   1 W/(m²·K) = 0.1761 BTU/(h·ft²·°F)                           │
  │   1 BTU/(h·ft²·°F) = 5.678 W/(m²·K)                            │
  ├────────────────────────────────────────────────────────────────┤
  │ CONDUCTIVITÉ THERMIQUE                                          │
  │   1 W/(m·K) = 0.5778 BTU/(h·ft·°F)                             │
  └────────────────────────────────────────────────────────────────┘


10.14 CONSTANTES PHYSIQUES
───────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────┐
  │ Constante des gaz parfaits:                             │
  │   R = 8.314 J/(mol·K)                                   │
  │                                                         │
  │ Constante de Stefan-Boltzmann:                         │
  │   σ = 5.67×10⁻⁸ W/(m²·K⁴)                              │
  │                                                         │
  │ Nombre d'Avogadro:                                     │
  │   N_A = 6.022×10²³ mol⁻¹                               │
  │                                                         │
  │ Accélération gravitationnelle:                         │
  │   g₀ = 9.80665 m/s²                                    │
  └─────────────────────────────────────────────────────────┘




---

[← Section précédente : Exemples](9-Exemples-de-Calcul.md) | [Retour à l'accueil](Home.md) | [Section suivante : Analyses Avancées →](11-14-Analyses-Avancees.md)
