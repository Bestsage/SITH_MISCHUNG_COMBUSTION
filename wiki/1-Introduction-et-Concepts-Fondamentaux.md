# 1. INTRODUCTION ET CONCEPTS FONDAMENTAUX

[← Retour à l'accueil](Home.md) | [Section suivante : Théorie Détaillée →](2-Theorie-Detaillee-du-Transfert-Thermique.md)

---

## Table des matières
- [1.1 Pourquoi le refroidissement est-il critique ?](#11-pourquoi-le-refroidissement-est-il-critique-)
- [1.2 Les différentes stratégies de refroidissement](#12-les-différentes-stratégies-de-refroidissement)
- [1.3 Schéma du transfert thermique](#13-schéma-du-transfert-thermique)
- [1.4 Équations fondamentales du transfert](#14-équations-fondamentales-du-transfert)
- [1.5 Ordres de grandeur typiques](#15-ordres-de-grandeur-typiques)

---

## 1.1 POURQUOI LE REFROIDISSEMENT EST-IL CRITIQUE ?

Un moteur-fusée à propergols liquides génère des températures extrêmement élevées lors de la combustion:

- **Couple LOX/RP-1:**    T_c ≈ 3500-3600 K
- **Couple LOX/LH2:**     T_c ≈ 3200-3400 K  
- **Couple LOX/CH4:**     T_c ≈ 3500-3600 K
- **Couple N2O4/UDMH:**   T_c ≈ 3200-3400 K
- **Couple H2O2/RP-1:**   T_c ≈ 2800-3000 K

### ⚠️ PROBLÈME CRITIQUE

Ces températures dépassent largement le point de fusion de TOUS les métaux et alliages connus:

- **Cuivre fond à:**      1358 K (1085°C)
- **Inconel fond à:**     1609 K (1336°C)  
- **Tungstène fond à:**   3695 K (3422°C)

Sans refroidissement, la paroi de la chambre fondrait en quelques MILLISECONDES à quelques SECONDES selon:
- Le flux thermique local
- L'épaisseur de la paroi
- La conductivité thermique du matériau
- La capacité thermique massique

### EXEMPLE NUMÉRIQUE - Temps avant fusion sans refroidissement

**Données:** CuCr, e=3mm, ρ=8900 kg/m³, Cp=385 J/kg·K  
**Flux entrant:** q = 30 MW/m² (typique au col)
  
Énergie pour chauffer 1m² de ΔT = 1000K:
```
E = ρ × e × Cp × ΔT = 8900 × 0.003 × 385 × 1000 = 10.3 MJ
```
  
Temps:
```
t = E/q = 10.3×10⁶ / 30×10⁶ = 0.34 seconde!
```

💀 **En moins d'une demi-seconde, la paroi atteint sa température de fusion sans refroidissement actif!**

---

## 1.2 LES DIFFÉRENTES STRATÉGIES DE REFROIDISSEMENT

Il existe plusieurs méthodes pour gérer la charge thermique:

### A) REFROIDISSEMENT RÉGÉNÉRATIF (traité dans ce guide)

Le propergol (fuel ou oxydant) circule dans des canaux autour de la chambre AVANT d'être injecté et brûlé.

**Avantages:**
- ✅ Récupère l'énergie thermique (améliore Isp)
- ✅ Pas de perte de masse propulsive
- ✅ Permet fonctionnement continu longue durée
- ✅ Contrôle précis des températures

**Inconvénients:**
- ❌ Complexité de fabrication (canaux, soudures)
- ❌ Risque de cokéfaction avec hydrocarbures
- ❌ Pertes de charge hydrauliques
- ❌ Coût élevé de fabrication

### B) REFROIDISSEMENT PAR FILM (Film Cooling)

Une couche de propergol liquide ou gazeux est injectée le long de la paroi, créant une barrière protectrice.

**Avantages:**
- ✅ Simple à implémenter
- ✅ Réduit le flux thermique effectif

**Inconvénients:**
- ❌ Perte d'Isp (propergol non brûlé de façon optimale)
- ❌ Peut perturber la combustion
- ❌ Efficacité limitée dans le temps

### C) REFROIDISSEMENT ABLATIF

La paroi est faite d'un matériau qui s'érode progressivement, absorbant l'énergie par changement de phase.

**Avantages:**
- ✅ Très simple (pas de circulation)
- ✅ Léger pour moteurs à courte durée
- ✅ Fiable (pas de pompes, pas de canaux)

**Inconvénients:**
- ❌ Durée limitée
- ❌ Changement de géométrie pendant le tir
- ❌ Débris dans l'écoulement

### D) REFROIDISSEMENT RADIATIF

La paroi rayonne sa chaleur vers l'espace. Utilisé principalement pour les tuyères de moteurs spatiaux à faible poussée.

**Avantages:**
- ✅ Très simple, léger
- ✅ Pas de fluide de refroidissement

**Inconvénients:**
- ❌ Limité aux faibles flux (< 5 MW/m²)
- ❌ Nécessite matériaux réfractaires (Nb, Mo, W)

### E) TRANSPIRATION (Sweat Cooling)

Le coolant suinte à travers un matériau poreux.

**Avantages:**
- ✅ Très efficace thermiquement

**Inconvénients:**
- ❌ Risque de bouchage des pores
- ❌ Difficulté de fabrication
- ❌ Rarement utilisé en pratique

---

## 1.3 SCHÉMA DU TRANSFERT THERMIQUE

Vue en coupe de la paroi d'un moteur à refroidissement régénératif:

```
     GAZ DE COMBUSTION CHAUDS
     T_gaz ≈ 2800-3500 K (selon T_aw adiabatique)
     Vitesse: Mach 0.1-0.3 (chambre) à Mach 1+ (col)
            │
            │ CONVECTION FORCÉE (coefficient h_g)
            │ q₁ = h_g × (T_gaz - T_wall_hot)
            ↓
    ════════════════════════════════════════  
    ║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║  ← Surface chaude
    ║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║    T_wall_hot
    ║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║
    ║░░░░░░ PAROI MÉTALLIQUE ░░░░░░░░░░░░║  ← Épaisseur e
    ║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║    Conductivité k
    ║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║
    ║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║  ← Surface froide
    ════════════════════════════════════════    T_wall_cold
            │
            │ CONDUCTION (à travers la paroi)
            │ q₂ = (k/e) × (T_wall_hot - T_wall_cold)
            │
            ↓
    ╔══════════════════════════════════════╗
    ║        CANAL DE REFROIDISSEMENT      ║  ← Hauteur h_canal
    ║   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~→      ║    Largeur w_canal
    ║        Coolant en écoulement         ║    T_coolant
    ╚══════════════════════════════════════╝
            │
            │ CONVECTION FORCÉE (coefficient h_c)
            │ q₃ = h_c × (T_wall_cold - T_coolant)
            ↓
    ════════════════════════════════════════
    ║        PAROI EXTERNE (liner)         ║
    ════════════════════════════════════════
```

### PRINCIPE DE CONSERVATION

En régime permanent (steady-state), le flux est CONSTANT à travers toutes les couches:

```
q₁ = q₂ = q₃ = q

q = h_g×(T_gaz - T_wh) = (k/e)×(T_wh - T_wc) = h_c×(T_wc - T_cool)
```

---

## 1.4 ÉQUATIONS FONDAMENTALES DU TRANSFERT

La résolution du problème thermique repose sur l'ANALOGIE ÉLECTRIQUE: le flux de chaleur est analogue au courant, la différence de température à la tension.

### RÉSISTANCES THERMIQUES EN SÉRIE

```
  ┌─────────┐    ┌─────────┐    ┌─────────┐
  │  R_gaz  │────│ R_paroi │────│ R_cool  │
  │  1/h_g  │    │   e/k   │    │  1/h_c  │
  └─────────┘    └─────────┘    └─────────┘
       ↑              ↑              ↑
    T_gaz          T_wall         T_cool
```

**Résistance totale:**
```
R_total = R_gaz + R_paroi + R_cool
R_total = 1/h_g + e/k + 1/h_c   [m²·K/W]
```

**Flux thermique:**
```
q = ΔT_total / R_total
q = (T_gaz - T_coolant) / (1/h_g + e/k + 1/h_c)   [W/m²]
```

### REMARQUE IMPORTANTE

Cette formule suppose des coefficients h constants et une paroi plane. En réalité:
- h_g varie avec la position (maximum au col)
- La géométrie est cylindrique/conique
- T_coolant augmente le long du canal
- Les propriétés varient avec T

---

## 1.5 ORDRES DE GRANDEUR TYPIQUES

Pour un moteur LOX/RP-1 de 100 kN:

### PARAMÈTRES DE CONCEPTION

| Paramètre              | Valeur typique               |
|------------------------|------------------------------|
| Pression chambre       | 30-100 bar                   |
| Température chambre    | 3400-3600 K                  |
| Diamètre col           | 50-150 mm                    |
| Diamètre chambre       | 100-300 mm                   |
| Rapport de section     | 15-40 (selon altitude)       |
| Épaisseur paroi        | 1-5 mm                       |
| Nombre de canaux       | 50-200                       |

### FLUX THERMIQUES

| Zone                   | Flux q (MW/m²)               |
|------------------------|------------------------------|
| Injecteur              | 5 - 15                       |
| Chambre cylindrique    | 5 - 15                       |
| Convergent             | 10 - 30                      |
| Col (MAXIMUM!)         | 20 - 80                      |
| Divergent (début)      | 10 - 30                      |
| Divergent (sortie)     | 1 - 5                        |

### COEFFICIENTS DE TRANSFERT

| Coefficient            | Valeur (W/m²·K)              |
|------------------------|------------------------------|
| h_g (chambre)          | 2,000 - 10,000               |
| h_g (col)              | 10,000 - 50,000              |
| h_c (RP-1)             | 5,000 - 30,000               |
| h_c (LH2)              | 20,000 - 150,000             |
| h_c (CH4)              | 10,000 - 50,000              |

### TEMPÉRATURES DE PAROI

| Surface                | Température (K)              |
|------------------------|------------------------------|
| T_wall_hot (typique)   | 600 - 1000                   |
| T_wall_hot (max admis) | 800 - 1200 selon matériau    |
| T_wall_cold            | 400 - 800                    |
| T_coolant entrée       | 150 - 300                    |
| T_coolant sortie       | 300 - 500                    |

---

[← Retour à l'accueil](Home.md) | [Section suivante : Théorie Détaillée →](2-Theorie-Detaillee-du-Transfert-Thermique.md)
