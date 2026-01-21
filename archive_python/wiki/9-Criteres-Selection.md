# 9. Critères de Sélection des Matériaux

## 🎯 Les Trois Piliers du Choix

Pour qu'un matériau soit adapté à un moteur-fusée à refroidissement régénératif, il doit exceller dans trois domaines :

---

## 1️⃣ Conductivité Thermique (k) ÉLEVÉE

### Pourquoi c'est important ?

La conductivité thermique détermine la capacité du matériau à **transférer la chaleur** de la surface chaude (côté gaz) vers la surface froide (côté coolant).

```
q = (k / e) × ΔT
```

**Plus k est grand, plus la chaleur est évacuée rapidement !**

### Valeurs Comparatives

| Matériau | k (W/m·K) à 300K | Performance |
|----------|------------------|-------------|
| **Argent** | 429 | ⭐⭐⭐⭐⭐ Excellent (trop cher/mou) |
| **Cuivre pur** | 401 | ⭐⭐⭐⭐⭐ Excellent |
| **CuCr (Cuivre-Chrome)** | 320 | ⭐⭐⭐⭐ Très bon |
| **Aluminium** | 237 | ⭐⭐⭐ Bon (mais fond trop bas) |
| **Acier 316L** | 16 | ⭐ Médiocre |
| **Inconel 718** | 11 | ⭐ Faible |

### 💡 Règle d'Or

> **Pour la paroi interne (liner) :** Privilégier k > 100 W/m·K
> 
> **Pour la paroi externe (structure) :** k peut être plus faible si elle n'est pas directement exposée

---

## 2️⃣ Température de Fusion (T_m) ÉLEVÉE

### Pourquoi c'est important ?

La température de la paroi côté gaz peut atteindre **800-1200 K** selon le design. Le matériau doit avoir une température de fusion **bien supérieure** pour maintenir ses propriétés mécaniques.

### Règle de Sécurité

```
T_wall_max < 0.7 × T_fusion  (conservateur)
T_wall_max < 0.8 × T_fusion  (acceptable)
```

### Valeurs Comparatives

| Matériau | T_fusion (K) | T_wall_max recommandé |
|----------|--------------|------------------------|
| **Tungstène** | 3695 | ~2950 K ⭐⭐⭐⭐⭐ |
| **Molybdène** | 2896 | ~2300 K ⭐⭐⭐⭐ |
| **Inconel 718** | 1609 | ~1280 K ⭐⭐⭐ |
| **Acier 316L** | 1673 | ~1340 K ⭐⭐⭐ |
| **CuCr** | 1358 | ~1085 K ⭐⭐ |
| **Aluminium** | 933 | ~745 K ⭐ |

### ⚠️ Attention

Certains matériaux perdent leur résistance mécanique **avant** d'atteindre le point de fusion !

**Exemple :** Le cuivre à 800 K a perdu 50% de sa résistance mécanique.

---

## 3️⃣ Résistance Mécanique (σ_y) ÉLEVÉE

### Pourquoi c'est important ?

La paroi doit supporter la **pression de chambre** sans se déformer. La contrainte principale est la contrainte circonférentielle (hoop stress).

```
σ_hoop = (P_c × R_internal) / e_wall
```

Pour ne pas plastifier :
```
σ_hoop < σ_yield  (idéalement σ_hoop < 0.7 × σ_yield)
```

### Valeurs Comparatives

| Matériau | σ_y (MPa) à 300K | σ_y (MPa) à 800K | Tenue à chaud |
|----------|------------------|------------------|---------------|
| **Inconel 718** | 1100 | 900 | ⭐⭐⭐⭐⭐ Excellent |
| **Haynes 230** | 400 | 350 | ⭐⭐⭐⭐ Très bon |
| **NARloy-Z (CuAgZr)** | 400 | 250 | ⭐⭐⭐ Bon |
| **Acier 316L** | 290 | 180 | ⭐⭐ Acceptable |
| **CuCr** | 300 | 150 | ⭐⭐ Acceptable |
| **Cuivre pur** | 70 | 30 | ⭐ Faible |

---

## 🔄 Le Triangle des Compromis

Aucun matériau n'est parfait dans les trois domaines ! Il faut faire des **compromis**.

### Visualisation

```
        Conductivité (k)
              ↑
              │
         Cuivre pur ⭐
              │
              │
Résistance ←──┼──→ Température de fusion
   (σ_y)      │         (T_m)
              │
      Inconel ⭐    Tungstène ⭐
              │
              ↓
```

### Stratégies Courantes

| Stratégie | Description | Exemple |
|-----------|-------------|---------|
| **Bi-métallique** | Liner en cuivre (k élevé) + Structure en Inconel (σ_y élevé) | Merlin, RS-25 |
| **Compromis** | Un seul matériau moyennement bon partout | CuCr, NARloy-Z |
| **Haute température** | Matériau réfractaire pour zones extrêmes | Tungstène au col |

---

## 📊 Tableau Comparatif Complet

| Matériau | k (W/m·K) | T_m (K) | σ_y (MPa) | Coût | Usage typique |
|----------|-----------|---------|-----------|------|---------------|
| **CuCr** | 320 | 1358 | 300 | €€ | Liner chambre/col |
| **NARloy-Z** | 365 | 1358 | 400 | €€€€ | NASA, haute perf |
| **Inconel 718** | 11 | 1609 | 1100 | €€€ | Structure externe |
| **Acier 316L** | 16 | 1673 | 290 | € | Structure économique |
| **Tungstène** | 170 | 3695 | 550 | €€€€ | Col haute température |

**Légende coût :** € = bon marché, €€€€ = très coûteux

---

## 🎓 Points Clés à Retenir

1. ✅ **Conductivité thermique** : évacue la chaleur (le cuivre excelle)
2. ✅ **Température de fusion** : limite la température de fonctionnement
3. ✅ **Résistance mécanique** : tient la pression (Inconel excelle)
4. ✅ **Aucun matériau n'est parfait** → compromis ou conception bi-métallique

---

## 🔄 Navigation

- 🏠 [Retour à l'Accueil](Home)
- 📚 [Retour à Partie 3](Partie-3-Materiaux)
- ⬅️ [Précédent : Partie 2](Partie-2-Theorie-Avancee)
- ➡️ [Suivant : Base de Données Matériaux](10-Base-Donnees-Materiaux)
