# 2. THÉORIE DÉTAILLÉE DU TRANSFERT THERMIQUE

[← Section précédente : Introduction](1-Introduction-et-Concepts-Fondamentaux.md) | [Retour à l'accueil](Home.md) | [Section suivante : Modèle de Bartz →](3-Modele-de-Bartz.md)

---

## Table des matières
- [2.1 La conduction thermique](#21-la-conduction-thermique)
- [2.2 La convection thermique](#22-la-convection-thermique)
- [2.3 Les nombres adimensionnels](#23-les-nombres-adimensionnels)

---

Cette section développe les fondements physiques et mathématiques du transfert de chaleur dans les moteurs-fusées.

## 2.1 LA CONDUCTION THERMIQUE

### 2.1.1 Loi de Fourier

La conduction est le transfert d'énergie thermique par agitation moléculaire et interaction électronique dans un milieu solide (ou fluide immobile).

**ÉQUATION DE FOURIER (forme différentielle):**
```
q⃗ = -k × ∇T
```

Où:
- `q⃗` = vecteur flux thermique [W/m²]
- `k` = conductivité thermique [W/(m·K)]
- `∇T` = gradient de température [K/m]

Le signe négatif indique que le flux va des zones chaudes vers les zones froides.

**Pour une paroi plane 1D:**
```
q = -k × dT/dx = k × (T_hot - T_cold) / e
q = k × ΔT / e   [W/m²]
```

**RÉSISTANCE THERMIQUE DE CONDUCTION:**
```
R_cond = e / k   [m²·K/W]
ΔT = q × R_cond
```

Plus k est élevé, plus la résistance est faible, plus le transfert est efficace.

### 2.1.2 Conductivité des matériaux pour moteurs-fusées

La conductivité k varie selon:
- La composition du matériau
- La température (généralement ↓ quand T ↑ pour métaux)
- L'état cristallin
- Les impuretés

**TABLEAU DES CONDUCTIVITÉS DÉTAILLÉ:**

| Matériau         | k (W/m·K) à 300K | k (W/m·K) à 500K | k (W/m·K) à 800K | k (W/m·K) à 1000K |
|------------------|------------------|------------------|------------------|-------------------|
| Cuivre pur       | 401              | 386              | 357              | 337               |
| CuCr (C18200)    | 324              | 315              | 298              | 285               |
| CuCrZr           | 315              | 305              | 288              | 275               |
| GRCop-84 (NASA)  | 298              | 285              | 265              | 250               |
| Inconel 718      | 11.4             | 14.7             | 19.2             | 22.1              |
| Inconel 625      | 9.8              | 12.8             | 17.3             | 20.5              |
| Inox 316L        | 16.3             | 18.9             | 22.5             | 25.2              |
| Inox 304         | 16.2             | 18.6             | 22.0             | 24.5              |
| Niobium          | 53.7             | 55.1             | 59.3             | 62.0              |
| C103 (Nb alloy)  | 44.2             | 46.5             | 51.2             | 54.5              |
| Molybdène        | 138              | 126              | 112              | 105               |
| TZM (Mo alloy)   | 120              | 115              | 105              | 98                |
| Tungstène        | 173              | 156              | 132              | 118               |
| Rhénium          | 47.9             | 44.5             | 40.2             | 38.0              |
| Tantale          | 57.5             | 56.0             | 57.5             | 59.0              |
| AlSi10Mg (SLM)   | 130              | 138              | -                | -                 |
| Ti-6Al-4V        | 6.7              | 8.5              | 12.0             | 15.0              |
| Graphite (ISO)   | 120              | 100              | 80               | 70                |
| C/C composite    | 50-150           | 70-120           | 80-100           | 85-95             |

### REMARQUES SUR LES ALLIAGES DE CUIVRE

#### • CuCr (C18200 / "Chromium Copper")
- Contient ~1% Cr
- Bonne conductivité + résistance mécanique
- T_max service ≈ 1050 K (ramollissement)
- Très utilisé: Merlin (SpaceX), RS-25 (NASA)

#### • CuCrZr (C18150)
- Contient ~0.8% Cr + 0.08% Zr
- Meilleure tenue à chaud que CuCr
- T_max service ≈ 1100 K
- Utilisé: RD-170 (Energomash)

#### • GRCop-84 (NASA Glenn)
- Cu + 8% Cr + 4% Nb (nano-particules)
- Développé spécifiquement pour moteurs-fusées
- Excellente résistance au fluage à haute T
- T_max service ≈ 1200 K
- Utilisé: SLS RS-25 upgrades, Relativity Terran

### 2.1.3 Géométrie cylindrique

Pour une paroi cylindrique (chambre, tuyère):
```
q_radial = (2π × k × L × ΔT) / ln(r_ext/r_int)
Résistance: R_cyl = ln(r_ext/r_int) / (2π × k × L)
```

Pour des parois minces (e << r_moy), on peut approximer:
```
R_cyl ≈ e / (k × A_moy)  où A_moy = 2π × r_moy × L
```

---

## 2.2 LA CONVECTION THERMIQUE

### 2.2.1 Loi de Newton du refroidissement

La convection est le transfert d'énergie entre une surface solide et un fluide en mouvement.

**ÉQUATION DE NEWTON:**
```
q = h × (T_surface - T_fluide)   [W/m²]
```

Où:
- `h` = coefficient de transfert convectif [W/(m²·K)]
- `T_surface` = température de la paroi [K]
- `T_fluide` = température du fluide [K]

Le coefficient h dépend de nombreux facteurs:
- Type d'écoulement (laminaire, turbulent)
- Vitesse du fluide
- Propriétés thermophysiques (ρ, μ, Cp, k_fluide)
- Géométrie du canal
- Rugosité de surface
- Effets d'entrée

**RÉSISTANCE THERMIQUE DE CONVECTION:**
```
R_conv = 1 / h   [m²·K/W]
```

### 2.2.2 Types de convection

**CONVECTION NATURELLE:**
- Le mouvement du fluide est dû à la différence de densité causée par le gradient de température
- h ≈ 5-25 W/m²·K (air)
- → Non pertinent pour les moteurs-fusées!

**CONVECTION FORCÉE:**
- Le mouvement du fluide est imposé par une pompe/turbine
- h ≈ 50 - 200,000 W/m²·K selon le fluide et les conditions
- → C'est le cas dans les moteurs-fusées

**ÉBULLITION:**
- Changement de phase liquide → vapeur
- h peut atteindre 100,000+ W/m²·K
- ⚠️ Éviter l'ébullition non contrôlée (DNB = crise d'ébullition)

### 2.2.3 Couche limite thermique

Près de la paroi, il existe une "couche limite thermique" où la température varie de T_surface à T_fluide.

**CÔTÉ GAZ CHAUD:**
- Épaisseur couche limite: δ_th ≈ 0.1-1 mm
- C'est là que se concentre la résistance thermique
- La turbulence améliore le mélange → h_g plus élevé

**CÔTÉ COOLANT:**
- Épaisseur couche limite: δ_th ≈ 0.01-0.5 mm
- Canaux étroits → meilleur transfert
- Turbulence très importante pour h_c élevé

**LIEN AVEC h:**
```
h ≈ k_fluide / δ_th
```

Plus la couche limite est mince, plus h est élevé.

---

## 2.3 LES NOMBRES ADIMENSIONNELS

Les corrélations de transfert thermique utilisent des groupements adimensionnels permettant de généraliser les résultats expérimentaux.

### 2.3.1 Nombre de Reynolds (Re)

**DÉFINITION:**
```
Re = ρ × v × D_h / μ = v × D_h / ν
```

Où:
- `ρ` = masse volumique [kg/m³]
- `v` = vitesse moyenne [m/s]
- `D_h` = diamètre hydraulique [m]
- `μ` = viscosité dynamique [Pa·s]
- `ν` = viscosité cinématique [m²/s] = μ/ρ

**SIGNIFICATION PHYSIQUE:**
```
Re = Forces d'inertie / Forces visqueuses
```

**RÉGIMES D'ÉCOULEMENT:**

| Re                 | Régime                              |
|--------------------|-------------------------------------|
| Re < 2,300         | LAMINAIRE                           |
|                    | Écoulement ordonné en couches       |
|                    | Profil de vitesse parabolique       |
|                    | Transfert thermique faible          |
| 2,300 < Re < 10,000| TRANSITOIRE                         |
|                    | Intermittence turbulente            |
|                    | Comportement imprévisible           |
|                    | À éviter si possible!               |
| Re > 10,000        | TURBULENT DÉVELOPPÉ                 |
|                    | Mélange chaotique efficace          |
|                    | Profil de vitesse aplati            |
|                    | Excellent transfert thermique!      |

**DIAMÈTRE HYDRAULIQUE:**

Pour un canal non-circulaire:
```
D_h = 4 × A / P
```

Où:
- `A` = aire de la section [m²]
- `P` = périmètre mouillé [m]

Exemples:
- Canal rectangulaire (w × h): `D_h = 4×w×h / (2w+2h) = 2wh/(w+h)`
- Canal carré (a × a): `D_h = a`
- Anneau (R_ext, R_int): `D_h = 2×(R_ext - R_int)`

**VALEURS TYPIQUES DANS LES MOTEURS:**

| Fluide/Zone        | Re typique                       |
|--------------------|----------------------------------|
| Gaz chambre        | 10⁵ - 10⁷ (hautement turbulent)  |
| RP-1 dans canaux   | 10⁴ - 10⁵                        |
| LH2 dans canaux    | 10⁵ - 10⁶                        |
| CH4 dans canaux    | 10⁴ - 10⁵                        |
| LOX dans canaux    | 10⁴ - 10⁵                        |

### 2.3.2 Nombre de Prandtl (Pr)

**DÉFINITION:**
```
Pr = μ × Cp / k = ν / α
```

Où:
- `μ` = viscosité dynamique [Pa·s]
- `Cp` = capacité thermique massique [J/(kg·K)]
- `k` = conductivité thermique [W/(m·K)]
- `ν` = viscosité cinématique [m²/s]
- `α` = diffusivité thermique [m²/s]

**SIGNIFICATION PHYSIQUE:**
```
Pr = Diffusivité de quantité de mouvement / Diffusivité thermique
Pr = Épaisseur couche limite dynamique / Épaisseur couche limite thermique
```

**INTERPRÉTATION:**

| Pr                 | Signification                       |
|--------------------|-------------------------------------|
| Pr << 1            | MÉTAUX LIQUIDES                     |
| (0.001-0.03)       | Diffusion thermique >> diffusion    |
|                    | de quantité de mouvement            |
|                    | Ex: Na, K, NaK, Hg, Li              |
| Pr ≈ 0.7-1.0       | GAZ                                 |
|                    | Couches limites comparables         |
|                    | Ex: Air, N2, O2, gaz de combustion  |
| Pr > 1             | LIQUIDES                            |
| (1-1000)           | Diffusion momentum >> diffusion     |
|                    | thermique                           |
|                    | Ex: H2O (Pr≈6), RP-1 (Pr≈20-50)     |

**VALEURS TYPIQUES:**

| Fluide             | Pr (approximatif)                |
|--------------------|----------------------------------|
| Gaz de combustion  | 0.7 - 0.9                        |
| Hydrogène liquide  | 0.7 - 1.5                        |
| Méthane liquide    | 2 - 5                            |
| LOX                | 2 - 4                            |
| RP-1 / Kérosène    | 10 - 100 (selon T)               |
| Éthanol            | 10 - 50                          |
| Eau                | 1 - 10 (selon T)                 |

### 2.3.3 Nombre de Nusselt (Nu)

**DÉFINITION:**
```
Nu = h × D_h / k_fluide
```

Où:
- `h` = coefficient de convection [W/(m²·K)]
- `D_h` = diamètre hydraulique [m]
- `k_fluide` = conductivité du fluide [W/(m·K)]

**SIGNIFICATION PHYSIQUE:**
```
Nu = Transfert convectif réel / Transfert conductif pur
```

- `Nu = 1` signifie que la convection n'améliore pas le transfert par rapport à la conduction seule
- `Nu >> 1` signifie une amélioration significative

**UTILISATION:**

Une fois Nu calculé via une corrélation, on obtient h:
```
h = Nu × k_fluide / D_h
```

**VALEURS TYPIQUES:**
- Écoulement laminaire: Nu ≈ 3.66-4.36
- Écoulement turbulent: Nu ≈ 100-1000
- Ébullition: Nu >> 1000

### 2.3.4 Autres nombres utiles

**NOMBRE DE STANTON (St):**
```
St = h / (ρ × v × Cp) = Nu / (Re × Pr)
```
Utilisé dans les analyses de couche limite. Représente le transfert thermique adimensionnel.

**NOMBRE DE BIOT (Bi):**
```
Bi = h × L_c / k_solide
```
Où L_c = caractéristique longueur du solide (e.g., épaisseur)

- Si `Bi << 0.1`: Température uniforme dans le solide
- Si `Bi >> 0.1`: Gradient de température significatif

**NOMBRE DE FOURIER (Fo):**
```
Fo = α × t / L²
```
Temps adimensionnel pour les problèmes transitoires. α = diffusivité thermique du solide.

**NOMBRE DE MACH (Ma):**
```
Ma = v / a  (a = vitesse du son)
```
Important côté gaz: effets de compressibilité.

---

[← Section précédente : Introduction](1-Introduction-et-Concepts-Fondamentaux.md) | [Retour à l'accueil](Home.md) | [Section suivante : Modèle de Bartz →](3-Modele-de-Bartz.md)
