# 📸 Visual Comparison: Before vs After

This document shows side-by-side examples of the wiki improvements.

---

## Example 1: Table of Contents / Navigation

### ❌ BEFORE (wiki.txt)
```
📖 SOMMAIRE GÉNÉRAL
─────────────────────
PARTIE 1 : LES BASES (Niveau Débutant)
   1. Introduction : Comment ça vole ?
   2. La Tuyère de Laval : Accélérer le son
   3. Pourquoi ça chauffe autant ?
   4. Le principe du Refroidissement Régénératif

PARTIE 2 : THÉORIE AVANCÉE & MATHÉMATIQUES (Niveau Ingénieur)
   5. Chimie de Combustion (NASA CEA)
   6. Transfert Thermique : L'Équation de Bartz
   ...
```
- No clickable links
- Plain text only
- Must scroll to find section
- ASCII art decorations

### ✅ AFTER (wiki/Home.md)
```markdown
## 📖 Table des Matières

### 🎓 [Partie 1 : Les Bases (Niveau Débutant)](Partie-1-Les-Bases)
Introduction accessible aux concepts fondamentaux des moteurs-fusées

1. **[Introduction : Comment ça vole ?](1-Introduction)**
   - Le principe d'action-réaction
   - ISP et performance des moteurs

2. **[La Tuyère de Laval : Accélérer le son](2-Tuyere-de-Laval)**
   - Comprendre la convergent-divergent
   - Le blocage sonique au col
...
```
- ✅ Clickable links to every page
- ✅ Emoji icons for visual hierarchy
- ✅ Sub-bullets showing content
- ✅ Professional Markdown formatting

---

## Example 2: Data Tables

### ❌ BEFORE (wiki.txt)
```
Un moteur-fusée à propergols liquides génère des températures 
extrêmement élevées lors de la combustion:

  • Couple LOX/RP-1:    T_c ≈ 3500-3600 K
  • Couple LOX/LH2:     T_c ≈ 3200-3400 K  
  • Couple LOX/CH4:     T_c ≈ 3500-3600 K
  • Couple N2O4/UDMH:   T_c ≈ 3200-3400 K
  • Couple H2O2/RP-1:   T_c ≈ 2800-3000 K

⚠️  PROBLÈME CRITIQUE:
Ces températures dépassent largement le point de fusion de TOUS 
les métaux et alliages connus:

  • Cuivre fond à:      1358 K (1085°C)
  • Inconel fond à:     1609 K (1336°C)  
  • Tungstène fond à:   3695 K (3422°C)
```
- Hard to scan
- No visual comparison
- Mixed units in text

### ✅ AFTER (wiki/13-Concepts-Fondamentaux.md)
```markdown
### Températures Extrêmes de Combustion

| Couple de Propergols | Température de Chambre (T_c) |
|----------------------|------------------------------|
| **LOX/RP-1** | 3500-3600 K (3227-3327°C) |
| **LOX/LH₂** | 3200-3400 K (2927-3127°C) |
| **LOX/CH₄** | 3500-3600 K (3227-3327°C) |
| **N₂O₄/UDMH** | 3200-3400 K (2927-3127°C) |
| **H₂O₂/RP-1** | 2800-3000 K (2527-2727°C) |

### ⚠️ Problème Critique : Les Limites des Matériaux

| Matériau | Point de Fusion |
|----------|-----------------|
| **Cuivre** | 1358 K (1085°C) |
| **Inconel** | 1609 K (1336°C) |
| **Tungstène** | 3695 K (3422°C) |
```
- ✅ Professional table layout
- ✅ Easy to scan and compare
- ✅ Bold headers for emphasis
- ✅ Consistent unit presentation

---

## Example 3: Formulas and Calculations

### ❌ BEFORE (wiki.txt)
```
EXEMPLE NUMÉRIQUE - Temps avant fusion sans refroidissement:
  Données: CuCr, e=3mm, ρ=8900 kg/m³, Cp=385 J/kg·K
  Flux entrant: q = 30 MW/m² (typique au col)
  
  Énergie pour chauffer 1m² de ΔT = 1000K:
  E = ρ × e × Cp × ΔT = 8900 × 0.003 × 385 × 1000 = 10.3 MJ
  
  Temps: t = E/q = 10.3×10⁶ / 30×10⁶ = 0.34 seconde!

💀 En moins d'une demi-seconde, la paroi atteint sa température 
   de fusion sans refroidissement actif!
```
- Plain text formulas
- Hard to distinguish data from calculations
- No visual structure

### ✅ AFTER (wiki/13-Concepts-Fondamentaux.md)
```markdown
### 📊 Exemple Numérique : Temps avant Fusion

**Scénario :** Paroi en CuCr (Cuivre-Chrome) au col, sans refroidissement

#### Données
​```
Matériau    : CuCr
Épaisseur   : e = 3 mm = 0.003 m
Densité     : ρ = 8900 kg/m³
Chaleur spé : Cp = 385 J/(kg·K)
Flux entrant: q = 30 MW/m² = 30×10⁶ W/m² (typique au col)
​```

#### Calcul

**Énergie nécessaire pour chauffer 1 m² de paroi de ΔT = 1000 K :**
​```
E = ρ × e × Cp × ΔT
E = 8900 × 0.003 × 385 × 1000
E = 10.3 MJ = 10.3×10⁶ J
​```

**Temps pour atteindre cette température :**
​```
t = E / q
t = 10.3×10⁶ / 30×10⁶
t = 0.34 seconde
​```

### 💀 Résultat

> **En moins d'une demi-seconde (0.34 s), la paroi atteint sa température 
> de fusion sans refroidissement actif !**
```
- ✅ Code blocks for data and formulas
- ✅ Clear section headers
- ✅ Quote blocks for emphasis
- ✅ Step-by-step presentation

---

## Example 4: Lists and Comparisons

### ❌ BEFORE (wiki.txt)
```
A) REFROIDISSEMENT RÉGÉNÉRATIF (traité dans ce guide)
   Le propergol (fuel ou oxydant) circule dans des canaux 
   autour de la chambre AVANT d'être injecté et brûlé.
   
   Avantages:
   ✅ Récupère l'énergie thermique (améliore Isp)
   ✅ Pas de perte de masse propulsive
   ✅ Permet fonctionnement continu longue durée
   ✅ Contrôle précis des températures
   
   Inconvénients:
   ❌ Complexité de fabrication (canaux, soudures)
   ❌ Risque de cokéfaction avec hydrocarbures
   ❌ Pertes de charge hydrauliques
   ❌ Coût élevé de fabrication
```
- Basic list format
- No context or explanations
- Hard to compare multiple methods

### ✅ AFTER (wiki/13-Concepts-Fondamentaux.md)
```markdown
### A) Refroidissement Régénératif ⭐ (Traité dans ce guide)

**Principe :** Le propergol (carburant ou oxydant) circule dans des canaux 
autour de la chambre **AVANT** d'être injecté et brûlé.

#### ✅ Avantages

| Avantage | Description |
|----------|-------------|
| **Récupération d'énergie** | L'énergie thermique améliore l'ISP (préchauffage) |
| **Pas de perte de masse** | Toute la masse sert à la propulsion |
| **Fonctionnement longue durée** | Permet des tirs de plusieurs minutes |
| **Contrôle précis** | Ajustement possible du débit de coolant |

#### ❌ Inconvénients

| Inconvénient | Description |
|--------------|-------------|
| **Complexité de fabrication** | Usinage de canaux complexes, soudures difficiles |
| **Risque de cokéfaction** | Avec hydrocarbures (RP-1), dépôts carbonés possibles |
| **Pertes de charge** | Résistance hydraulique dans les canaux étroits |
| **Coût élevé** | Fabrication très coûteuse (€€€€) |

**Exemples :** SpaceX Merlin, RS-25, Vulcain 2, RD-180

---

## 📊 Comparaison des Stratégies

| Stratégie | Efficacité | Complexité | Coût | Durée | Usage Principal |
|-----------|------------|------------|------|-------|-----------------|
| **Régénératif** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | €€€€ | ∞ | Moteurs haute perf |
| **Film** | ⭐⭐⭐ | ⭐⭐ | €€ | Longue | Complément |
| **Ablatif** | ⭐⭐⭐ | ⭐ | €€ | Courte | Moteurs jetables |
...
```
- ✅ Tables with descriptions
- ✅ Visual comparison table
- ✅ Real-world examples
- ✅ Star ratings for quick assessment

---

## Example 5: Page Navigation

### ❌ BEFORE (wiki.txt)
- No navigation
- No page breaks
- Single continuous file
- Must use Ctrl+F to find content

### ✅ AFTER (Every wiki page)
```markdown
## 🔄 Navigation

- 🏠 [Retour à l'Accueil](Home)
- 📚 [Retour à Partie 5](Partie-5-Documentation-Technique)
- ⬅️ [Précédent : Section 12](12-Export-Fabrication)
- ➡️ [Suivant : Section 14](14-Transfert-Thermique)
```
- ✅ Consistent navigation on every page
- ✅ Home link
- ✅ Part overview link
- ✅ Previous/Next links
- ✅ Emoji icons for clarity

---

## Summary of Improvements

### Formatting
| Aspect | Before | After |
|--------|--------|-------|
| Structure | 1 file (4622 lines) | 15+ modular files |
| Tables | 0 | 30+ professional tables |
| Code blocks | 0 | 20+ formatted blocks |
| Links | 0 | 100+ internal links |
| Visual aids | ASCII art | Markdown + Emojis |

### User Experience
| Aspect | Before | After |
|--------|--------|-------|
| Find information | Scroll + Search | Click links |
| Read on mobile | Difficult | Optimized |
| Update content | Edit huge file | Edit one page |
| Print | Poor formatting | Professional |
| Share section | Copy/paste | Share link |

### Professional Quality
| Aspect | Before | After |
|--------|--------|-------|
| Visual appeal | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Readability | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Maintainability | ⭐ | ⭐⭐⭐⭐⭐ |
| GitHub integration | ⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎉 Result

**The wiki has been transformed from a plain text document into a professional, 
modern, and user-friendly documentation system that reflects the quality and 
sophistication of the SITH MISCHUNG COMBUSTION project!**
