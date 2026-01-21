# 5. Chimie de Combustion (NASA CEA)

## 🔬 Le Code NASA CEA

Le logiciel **SITH MISCHUNG COMBUSTION** intègre ou simule le code **NASA CEA** (Chemical Equilibrium with Applications), développé par le NASA Glenn Research Center.

> **CEA** est l'outil standard de l'industrie pour calculer les compositions chimiques à l'équilibre et les propriétés thermodynamiques des mélanges complexes.

---

## 🎯 Variables Clés de Combustion

### 1️⃣ Rapport de Mélange (O/F ou MR)

**Définition :**
```
O/F = Masse d'Oxydant / Masse de Carburant
```

#### Types de Rapports

| Type | Description | Caractéristiques |
|------|-------------|------------------|
| **O/F Optimal** | Donne l'ISP maximum | Meilleur compromis performance |
| **O/F Stoichiométrique** | Combustion complète parfaite | Température maximale (souvent trop chaud !) |
| **Rich** (O/F < optimal) | Excès de carburant | Température plus basse, peut créer du carbone |
| **Lean** (O/F > optimal) | Excès d'oxydant | Gaz oxydants, température élevée |

#### Exemples Concrets

| Propergol | O/F Optimal | O/F Stoichio | T_c Optimal (K) |
|-----------|-------------|--------------|-----------------|
| LOX/RP-1 | **2.56** | 2.77 | 3590 |
| LOX/CH₄ | **3.4** | 4.0 | 3520 |
| LOX/LH₂ | **6.0** | 8.0 | 3290 |
| LOX/Éthanol | **1.7** | 1.94 | 3430 |

**💡 Note :** On opère généralement légèrement *rich* (O/F < optimal) pour :
- Réduire la température → protéger les matériaux
- Éviter l'oxydation des parois métalliques
- Créer un film protecteur

---

### 2️⃣ Vitesse Caractéristique (C*)

**Définition :**

La vitesse caractéristique mesure l'**efficacité de la chambre de combustion** indépendamment de la tuyère.

```
C* = (P_c × A_t) / ṁ
```

Où :
- **P_c** = Pression de chambre (Pa)
- **A_t** = Aire du col (m²)
- **ṁ** = Débit massique total (kg/s)

**Unité :** m/s

#### Valeurs Typiques

| Propergol | C* Théorique | C* Réel | Efficacité C* |
|-----------|--------------|---------|---------------|
| LOX/RP-1 | 1780 m/s | 1700-1750 m/s | 95-98% |
| LOX/CH₄ | 1860 m/s | 1800-1840 m/s | 96-99% |
| LOX/LH₂ | 2430 m/s | 2350-2400 m/s | 96-99% |

**Efficacité C* :**
```
η_C* = C*_réel / C*_théorique
```

Une efficacité de 95% ou plus indique une bonne combustion et un bon design d'injecteurs.

---

### 3️⃣ Température de Chambre (T_c)

**Température adiabatique de flamme** = température maximale atteinte si toute l'énergie chimique est convertie en chaleur.

#### Facteurs d'Influence

| Facteur | Impact sur T_c |
|---------|----------------|
| ↑ O/F vers stoichio | ↑ T_c augmente |
| ↑ Pression de chambre | ↑ T_c augmente légèrement |
| Carburant plus énergétique | ↑ T_c augmente |
| Dilution (H₂O, N₂) | ↓ T_c diminue |

---

### 4️⃣ Propriétés des Gaz de Combustion

CEA calcule également :

| Propriété | Symbole | Utilité |
|-----------|---------|---------|
| Viscosité dynamique | μ | Calcul de h_g (Bartz) |
| Chaleur spécifique | Cp | Calcul de h_g (Bartz) |
| Nombre de Prandtl | Pr | Calcul de h_g (Bartz) |
| Ratio des chaleurs spécifiques | γ (gamma) | Calcul de vitesse d'éjection |
| Masse molaire moyenne | M | Calcul de propriétés |

**Ces propriétés varient avec la température et la pression locale !**

---

## 🖥️ Utilisation dans le Logiciel

Le logiciel SITH MISCHUNG COMBUSTION :

1. **Prend vos inputs :**
   - Propergols (LOX, RP-1, CH4, etc.)
   - O/F ratio
   - Pression de chambre
   - Rapport d'expansion

2. **Calcule avec CEA :**
   - Température de chambre
   - C* théorique
   - ISP théorique
   - Propriétés des gaz (μ, Cp, Pr, γ)

3. **Utilise ces résultats :**
   - Pour l'équation de Bartz (calcul de h_g)
   - Pour le profil de température
   - Pour dimensionner la tuyère

---

## 📊 Exemple Numérique : LOX/RP-1

### Conditions
- **O/F** = 2.56 (optimal)
- **P_c** = 100 bar = 10 MPa
- **ṁ** = 10 kg/s
- **Expansion** = 15:1

### Résultats CEA
- **T_c** = 3590 K
- **C*** = 1780 m/s
- **ISP (vide)** = 320 s
- **γ** = 1.24
- **μ** = 8.2 × 10⁻⁵ Pa·s
- **Cp** = 2100 J/(kg·K)
- **Pr** = 0.52

### Calcul du Diamètre de Col

À partir de C* :
```
A_t = (ṁ × C*) / P_c
A_t = (10 × 1780) / (10×10⁶)
A_t = 0.00178 m² = 17.8 cm²

D_t = √(4×A_t/π) = 0.0476 m ≈ 47.6 mm
```

---

## 🎓 Points Clés à Retenir

1. ✅ NASA CEA calcule les propriétés d'équilibre chimique
2. ✅ O/F optimal ≠ O/F stoichiométrique
3. ✅ C* mesure l'efficacité de la chambre seule
4. ✅ Les propriétés des gaz (μ, Cp, Pr) sont essentielles pour Bartz

---

## 🔗 Ressources Supplémentaires

- [NASA CEA Website](https://cearun.grc.nasa.gov/)
- [RocketCEA Python Library](https://rocketcea.readthedocs.io/)

---

## 🔄 Navigation

- 🏠 [Retour à l'Accueil](Home)
- 📚 [Retour à Partie 2](Partie-2-Theorie-Avancee)
- ⬅️ [Précédent : Partie 1](Partie-1-Les-Bases)
- ➡️ [Suivant : Équation de Bartz](6-Equation-Bartz)
