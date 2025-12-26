# 🔥 WIKI COMPLET - ANALYSE THERMIQUE DES MOTEURS-FUSÉES

## Table des matières
1. [Introduction](#1-introduction)
2. [Théorie du transfert thermique](#2-théorie-du-transfert-thermique)
3. [Modèle de Bartz](#3-modèle-de-bartz)
4. [Calcul des températures de paroi](#4-calcul-des-températures-de-paroi)
5. [Corrélations de Dittus-Boelter et Gnielinski](#5-corrélations-de-dittus-boelter-et-gnielinski)
6. [Épaisseur critique et ablation](#6-épaisseur-critique-et-ablation)
7. [Propriétés des matériaux](#7-propriétés-des-matériaux)
8. [Propriétés des coolants](#8-propriétés-des-coolants)
9. [Exemples de calcul](#9-exemples-de-calcul)
10. [Références](#10-références)

---

## 1. Introduction

### 1.1 Contexte
Un moteur-fusée génère des températures extrêmes (2500-3500 K) dans la chambre de combustion. Sans refroidissement adéquat, la paroi fondrait en quelques secondes. Cette documentation explique **exactement** comment le logiciel calcule les transferts thermiques et détermine si une configuration est viable.

### 1.2 Le problème thermique
```
     GAZ CHAUDS (T_c ~ 3000 K)
            ↓ q (flux thermique)
    ════════════════════════  ← Paroi côté chaud (T_wall_hot)
    ║                      ║
    ║   PAROI MÉTALLIQUE   ║  ← Épaisseur e, conductivité k
    ║                      ║
    ════════════════════════  ← Paroi côté froid (T_wall_cold)
            ↓ q (flux thermique)
     COOLANT (T_cool ~ 100-300 K)
```

### 1.3 Équation fondamentale
En régime permanent, le flux thermique est **constant** à travers toutes les couches :

$$q = h_g (T_{gaz} - T_{wall,hot}) = \frac{k}{e}(T_{wall,hot} - T_{wall,cold}) = h_c (T_{wall,cold} - T_{cool})$$

Où :
- $q$ = flux thermique (W/m²)
- $h_g$ = coefficient de transfert côté gaz chaud (W/m²·K)
- $h_c$ = coefficient de transfert côté coolant (W/m²·K)
- $k$ = conductivité thermique du matériau (W/m·K)
- $e$ = épaisseur de la paroi (m)

---

## 2. Théorie du transfert thermique

### 2.1 Les trois modes de transfert

#### 2.1.1 Conduction (dans la paroi)
La loi de Fourier décrit le transfert de chaleur par conduction :

$$q = -k \nabla T = \frac{k}{e}(T_1 - T_2)$$

Pour une paroi plane d'épaisseur $e$ :

$$q = \frac{k}{e} \Delta T_{paroi}$$

**Résistance thermique de conduction :**
$$R_{cond} = \frac{e}{k} \quad \text{(m²·K/W)}$$

#### 2.1.2 Convection (gaz → paroi et paroi → coolant)
La loi de Newton du refroidissement :

$$q = h (T_{fluide} - T_{surface})$$

**Résistance thermique de convection :**
$$R_{conv} = \frac{1}{h} \quad \text{(m²·K/W)}$$

#### 2.1.3 Rayonnement (négligé ici)
Dans les moteurs-fusées à paroi refroidie, le rayonnement représente généralement moins de 5% du flux total et est négligé dans ce modèle simplifié.

### 2.2 Circuit thermique équivalent
On peut modéliser le transfert comme un circuit électrique :

```
T_gaz ──[R_conv,gaz]──┬──[R_cond]──┬──[R_conv,cool]── T_cool
                      │            │
                   T_wall,hot   T_wall,cold
```

**Résistance totale :**
$$R_{total} = \frac{1}{h_g} + \frac{e}{k} + \frac{1}{h_c}$$

**Flux thermique :**
$$q = \frac{T_{gaz} - T_{cool}}{R_{total}} = \frac{T_{gaz} - T_{cool}}{\frac{1}{h_g} + \frac{e}{k} + \frac{1}{h_c}}$$

### 2.3 Nombres adimensionnels clés

#### Nombre de Reynolds
$$Re = \frac{\rho v D_h}{\mu} = \frac{v D_h}{\nu}$$

| Régime | Reynolds |
|--------|----------|
| Laminaire | Re < 2300 |
| Transitoire | 2300 < Re < 10000 |
| Turbulent | Re > 10000 |

#### Nombre de Prandtl
$$Pr = \frac{\mu C_p}{k} = \frac{\nu}{\alpha}$$

Le nombre de Prandtl compare la diffusivité de quantité de mouvement à la diffusivité thermique :
- Pr < 1 : diffusion thermique plus rapide (métaux liquides)
- Pr ~ 1 : diffusions égales (gaz)
- Pr > 1 : diffusion de mouvement plus rapide (huiles, eau)

#### Nombre de Nusselt
$$Nu = \frac{h D_h}{k}$$

Le Nusselt est le rapport entre le transfert convectif réel et le transfert conductif pur.

---

## 3. Modèle de Bartz

### 3.1 Origine
L'équation de Bartz (1957) est LA référence pour calculer le coefficient de transfert thermique côté gaz chaud dans les moteurs-fusées. Elle est dérivée de la corrélation de Dittus-Boelter modifiée pour les conditions de propulsion.

### 3.2 Équation complète de Bartz

$$h_g = \frac{0.026}{D_t^{0.2}} \left( \frac{\mu^{0.2} C_p}{Pr^{0.6}} \right) \left( \frac{p_c}{c^*} \right)^{0.8} \left( \frac{D_t}{R_c} \right)^{0.1} \left( \frac{A_t}{A} \right)^{0.9} \sigma$$

Où :
- $D_t$ = diamètre du col (m)
- $\mu$ = viscosité dynamique des gaz (Pa·s)
- $C_p$ = chaleur spécifique à pression constante (J/kg·K)
- $Pr$ = nombre de Prandtl des gaz de combustion
- $p_c$ = pression de chambre (Pa)
- $c^*$ = vitesse caractéristique (m/s)
- $R_c$ = rayon de courbure du col (m)
- $A_t$ = aire du col (m²)
- $A$ = aire locale (m²)
- $\sigma$ = facteur de correction

### 3.3 Facteur de correction σ

$$\sigma = \frac{1}{\left[ \frac{1}{2} \frac{T_{wall}}{T_c} \left(1 + \frac{\gamma-1}{2} M^2 \right) + \frac{1}{2} \right]^{0.68} \left[ 1 + \frac{\gamma-1}{2} M^2 \right]^{0.12}}$$

### 3.4 Formule simplifiée (utilisée dans le code)

Pour simplifier les calculs tout en gardant une bonne précision :

```python
# Coefficient au col (maximum)
hg_throat = (0.026 / Dt^0.2) * (μ^0.2 * Cp / Pr^0.6) * (Pc / c*)^0.8

# Coefficient local (scaling avec le diamètre)
hg_local = hg_throat * (Dt / D_local)^1.8
```

### 3.5 Valeurs typiques de h_g

| Zone | h_g typique (W/m²·K) |
|------|---------------------|
| Chambre | 2,000 - 8,000 |
| Convergent | 5,000 - 15,000 |
| **Col** | **10,000 - 50,000** |
| Divergent (début) | 5,000 - 20,000 |
| Divergent (sortie) | 500 - 3,000 |

### 3.6 Pourquoi le col est critique

Le coefficient de transfert dépend de $(A_t/A)^{0.9}$, donc :
- Au col : $A = A_t$ → rapport = 1 → **h_g maximum**
- Dans la chambre : $A >> A_t$ → rapport petit → h_g plus faible
- En sortie de tuyère : $A >> A_t$ → h_g minimal

---

## 4. Calcul des températures de paroi

### 4.1 Température de paroi côté chaud (T_wall_hot)

C'est la température **critique** - elle ne doit pas dépasser T_max_service ni T_fusion.

**Méthode de calcul :**

En régime permanent, on résout le système d'équations :
$$q = h_g (T_{gaz} - T_{wall,hot})$$
$$q = \frac{k}{e} (T_{wall,hot} - T_{wall,cold})$$

En combinant :
$$T_{wall,hot} = \frac{h_g \cdot T_{gaz} + \frac{k}{e} \cdot T_{wall,cold}}{h_g + \frac{k}{e}}$$

### 4.2 Code de calcul

```python
# Conductance de la paroi
k_over_e = k / e  # W/m²-K

# Température paroi chaude (équilibre thermique)
T_wall_hot = (hg * T_gas + k_over_e * T_wall_cold) / (hg + k_over_e)

# Flux thermique résultant
q = hg * (T_gas - T_wall_hot)  # W/m²
```

### 4.3 Cas limites

#### Paroi très fine (e → 0)
$$\lim_{e \to 0} T_{wall,hot} = T_{wall,cold}$$
La paroi n'offre pas de résistance → température uniforme.

#### Paroi très épaisse (e → ∞)
$$\lim_{e \to \infty} T_{wall,hot} = T_{gaz}$$
Toute la résistance est dans la paroi → le côté chaud atteint T_gaz.

### 4.4 Profil de température dans la paroi

La température varie **linéairement** dans la paroi (conduction 1D, régime permanent) :

$$T(x) = T_{wall,hot} - \frac{q}{k} \cdot x$$

Où $x$ est la distance depuis la surface chaude (0 ≤ x ≤ e).

---

## 5. Corrélations de Dittus-Boelter et Gnielinski

### 5.1 Côté coolant - Calcul de h_c

Le coefficient de transfert côté coolant dépend du régime d'écoulement.

### 5.2 Corrélation de Dittus-Boelter (turbulent, Re > 10000)

$$Nu = 0.023 \cdot Re^{0.8} \cdot Pr^{n}$$

Où :
- $n = 0.4$ pour le chauffage du fluide (notre cas)
- $n = 0.3$ pour le refroidissement du fluide

**Coefficient de transfert :**
$$h_c = Nu \cdot \frac{k_{coolant}}{D_h}$$

### 5.3 Corrélation de Gnielinski (transitoire, 2300 < Re < 10000)

Plus précise dans la zone de transition :

$$Nu = \frac{(f/8)(Re - 1000)Pr}{1 + 12.7(f/8)^{0.5}(Pr^{2/3} - 1)}$$

Où $f$ est le facteur de friction de Darcy :
$$f = (0.79 \ln(Re) - 1.64)^{-2}$$

### 5.4 Écoulement laminaire (Re < 2300)

Pour un flux thermique constant :
$$Nu = 4.36$$

Pour une température de paroi constante :
$$Nu = 3.66$$

### 5.5 Code de calcul

```python
# Nombres adimensionnels
Re = (rho * v * D_h) / mu      # Reynolds
Pr = (mu * Cp) / k_liq          # Prandtl

if Re > 10000:  # Turbulent - Dittus-Boelter
    Nu = 0.023 * Re**0.8 * Pr**0.4
    regime = "turbulent"
    
elif Re > 2300:  # Transitoire - Gnielinski
    f = (0.79 * math.log(Re) - 1.64)**(-2)
    Nu = (f/8) * (Re - 1000) * Pr / (1 + 12.7 * (f/8)**0.5 * (Pr**(2/3) - 1))
    Nu = max(Nu, 4.36)  # Minimum physique
    regime = "transitoire"
    
else:  # Laminaire
    Nu = 4.36
    regime = "laminaire"

# Coefficient de transfert
h_cool = Nu * k_liq / D_h
```

### 5.6 Valeurs typiques de h_c

| Coolant | Régime | h_c typique (W/m²·K) |
|---------|--------|---------------------|
| RP-1 | Turbulent | 5,000 - 20,000 |
| LH2 | Turbulent | 20,000 - 100,000 |
| LOX | Turbulent | 10,000 - 50,000 |
| CH4 | Turbulent | 8,000 - 30,000 |
| Eau | Turbulent | 10,000 - 50,000 |

---

## 6. Épaisseur critique et ablation

### 6.1 Concept d'épaisseur critique

Pour un flux thermique donné, il existe une **épaisseur maximale** au-delà de laquelle la paroi fond.

### 6.2 Calcul de l'épaisseur critique de fusion

En régime permanent :
$$T_{wall,hot} = T_{wall,cold} + \frac{q \cdot e}{k}$$

Pour éviter la fusion ($T_{wall,hot} < T_{melt}$) :
$$e < \frac{k (T_{melt} - T_{wall,cold})}{q}$$

**Épaisseur critique de fusion :**
$$e_{melt} = \frac{k (T_{melt} - T_{wall,cold})}{q}$$

### 6.3 Épaisseur de service maximum

Pour rester sous T_max_service :
$$e_{max} = \frac{k (T_{max,service} - T_{wall,cold})}{q}$$

### 6.4 🔥 ABLATION - Épaisseur sacrificielle

#### Concept
Si l'épaisseur initiale $e_0$ est **supérieure** à $e_{melt}$, une partie de la paroi va fondre jusqu'à atteindre l'équilibre thermique.

#### Épaisseur qui fond (sacrificielle)
$$e_{sacrificielle} = e_0 - e_{melt}$$

**Si $e_{sacrificielle} > 0$ :**
- Les premiers millimètres de la paroi vont fondre
- La masse du moteur diminue
- Le processus s'arrête quand $e = e_{melt}$

#### Calcul détaillé

```python
# Épaisseur critique (équilibre thermique)
e_melt = k * (T_melt - T_wall_cold) / q

# Épaisseur actuelle
e_current = épaisseur_initiale

# Épaisseur sacrificielle
if e_current > e_melt:
    e_sacrificielle = e_current - e_melt
    # Cette épaisseur va fondre!
else:
    e_sacrificielle = 0
    # La paroi survit intacte
```

### 6.5 Dynamique de l'ablation

Le processus d'ablation n'est **pas instantané**. Voici la physique :

1. **Phase initiale** : T_wall_hot augmente rapidement
2. **Atteinte de T_melt** : Le métal commence à fondre en surface
3. **Ablation** : Le métal fondu est emporté par le flux de gaz
4. **Équilibre** : L'épaisseur diminue jusqu'à $e_{melt}$

#### Taux d'ablation approximatif
$$\dot{m}_{ablation} = \frac{q - q_{équilibre}}{L_{fusion} + C_p (T_{melt} - T_{initial})}$$

Où $L_{fusion}$ est la chaleur latente de fusion (J/kg).

### 6.6 Masse perdue par ablation

$$\Delta m = \rho_{métal} \cdot A_{surface} \cdot e_{sacrificielle}$$

Où :
- $\rho_{métal}$ = densité du métal (kg/m³)
- $A_{surface}$ = surface totale refroidie (m²)

### 6.7 Exemple numérique

**Données :**
- Matériau : Cuivre (k = 385 W/m·K, T_melt = 1358 K, ρ = 8960 kg/m³)
- Flux au col : q = 20 MW/m² = 20×10⁶ W/m²
- T_wall_cold : 400 K (coolant RP-1)
- Épaisseur initiale : 5 mm

**Calcul :**
$$e_{melt} = \frac{385 \times (1358 - 400)}{20 \times 10^6} = \frac{385 \times 958}{20 \times 10^6} = 18.4 \text{ mm}$$

**Résultat :** e_melt = 18.4 mm > e_current = 5 mm → **La paroi survit !**

**Cas inverse (flux = 50 MW/m²) :**
$$e_{melt} = \frac{385 \times 958}{50 \times 10^6} = 7.4 \text{ mm}$$

Si e_current = 10 mm :
$$e_{sacrificielle} = 10 - 7.4 = 2.6 \text{ mm vont fondre}$$

---

## 7. Propriétés des matériaux

### 7.1 Table complète des matériaux

| Matériau | k (W/m·K) | T_melt (K) | T_max (K) | ρ (kg/m³) | Usage |
|----------|-----------|------------|-----------|-----------|-------|
| Cuivre (Cu) | 385 | 1358 | 1100 | 8960 | Chambres hautes perfs |
| CuCr (Cuivre-Chrome) | 320 | 1350 | 1050 | 8900 | Standard industrie |
| CuZr (Cuivre-Zirconium) | 340 | 1356 | 1000 | 8920 | Alternative CuCr |
| **AlSi10Mg (SLM)** | 130 | 870 | 573 | 2670 | Impression 3D |
| Inconel 718 | 11.4 | 1609 | 1200 | 8190 | Haute température |
| Inconel 625 | 9.8 | 1623 | 1250 | 8440 | Corrosion + haute T |
| Inox 316L | 16.3 | 1673 | 1100 | 8000 | Low cost |
| Inox 304 | 16.2 | 1723 | 1050 | 7900 | Low cost |
| Niobium (Nb) | 53.7 | 2750 | 2200 | 8570 | Très haute T |
| Molybdène (Mo) | 138 | 2896 | 2400 | 10280 | Extrême T |
| Tungstène (W) | 173 | 3695 | 3000 | 19300 | Col tuyère |
| Titane Ti-6Al-4V | 6.7 | 1933 | 700 | 4430 | Léger mais limite |
| Aluminium 6061 | 167 | 855 | 500 | 2700 | Basse pression |
| Graphite (C) | 120 | 3900 | 3500 | 2200 | Ablatif |
| Rhénium (Re) | 48 | 3459 | 2800 | 21020 | Extrême (coût $$) |

### 7.2 Conductivité vs Température de fusion

```
k (W/m-K)
    ^
400 |  Cu●
    |
300 |     CuCr●  CuZr●
    |
200 |                        W●
    |
150 |              Mo●       Al●
    |     AlSi10Mg●
100 |                  Graphite●
    |                             Nb●  Re●
 50 |
    |
 20 |                     Inox● Inconel●
    |                                  Ti●
  0 +--●--●--●--●--●--●--●--●--●--●--●--→ T_melt (K)
      500 1000 1500 2000 2500 3000 3500
```

**Règle générale :** 
- Haute conductivité → bonne évacuation de chaleur → paroi plus froide
- Haute T_melt → résiste à de plus hauts flux

### 7.3 Choix du matériau selon l'application

| Application | Matériau recommandé | Raison |
|-------------|---------------------|--------|
| Prototype/test | Inox 316L | Pas cher, facile à usiner |
| Impression 3D | AlSi10Mg | Standard SLM |
| Haute performance | CuCr / CuZr | k élevé, Tmelt OK |
| Extrême (Starship) | Inox 304L | Ablation contrôlée |
| Durée de vie longue | Inconel 625 | Résistance mécanique à chaud |

---

## 8. Propriétés des coolants

### 8.1 Table des coolants (depuis RocketCEA)

| Coolant | Cp (J/kg·K) | T_boil (K) | T_crit (K) | ρ (kg/m³) | μ (Pa·s) | k (W/m·K) |
|---------|-------------|------------|------------|-----------|----------|-----------|
| LH2 | 14300 | 20 | 33 | 71 | 1.3e-5 | 0.10 |
| LOX | 1700 | 90 | 155 | 1141 | 2.0e-4 | 0.15 |
| CH4 (LNG) | 3500 | 112 | 191 | 422 | 1.2e-4 | 0.19 |
| RP-1 | 2000 | 490 | 678 | 810 | 1.5e-3 | 0.13 |
| C2H5OH | 2440 | 351 | 514 | 789 | 1.1e-3 | 0.17 |
| N2H4 | 3100 | 387 | 653 | 1004 | 9.0e-4 | 0.50 |
| MMH | 2900 | 360 | 585 | 878 | 8.0e-4 | 0.22 |
| N2O4 | 1560 | 294 | 431 | 1450 | 4.0e-4 | 0.12 |
| H2O | 4186 | 373 | 647 | 1000 | 1.0e-3 | 0.60 |
| NH3 | 4700 | 240 | 406 | 682 | 2.5e-4 | 0.50 |

### 8.2 Facteur de mérite des coolants

Pour comparer les coolants, on utilise le **facteur de mérite** :

$$FM = \rho \cdot C_p \cdot k^{0.6} / \mu^{0.4}$$

Plus FM est élevé, meilleur est le coolant.

| Coolant | Facteur de mérite (relatif) |
|---------|---------------------------|
| LH2 | 1.00 (référence) |
| H2O | 0.85 |
| NH3 | 0.70 |
| CH4 | 0.45 |
| N2H4 | 0.40 |
| C2H5OH | 0.30 |
| RP-1 | 0.25 |
| LOX | 0.20 |

### 8.3 Considérations pratiques

| Coolant | Avantages | Inconvénients |
|---------|-----------|---------------|
| LH2 | Meilleur coolant, haute Isp | Cryogénique extrême, faible densité |
| RP-1 | Stockable, dense, pas cher | Cp faible, viscosité haute |
| CH4 | Bon compromis, propre | Cryogénique |
| LOX | Disponible (oxidizer) | Réactif, T_boil basse |
| H2O | Excellent Cp, pas cher | Lourde, corrosion |

---

## 9. Exemples de calcul

### 9.1 Exemple complet : Moteur RP-1/LOX

**Données d'entrée :**
- Pression chambre : 25 bar
- Diamètre col : 30 mm
- Température chambre : 3200 K
- Coolant : RP-1 à 300 K, 30 bar, 20 m/s
- Matériau : Cuivre-Chrome (CuCr)
- Épaisseur : 3 mm
- Diamètre hydraulique canaux : 3 mm

**Étape 1 : Calcul de h_g (Bartz)**
```
Propriétés gaz (depuis RocketCEA):
- μ = 8.5e-5 Pa·s
- Cp = 2100 J/kg·K  
- Pr = 0.55
- c* = 1700 m/s

hg_throat = (0.026 / 0.030^0.2) × (8.5e-5^0.2 × 2100 / 0.55^0.6) × (25e5 / 1700)^0.8
hg_throat = 0.052 × 130 × 890
hg_throat ≈ 6000 W/m²·K
```

**Étape 2 : Calcul de h_c (Dittus-Boelter)**
```
Propriétés RP-1:
- ρ = 810 kg/m³
- μ = 1.5e-3 Pa·s
- Cp = 2000 J/kg·K
- k = 0.13 W/m·K

Re = (810 × 20 × 0.003) / 1.5e-3 = 32,400 (turbulent!)
Pr = (1.5e-3 × 2000) / 0.13 = 23.1

Nu = 0.023 × 32400^0.8 × 23.1^0.4 = 0.023 × 4180 × 4.3 = 413
h_cool = 413 × 0.13 / 0.003 = 17,900 W/m²·K
```

**Étape 3 : Calcul des températures**
```
k_CuCr = 320 W/m·K
e = 0.003 m
T_gas = 3200 K (au col, prendre T_throat ≈ 0.85 × T_c = 2720 K)
T_cool = 300 K

# Résistances thermiques
R_gaz = 1/6000 = 1.67e-4 m²K/W
R_paroi = 0.003/320 = 9.4e-6 m²K/W
R_cool = 1/17900 = 5.6e-5 m²K/W

R_total = 2.32e-4 m²K/W

# Flux thermique
q = (2720 - 300) / 2.32e-4 = 10.4 MW/m²

# Températures
T_wall_hot = 2720 - q/h_g = 2720 - 10.4e6/6000 = 987 K
T_wall_cold = 300 + q/h_cool = 300 + 10.4e6/17900 = 881 K
ΔT_paroi = 987 - 881 = 106 K ✓ (= q×e/k)
```

**Étape 4 : Vérification**
```
T_wall_hot = 987 K < T_max_service = 1050 K ✅
T_wall_hot = 987 K < T_melt = 1350 K ✅
Marge : 1050 - 987 = 63 K

→ Configuration VIABLE avec 63K de marge
```

**Étape 5 : Épaisseur critique**
```
e_melt = 320 × (1350 - 881) / 10.4e6 = 14.4 mm
e_max_service = 320 × (1050 - 881) / 10.4e6 = 5.2 mm

→ Peut aller jusqu'à 5.2 mm avant dépassement T_max
→ Peut aller jusqu'à 14.4 mm avant fusion
```

### 9.2 Exemple ablation : Que se passe-t-il avec 8 mm ?

**Si on prend e = 8 mm au lieu de 3 mm :**

```python
e = 0.008  # 8 mm

# Nouveau calcul avec e = 8 mm
R_paroi = 0.008/320 = 2.5e-5 m²K/W
R_total = 1.67e-4 + 2.5e-5 + 5.6e-5 = 2.48e-4 m²K/W

q = (2720 - 300) / 2.48e-4 = 9.76 MW/m²

T_wall_cold = 300 + 9.76e6/17900 = 845 K
T_wall_hot = 845 + 9.76e6 × 0.008/320 = 845 + 244 = 1089 K

# Vérification
T_wall_hot = 1089 K > T_max_service = 1050 K ⚠️ DÉPASSEMENT!
T_wall_hot = 1089 K < T_melt = 1350 K ✅ Pas de fusion

# Marge négative de 39K → dégradation accélérée du matériau
```

**Si on prend e = 20 mm :**
```python
e = 0.020  # 20 mm

R_paroi = 0.020/320 = 6.25e-5 m²K/W
R_total = 2.85e-4 m²K/W

q = 2420 / 2.85e-4 = 8.5 MW/m²

T_wall_cold = 300 + 8.5e6/17900 = 775 K
T_wall_hot = 775 + 8.5e6 × 0.020/320 = 775 + 531 = 1306 K

# Vérification  
T_wall_hot = 1306 K < T_melt = 1350 K ✅ Juste!
```

Mais si le flux est légèrement plus élevé ou les conditions légèrement différentes :
```
e_sacrificielle = 20 - 14.4 = 5.6 mm pourraient fondre
```

---

## 10. Références

### 10.1 Articles fondamentaux
1. **Bartz, D.R.** (1957). "A Simple Equation for Rapid Estimation of Rocket Nozzle Convective Heat Transfer Coefficients." *Jet Propulsion*, 27(1), 49-51.

2. **Dittus, F.W. & Boelter, L.M.K.** (1930). "Heat Transfer in Automobile Radiators of the Tubular Type." *University of California Publications in Engineering*, 2(13), 443-461.

3. **Gnielinski, V.** (1976). "New Equations for Heat and Mass Transfer in Turbulent Pipe and Channel Flow." *International Chemical Engineering*, 16(2), 359-368.

### 10.2 Livres de référence
1. **Sutton, G.P. & Biblarz, O.** (2016). *Rocket Propulsion Elements* (9th ed.). Wiley.

2. **Huzel, D.K. & Huang, D.H.** (1992). *Modern Engineering for Design of Liquid-Propellant Rocket Engines*. AIAA.

3. **Incropera, F.P. et al.** (2017). *Fundamentals of Heat and Mass Transfer* (8th ed.). Wiley.

### 10.3 Ressources en ligne
1. **NASA CEA** : https://cearun.grc.nasa.gov/
2. **RocketCEA** (Python) : https://rocketcea.readthedocs.io/
3. **Engineering Toolbox** : https://www.engineeringtoolbox.com/

### 10.4 Standards industriels
1. **NASA SP-125** : "Design of Liquid Propellant Rocket Engines"
2. **AIAA S-080** : "Space Systems - Metallic Pressure Vessels"

---

## Annexe A : Formules rapides

### Aide-mémoire

| Calcul | Formule |
|--------|---------|
| Flux thermique | $q = \Delta T / R_{total}$ |
| Résistance totale | $R = 1/h_g + e/k + 1/h_c$ |
| T paroi hot | $T_{hot} = T_{cold} + q \cdot e / k$ |
| Épaisseur fusion | $e_{melt} = k(T_{melt} - T_{cold})/q$ |
| Épaisseur sacrif. | $e_{sac} = e_0 - e_{melt}$ si $e_0 > e_{melt}$ |
| Reynolds | $Re = \rho v D_h / \mu$ |
| Nusselt (turb.) | $Nu = 0.023 \cdot Re^{0.8} \cdot Pr^{0.4}$ |
| h depuis Nu | $h = Nu \cdot k / D_h$ |

### Ordres de grandeur typiques

| Paramètre | Valeur typique |
|-----------|----------------|
| Flux au col | 10-50 MW/m² |
| h_g au col | 5,000-50,000 W/m²K |
| h_coolant | 5,000-100,000 W/m²K |
| T paroi hot | 600-1200 K |
| Épaisseur | 1-10 mm |

---

*Document généré automatiquement par Rocket Motor Design Plotter v6*
*Dernière mise à jour : Décembre 2025*
