# 3. MODÈLE DE BARTZ POUR h_g

[← Section précédente : Théorie](2-Theorie-Detaillee-du-Transfert-Thermique.md) | [Retour à l'accueil](Home.md) | [Section suivante : Températures de Paroi →](4-Calcul-des-Temperatures-de-Paroi.md)

---

## Table des matières
- [3.1 Historique et développement](#31-historique-et-développement)
- [3.2 Équation complète de Bartz](#32-équation-complète-de-bartz)
- [3.3 Formule simplifiée](#33-formule-simplifiée-utilisée-dans-le-code)
- [3.4 Propriétés des gaz de combustion](#34-propriétés-des-gaz-de-combustion)
- [3.5 Valeurs typiques de h_g](#35-valeurs-typiques-de-h_g)
- [3.6 Limitations du modèle](#36-limitations-du-modèle-de-bartz)
- [3.7 Comparaison avec autres corrélations](#37-comparaison-avec-autres-corrélations)

---

3. MODÈLE DE BARTZ POUR h_g
═══════════════════════════════════════════════════════════════

L'équation de Bartz est la corrélation de référence pour 
calculer le coefficient de transfert convectif côté gaz 
chaud dans les moteurs-fusées.


3.1 HISTORIQUE ET DÉVELOPPEMENT
───────────────────────────────────────────────────────────────

David R. Bartz a développé cette corrélation en 1957 au 
Jet Propulsion Laboratory (JPL) de la NASA.

CONTEXTE:
  - Années 1950: développement de missiles balistiques
  - Besoin de prédire les températures de paroi
  - Corrélations existantes (Dittus-Boelter) inadaptées
  - Conditions extrêmes: T > 3000 K, P > 50 bar

APPROCHE DE BARTZ:
  1. Partir de la corrélation de Dittus-Boelter
  2. Adapter pour les propriétés variables (T très élevées)
  3. Introduire un facteur de correction σ
  4. Valider expérimentalement sur moteurs réels

PUBLICATION ORIGINALE:
  Bartz, D.R., "A Simple Equation for Rapid Estimation of 
  Rocket Nozzle Convective Heat Transfer Coefficients"
  Jet Propulsion, Vol. 27, No. 1, 1957, pp. 49-51


3.2 ÉQUATION COMPLÈTE DE BARTZ
───────────────────────────────────────────────────────────────

FORME GÉNÉRALE:

            0.026      ⎛  μ^0.2 × Cp  ⎞   ⎛ p_c ⎞^0.8
  h_g = ──────────── × ⎜ ───────────── ⎟ × ⎜ ──── ⎟     × (A_t/A)^0.9 × σ
         D_t^0.2       ⎝   Pr^0.6     ⎠   ⎝ c*   ⎠

DÉFINITION DES TERMES:

  h_g   = coefficient de transfert convectif [W/(m²·K)]
  D_t   = diamètre au col [m]
  μ     = viscosité dynamique des gaz [Pa·s]
  Cp    = capacité thermique massique à pression constante [J/(kg·K)]
  Pr    = nombre de Prandtl des gaz combustion [-]
  p_c   = pression de chambre [Pa]
  c*    = vitesse caractéristique [m/s]
  A_t   = aire au col [m²]
  A     = aire locale [m²]
  σ     = facteur de correction pour couche limite [-]

LE FACTEUR σ (sigma):

                          1
  σ = ─────────────────────────────────────────────────────────
        ⎛   T_wall_hot     ⎞^0.68   ⎛           T_wall_hot     ⎞^0.12
       ⎜0.5 × ─────────── + 0.5⎟    × ⎜1 + γ-1 × M² × (0.5 - ─────────)⎟
        ⎝      T_stag      ⎠         ⎝   2            T_stag   ⎠

Où:
  T_wall_hot = température de paroi côté gaz [K]
  T_stag = température de stagnation (≈ T_chambre) [K]
  γ = rapport des chaleurs spécifiques [-]
  M = nombre de Mach local [-]

SIMPLIFICATION COURANTE:
Pour les calculs préliminaires, on utilise souvent σ ≈ 1.0-1.2


3.3 FORMULE SIMPLIFIÉE (utilisée dans le code)
───────────────────────────────────────────────────────────────

Pour simplifier l'implémentation, on utilise:

ÉTAPE 1 - Calcul de h_g au col (référence):

            0.026      ⎛  μ^0.2 × Cp  ⎞   ⎛ P_c ⎞^0.8
  h_g_col = ────────── × ⎜ ────────────  ⎟ × ⎜ ──── ⎟
            D_t^0.2     ⎝   Pr^0.6    ⎠   ⎝ c*   ⎠

ÉTAPE 2 - h_g local par mise à l'échelle:

  h_g(x) = h_g_col × (D_t / D_local)^1.8

Cette relation vient du fait que:
  - h_g ∝ (débit massique par unité de surface)^0.8
  - À débit constant: G = ṁ/A ∝ 1/D²
  - Donc h_g ∝ (1/D²)^0.8 = D^(-1.6)
  - Avec correction pour le rapport de section: exposant ≈ 1.8

JUSTIFICATION DE L'EXPOSANT 1.8:
  - Origine: combinaison d'effets géométriques et d'écoulement
  - Au col: A minimum, G maximum, donc h_g maximum
  - Dans la chambre: A grand, h_g plus faible
  - Dans le divergent: A croissant, h_g décroissant rapidement


3.4 PROPRIÉTÉS DES GAZ DE COMBUSTION
───────────────────────────────────────────────────────────────

Les propriétés thermo-physiques des gaz de combustion sont 
calculées à une température de film:

  T_film = (T_wall_hot + T_adiabatique) / 2

PROPRIÉTÉS TYPIQUES (LOX/RP-1, T ≈ 2500 K):
  ┌────────────────────┬──────────────────────────────────┐
  │ Propriété          │ Valeur approximative             │
  ├────────────────────┼──────────────────────────────────┤
  │ μ (viscosité)      │ 7-9 × 10⁻⁵ Pa·s                  │
  │ Cp                 │ 2000-2500 J/(kg·K)               │
  │ k_gaz              │ 0.15-0.25 W/(m·K)                │
  │ Pr                 │ 0.75-0.85                        │
  │ γ (gamma)          │ 1.15-1.25                        │
  │ M (masse molaire)  │ 22-28 kg/kmol                    │
  └────────────────────┴──────────────────────────────────┘

VARIATION AVEC LE MÉLANGE O/F:
  ┌──────────────────┬───────────┬───────────┬───────────┐
  │ O/F (LOX/RP-1)   │    2.0    │    2.6    │    3.2    │
  ├──────────────────┼───────────┼───────────┼───────────┤
  │ T_chambre (K)    │   3350    │   3600    │   3500    │
  │ M (kg/kmol)      │   21.5    │   24.0    │   27.5    │
  │ γ                │   1.22    │   1.18    │   1.15    │
  │ c* (m/s)         │   1680    │   1750    │   1700    │
  └──────────────────┴───────────┴───────────┴───────────┘

EFFET SUR h_g:
  - O/F élevé: T_c plus élevé, mais M plus élevé
  - h_g varie peu avec O/F (effets compensatoires)


3.5 VALEURS TYPIQUES DE h_g
───────────────────────────────────────────────────────────────

  ┌─────────────────┬────────────────────┬──────────────────────┐
  │ Zone            │ h_g (W/m²·K)       │ Commentaires         │
  ├─────────────────┼────────────────────┼──────────────────────┤
  │ Injecteur       │ 3,000 - 10,000     │ Dépend du design     │
  │ Chambre (cyl.)  │ 2,000 - 8,000      │ Écoulement subsonique│
  │ Convergent      │ 5,000 - 20,000     │ Accélération du gaz  │
  │ Col (throat)    │ 10,000 - 50,000    │ MAXIMUM! Ma = 1      │
  │ Divergent début │ 8,000 - 25,000     │ Expansion commence   │
  │ Divergent mi    │ 3,000 - 10,000     │ Refroidissement gaz  │
  │ Divergent sortie│ 500 - 3,000        │ Gaz très dilatés     │
  └─────────────────┴────────────────────┴──────────────────────┘

FACTEURS INFLUENÇANT h_g:

  ┌────────────────────┬────────────────────────────────────────┐
  │ Facteur            │ Effet sur h_g                          │
  ├────────────────────┼────────────────────────────────────────┤
  │ Pression chambre ↑ │ h_g ↑ (∝ P^0.8)                        │
  │ Diamètre col ↓     │ h_g ↑ (∝ D^-0.2 pour référence)        │
  │ Position → col     │ h_g ↑ (maximum au col)                 │
  │ Position → sortie  │ h_g ↓ (minimum à la sortie)            │
  │ T_chambre ↑        │ h_g ↓ légèrement (via σ)               │
  │ T_paroi ↓          │ h_g ↑ légèrement (via σ)               │
  └────────────────────┴────────────────────────────────────────┘


3.6 LIMITATIONS DU MODÈLE DE BARTZ
───────────────────────────────────────────────────────────────

Le modèle de Bartz a des limitations importantes:

❌ NE PREND PAS EN COMPTE:
  - Rayonnement thermique (important si T > 3000 K)
  - Dissociation/recombinaison des gaz
  - Effets de couche limite réactive
  - Turbulence de combustion
  - Effets 3D près de l'injecteur
  - Rugosité de surface
  - Dépôts de suie (cokéfaction)

⚠️ PRÉCISION:
  - Généralement ±20-30% pour h_g
  - Peut être pire dans des conditions extrêmes
  - Sous-estime parfois h_g au col

✅ RECOMMANDATIONS:
  - Utiliser des marges de sécurité (facteur 1.2-1.5)
  - Valider par essais si possible
  - Utiliser CFD pour conception détaillée
  - Comparer avec d'autres corrélations (Rao, Cinjarew)


3.7 COMPARAISON AVEC AUTRES CORRÉLATIONS
───────────────────────────────────────────────────────────────

CORRÉLATION DE RAO (1960):
  Similaire à Bartz mais avec facteur σ modifié.
  Meilleure pour les gaz à haute température.

CORRÉLATION DE CINJAREW:
  Utilisée par l'industrie russe.
  Prend en compte plus de paramètres.

APPROCHE CFD MODERNE:
  - Résolution numérique des équations de Navier-Stokes
  - Modèles de turbulence (k-ε, k-ω SST)
  - Précision bien meilleure mais coût élevé
  - Utilisée pour la conception finale




---

[← Section précédente : Théorie](2-Theorie-Detaillee-du-Transfert-Thermique.md) | [Retour à l'accueil](Home.md) | [Section suivante : Températures de Paroi →](4-Calcul-des-Temperatures-de-Paroi.md)
