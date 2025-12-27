# 🔥 GUIDE ULTIME DE CONCEPTION : SITH MISCHUNG COMBUSTION

Bienvenue dans la documentation officielle. Ce guide est structuré pour vous emmener du niveau "Débutant" au niveau "Ingénieur Aérospatial".

## 📖 SOMMAIRE GÉNÉRAL

### PARTIE 1 : LES BASES (Niveau Débutant)
1. Introduction : Comment ça vole ?
2. La Tuyère de Laval : Accélérer le son
3. Pourquoi ça chauffe autant ?
4. Le principe du Refroidissement Régénératif

### PARTIE 2 : THÉORIE AVANCÉE & MATHÉMATIQUES (Niveau Ingénieur)
5. Chimie de Combustion (NASA CEA)
6. Transfert Thermique : L'Équation de Bartz
7. Dimensionnement des Canaux de Refroidissement
8. Mécanique des Fluides & Pertes de Charge

---

## PARTIE 1 : LES BASES (POUR COMPRENDRE)

### 1. INTRODUCTION : LE PRINCIPE D'ACTION-RÉACTION

Une fusée ne "pousse" pas sur l'air (elle marche dans le vide). Elle pousse sur sa propre matière qu'elle éjecte.
C'est la 3ème loi de Newton : Pour chaque action, il y a une réaction égale et opposée.

- **La masse éjectée (mdot)** : Plus on jette de matière, plus on pousse.
- **La vitesse d'éjection (V_e)** : Plus on jette la matière vite, plus on pousse fort.

L'efficacité d'un moteur se mesure en ISP (Impulsion Spécifique).

👉 *Imaginez l'ISP comme la "consommation au 100km" de votre voiture, mais à l'envers. Plus l'ISP est haute, moins vous consommez pour la même poussée.*

### 2. LA TUYÈRE DE LAVAL : PASSER LE MUR DU SON

Pour accélérer un gaz au-delà de la vitesse du son (Mach 1), il faut une forme très spécifique : un sablier.

- **Convergent** : Le gaz est subsonique. On rétrécit le passage, le gaz accélère (comme un tuyau d'arrosage pincé).
- **Col (Throat)** : C'est le point le plus étroit. Le gaz atteint EXACTEMENT la vitesse du son (Mach 1).
- **Divergent** : Le gaz est supersonique. Pour l'accélérer encore, il faut ÉLARGIR le passage.

### 3. LE PROBLÈME THERMIQUE

| Matériau | Température de Fusion |
|----------|----------------------|
| Acier | ~1400°C |
| Cuivre | ~1080°C |
| Aluminium | ~600°C |

Dans la chambre, la température atteint **3000°C à 3600°C**.

⚠️ **Conclusion** : Sans refroidissement actif, le moteur fond instantanément.

Le point le plus critique est le **COL**. C'est là que le transfert de chaleur est le plus violent (flux thermique max).

---

## PARTIE 2 : THÉORIE AVANCÉE (POUR CONCEVOIR)

### 5. CHIMIE DE COMBUSTION (NASA CEA)

Le logiciel intègre ou simule le code NASA CEA (Chemical Equilibrium with Applications).

**Variables Clés:**

| Variable | Description |
|----------|-------------|
| MR (O/F) | Masse d'oxydant / Masse de carburant |
| O/F Optimal | Donne l'ISP max |
| C* | Vitesse Caractéristique de la chambre |

Formule de la vitesse caractéristique:

```
C* = P_chambre * A_col / mdot
```

### 6. TRANSFERT THERMIQUE : L'ÉQUATION DE BARTZ

Pour estimer la chaleur qui attaque la paroi (h_g : coefficient de convection gaz), on utilise l'équation semi-empirique de Bartz :

```
h_g = (0.026 / Dt^0.2) * ((µ^0.2 * Cp) / Pr^0.6) * (Pc / c*)^0.8 * σ
```

**Paramètres:**
- `Dt` : Diamètre au col
- `µ, Cp, Pr` : Propriétés du gaz (Viscosité, Chaleur spécifique, Prandtl)
- `Pc` : Pression chambre
- `σ` : Facteur de correction de couche limite

👉 **Points clés:**
- Plus la pression est haute, plus ça chauffe (exposant 0.8)
- Plus le moteur est petit, plus ça chauffe ! (Les petits moteurs sont plus durs à refroidir)

---

## PARTIE 3 : SCIENCE DES MATÉRIAUX

### 9. CRITÈRES DE SÉLECTION

Pour une chambre de combustion, on cherche le compromis impossible :

1. **Conductivité Thermique (k) ÉLEVÉE** : Pour évacuer la chaleur
2. **Température de Fusion ÉLEVÉE** : Pour ne pas fondre
3. **Résistance Mécanique (σ_y) ÉLEVÉE** : Pour tenir la pression

### 10. BASE DE DONNÉES DÉTAILLÉE

#### 🟢 LES CUIVRES (Le choix standard)

| Alliage | Conductivité (W/mK) | Avantages | Inconvénients |
|---------|---------------------|-----------|---------------|
| Cu-OFHC | 390 | Conductivité extrême | Très mou |
| CuCr | ~320 | Bon compromis | Résistance moyenne |
| CuZr | ~320 | Haute température | Coût élevé |
| GlidCop (Al-15) | ~365 | Reste dur à chaud | Cher |
| GRCop-42 | ~330 | Imprimable 3D | Nouveau matériau |

- **Cuivre pur (Cu-OFHC)** : Conductivité extrême (390 W/mK), mais très mou
- **Cuivre-Chrome (CuCr)** : Le compromis classique. Bonne conductivité (~320), résistance correcte
- **GlidCop (Al-15)** : Cuivre dopé à l'alumine. Reste dur même très proche de son point de fusion
- **CuCrNb (GRCop-42)** : Le roi actuel (développé pour SpaceX/Raptor). Imprimable en 3D

#### ⚪ LES SUPERALLIAGES

| Alliage | Conductivité (W/mK) | T_max | Application |
|---------|---------------------|-------|-------------|
| Inconel 718 | 10-12 | 1200°C+ | Extensions de tuyère |
| Inconel 625 | 10-12 | 1200°C+ | Gros moteurs |
| Monel 400 | 22 | 1000°C | Résistant LOX |

---

## PARTIE 4 : GUIDE DU LOGICIEL

### 11. UTILISATION DE L'OPTIMISEUR

L'onglet "Optimiseur" utilise l'algorithme **Differential Evolution** (Scipy).

**Configuration:**

1. **Variables** : Cochez ce que l'ordi peut modifier
   - Épaisseur paroi (ex: 1mm à 5mm)
   - Nombre de canaux
   
2. **Contraintes** : Cochez ce qui est INTERDIT
   - Ex: T_paroi > 1000 K
   
3. **Objectif** :
   - **Min Masse** : Utile pour le vol
   - **Max Marge** : Utile pour la sécurité/durée de vie
   - **Min Delta P** : Utile si vos pompes sont faibles

### 12. EXPORT CAD & FABRICATION

Le logiciel génère des fichiers pour la CAO (Fusion 360, SolidWorks).

| Format | Description | Usage |
|--------|-------------|-------|
| STEP | Solide complet (Volume) | Simulation CFD/thermique |
| DXF | Profil 2D | Import dans Sketch + Révolution |
| STL | Maillage triangulé | Impression 3D rapide |

⚠️ **Note sur les canaux** : Les canaux générés sont simplifiés (rectangulaires). Pour l'impression 3D, ajoutez des congés (fillets) ou utilisez une forme en goutte d'eau.

---

## Références & Bibliographie

**Sources principales:**
- NASA CEA Documentation
- Huzel & Huang - Modern Engineering for Design of Liquid-Propellant Rocket Engines
- Sutton & Biblarz - Rocket Propulsion Elements

**Ressources en ligne:**
- [NASA Technical Reports Server](https://ntrs.nasa.gov/)
- [SpaceX Engineering Blog](https://www.spacex.com/)

---

*"May the Thrust be with you." 🚀*
