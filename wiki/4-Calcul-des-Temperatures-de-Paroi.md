# 4. CALCUL DES TEMPÉRATURES DE PAROI

[← Section précédente : Modèle de Bartz](3-Modele-de-Bartz.md) | [Retour à l'accueil](Home.md) | [Section suivante : Design et Dimensionnement →](5-Design-et-Dimensionnement.md)

---

## Table des matières
- [4.1 Système d'équations thermiques](#41-système-déquations-thermiques)
- [4.2 Calcul de T_WALL_HOT (température critique)](#42-calcul-de-t_wall_hot-température-critique)
- [4.3 Calcul de T_WALL_COLD](#43-calcul-de-t_wall_cold)
- [4.4 Profil de température dans la paroi](#44-profil-de-température-dans-la-paroi)
- [4.5 Contraintes thermiques (stress thermique)](#45-contraintes-thermiques-stress-thermique)
- [4.6 Régime transitoire (démarrage/arrêt)](#46-régime-transitoire-démarragearrêt)

---

4. CALCUL DES TEMPÉRATURES DE PAROI
═══════════════════════════════════════════════════════════════

Le calcul précis des températures de paroi est l'objectif 
principal de l'analyse thermique. C'est ce qui détermine 
si le moteur survivra ou non.


4.1 SYSTÈME D'ÉQUATIONS THERMIQUES
───────────────────────────────────────────────────────────────

En régime permanent, le flux thermique est constant à travers 
toutes les couches. Cela donne un système de 3 équations:

ÉQUATION 1 - Côté gaz chaud:
  q = h_g × (T_gaz - T_wall_hot)

ÉQUATION 2 - Conduction dans la paroi:
  q = (k/e) × (T_wall_hot - T_wall_cold)

ÉQUATION 3 - Côté coolant:
  q = h_c × (T_wall_cold - T_coolant)

COMBINAISON - Flux thermique total:

        T_gaz - T_coolant
  q = ─────────────────────────────
       1/h_g + e/k + 1/h_c

Cette équation est FONDAMENTALE. Elle permet de calculer q 
connaissant les températures des fluides et les résistances.


4.2 CALCUL DE T_WALL_HOT (température critique)
───────────────────────────────────────────────────────────────

C'est la température la plus importante car c'est elle qui 
détermine si le matériau va fondre ou se dégrader.

MÉTHODE 1 - À partir du flux:

  T_wall_hot = T_gaz - q/h_g

MÉTHODE 2 - À partir de T_wall_cold:

  T_wall_hot = T_wall_cold + q × e/k

MÉTHODE 3 - Formule directe (résolution du système):

           h_g×T_gaz + (k/e)×T_wall_cold
  T_wh = ────────────────────────────────
                h_g + k/e

Ou de façon équivalente:

           h_g×T_gaz + h_c×T_cool + (k/e)×(h_c×T_cool/(h_c+k/e))
  T_wh = ──────────────────────────────────────────────────────────
                            ...système couplé...

En pratique, on résout par itération ou formule analytique.

INFLUENCE DES PARAMÈTRES SUR T_wall_hot:
  ┌────────────────────┬────────────────────────────────────────┐
  │ Si on augmente...  │ Effet sur T_wall_hot                   │
  ├────────────────────┼────────────────────────────────────────┤
  │ h_g ↑              │ T_wall_hot ↑ (plus de flux entrant)    │
  │ h_c ↑              │ T_wall_hot ↓ (meilleure évacuation)    │
  │ k ↑                │ T_wall_hot ↓ (gradient réduit)         │
  │ e ↑                │ T_wall_hot ↑ (résistance accrue)       │
  │ T_gaz ↑            │ T_wall_hot ↑ (source plus chaude)      │
  │ T_coolant ↓        │ T_wall_hot ↓ (puits plus froid)        │
  └────────────────────┴────────────────────────────────────────┘


4.3 CALCUL DE T_WALL_COLD
───────────────────────────────────────────────────────────────

MÉTHODE 1 - À partir du flux:

  T_wall_cold = T_coolant + q/h_c

MÉTHODE 2 - À partir de T_wall_hot:

  T_wall_cold = T_wall_hot - q × e/k

IMPORTANCE DE T_WALL_COLD:
  - Détermine le ΔT dans la paroi
  - Influence le stress thermique (dilatation différentielle)
  - Affecte les propriétés du coolant (ébullition possible?)

⚠️ ATTENTION À L'ÉBULLITION:
Si T_wall_cold > T_ébullition du coolant (à la pression locale):
  → Formation de bulles
  → Risque de DNB (Departure from Nucleate Boiling)
  → Chute drastique de h_c → SURCHAUFFE → DESTRUCTION

TEMPÉRATURES D'ÉBULLITION (à pression atmosphérique):
  ┌────────────────────┬──────────────────────────────────┐
  │ Coolant            │ T_boil @ 1 bar (K)               │
  ├────────────────────┼──────────────────────────────────┤
  │ LH2                │ 20.3 K                           │
  │ LOX                │ 90.2 K                           │
  │ LN2                │ 77.4 K                           │
  │ CH4                │ 111.7 K                          │
  │ C2H6               │ 184.6 K                          │
  │ NH3                │ 239.8 K                          │
  │ C2H5OH             │ 351.4 K                          │
  │ H2O                │ 373.2 K                          │
  │ N2H4               │ 387.0 K                          │
  │ RP-1               │ 490-540 K (plage)                │
  └────────────────────┴──────────────────────────────────┘

À haute pression, T_boil augmente (selon courbe de saturation).


4.4 PROFIL DE TEMPÉRATURE DANS LA PAROI
───────────────────────────────────────────────────────────────

En régime permanent avec flux constant, le profil est LINÉAIRE:

                     q
  T(x) = T_wall_hot - ─── × x
                      k

Où:
  x = distance depuis la surface chaude (0 ≤ x ≤ e)
  T(0) = T_wall_hot
  T(e) = T_wall_cold

REPRÉSENTATION GRAPHIQUE:

  T (K)
    │
T_wh├─────●
    │      ╲
    │       ╲  Gradient = -q/k
    │        ╲
    │         ╲
T_wc├──────────●
    │          │
    └──────────┴────── x (m)
    0          e

GRADIENT DE TEMPÉRATURE:

  dT/dx = -q/k   [K/m]

Exemple numérique:
  q = 20 MW/m², k = 320 W/m·K (CuCr)
  dT/dx = -20×10⁶ / 320 = -62,500 K/m = -62.5 K/mm

Pour une épaisseur e = 2 mm:
  ΔT = 62.5 × 2 = 125 K


4.5 CONTRAINTES THERMIQUES (STRESS THERMIQUE)
───────────────────────────────────────────────────────────────

Le gradient de température crée des contraintes mécaniques 
dues à la dilatation différentielle.

CONTRAINTE THERMIQUE MAXIMALE:

              E × α × ΔT
  σ_th = ──────────────────
              2 × (1 - ν)

Où:
  E = module de Young [Pa]
  α = coefficient de dilatation thermique [1/K]
  ΔT = T_wall_hot - T_wall_cold [K]
  ν = coefficient de Poisson [-]

PROPRIÉTÉS THERMOMÉCANIQUES:
  ┌──────────────────┬────────┬────────────┬────────┐
  │ Matériau         │ E (GPa)│ α (10⁻⁶/K) │ ν      │
  ├──────────────────┼────────┼────────────┼────────┤
  │ Cuivre           │  117   │    17.0    │ 0.34   │
  │ CuCr             │  130   │    16.5    │ 0.34   │
  │ Inconel 718      │  200   │    13.0    │ 0.29   │
  │ Inox 316L        │  193   │    16.0    │ 0.27   │
  │ Niobium          │  105   │     7.3    │ 0.40   │
  │ Molybdène        │  329   │     5.0    │ 0.31   │
  │ Tungstène        │  411   │     4.5    │ 0.28   │
  └──────────────────┴────────┴────────────┴────────┘

EXEMPLE DE CALCUL:
  CuCr, ΔT = 150 K, E = 130 GPa, α = 16.5×10⁻⁶/K, ν = 0.34
  
  σ_th = 130×10⁹ × 16.5×10⁻⁶ × 150 / (2×(1-0.34))
  σ_th = 244 MPa

Cette contrainte s'ajoute aux contraintes de pression!


4.6 RÉGIME TRANSITOIRE (DÉMARRAGE/ARRÊT)
───────────────────────────────────────────────────────────────

Pendant les phases de démarrage et d'arrêt, le régime n'est 
pas permanent. Les équations deviennent:

ÉQUATION DE LA CHALEUR (1D):

  ∂T       k     ∂²T        ∂²T
  ── = ───────── × ─── = α × ───
  ∂t    ρ × Cp    ∂x²        ∂x²

Où α = k/(ρ×Cp) est la diffusivité thermique [m²/s].

TEMPS CARACTÉRISTIQUE:

  τ = e² / α

C'est le temps pour atteindre ~63% du régime permanent.

VALEURS TYPIQUES DE τ:
  ┌──────────────────┬────────────┬─────────────────────┐


---

[← Section précédente : Modèle de Bartz](3-Modele-de-Bartz.md) | [Retour à l'accueil](Home.md) | [Section suivante : Design et Dimensionnement →](5-Design-et-Dimensionnement.md)
