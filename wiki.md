  GUIDE ULTIME DE CONCEPTION : SITH MISCHUNG COMBUSTION
════════════════════════════════════════════════════════════════════
Bienvenue dans la documentation officielle. Ce guide est structuré pour vous emmener du niveau "Débutant" au niveau "Ingénieur Aérospatial".

 SOMMAIRE GÉNÉRAL
─────────────────────
PARTIE 1 : LES BASES (Niveau Débutant)
   1. Introduction : Comment ça vole ?
   2. La Tuyère de Laval : Accélérer le son
   3. Pourquoi ça chauffe autant ?
   4. Le principe du Refroidissement Régénératif

PARTIE 2 : THÉORIE AVANCÉE & MATHÉMATIQUES (Niveau Ingénieur)
   5. Chimie de Combustion (NASA CEA)
   6. Transfert Thermique : L'Équation de Bartz
   7. Dimensionnement des Canaux de Refroidissement
   8. Mécanique des Fluides & Pertes de Charge

PARTIE 3 : SCIENCE DES MATÉRIAUX
   9. Critères de Sélection
   10. Base de Données Détaillée

PARTIE 4 : GUIDE DU LOGICIEL
   11. Guide de l'Interface et Analyse
   12. Outils Avancés et Production

PARTIE 5 : DOCUMENTATION TECHNIQUE APPROFONDIE
   13. Analyse Thermique Complète
   14. Modèle de Bartz Détaillé
   15. Propriétés des Matériaux
   16. Propriétés des Coolants
   17. Exemples de Calculs
   18. Références & Bibliographie

════════════════════════════════════════════════════════════════════
   PARTIE 1 : LES BASES (Niveau Débutant & Intermédiaire)
════════════════════════════════════════════════════════════════════

## 1. INTRODUCTION : LE PRINCIPE DE LA PROPULSION
────────────────────────────────────────────────────────────────────
Une fusée ne "pousse" pas sur l'air ambiant. Elle fonctionne selon le principe de **conservation de la quantité de mouvement**. Elle éjecte de la masse à haute vitesse dans une direction, ce qui crée une force (poussée) dans la direction opposée.

### 1.1 La Troisième Loi de Newton
> "Pour chaque action, il y a une réaction égale et opposée."

La force de poussée $F$ (Thrust) est générée par l'expulsion des gaz. Elle se définit par l'équation fondamentale :

$$ F = \dot{m} \cdot V_e + (P_e - P_a) \cdot A_e $$

*   $\dot{m}$ : Débit massique (kg/s) - La quantité de matière éjectée.
*   $V_e$ : Vitesse d'éjection des gaz (m/s).
*   $P_e$ : Pression des gaz à la sortie de la tuyère.
*   $P_a$ : Pression atmosphérique ambiante.
*   $A_e$ : Aire de la section de sortie.

### 1.2 L'efficacité : Impulsion Spécifique (Isp)
L'Isp est la mesure reine de l'efficacité d'un moteur. Elle représente la durée pendant laquelle un kilogramme de propergol peut produire une poussée d'un kilogramme-force.

$$ I_{sp} = \frac{F}{\dot{m} \cdot g_0} = \frac{V_{eq}}{g_0} $$

*   Plus l'Isp est élevée, moins vous consommez de carburant pour une même mission.
*   **Analogie** : C'est l'équivalent des "litres aux 100 km" pour une voiture, mais inversé (plus c'est haut, mieux c'est).

### 1.3 L'Équation de Tsiolkovsky
C'est l'équation qui dicte la loi spatiale. Elle relie la vitesse finale de la fusée à son efficacité et sa masse.

$$ \Delta v = I_{sp} \cdot g_0 \cdot \ln \left( \frac{m_{initial}}{m_{final}} \right) $$

Pour aller en orbite, il faut un $\Delta v$ d'environ 9.4 km/s. Comme le logarithme ($\ln$) écrase la valeur du ratio de masse, la seule façon efficace de gagner de la vitesse est d'augmenter l'Isp ($V_e$).

## 2. LA TUYÈRE DE LAVAL : THERMODYNAMIQUE DES GAZ
────────────────────────────────────────────────────────────────────
Pour transformer l'énergie chimique (combustion) en énergie cinétique (vitesse), on utilise une tuyère de Laval (forme sablier). Son rôle est de détendre le gaz pour l'accélérer.

### 2.1 Le mécanisme de conversion
Dans la chambre, le gaz est chaud et sous haute pression (haute Enthalpie $h$).
Dans la tuyère, on convertit cette enthalpie en vitesse :

$$ V_e = \sqrt{2 \cdot \eta \cdot (h_{chambre} - h_{sortie})} $$

### 2.2 Les trois zones critiques
1.  **Convergent (Subsonique, $M < 1$)** :
    Le gaz accélère en passant dans une section qui rétrécit. C'est intuitif (effet Venturi).
2.  **Col (Sonique, $M = 1$)** :
    C'est le goulot d'étranglement. Ici, le gaz atteint exactement la vitesse du son. Le débit est "bloqué" (Choked Flow). On ne peut pas pousser plus de débit en augmentant la pression chambre.
3.  **Divergent (Supersonique, $M > 1$)** :
    C'est la partie contre-intuitive. Pour accélérer un gaz supersonique, il faut **élargir** le passage. La densité du gaz chute plus vite que l'augmentation de la surface, forçant le gaz à accélérer pour conserver le débit.

### 2.3 Le rapport de détende (Area Ratio $\epsilon$)
C'est le paramètre géométrique principal de la tuyère :

$$ \epsilon = \frac{A_e}{A_t} $$

*   $A_e$ : Aire de sortie.
*   $A_t$ : Aire au col.
*   Un grand $\epsilon$ est nécessaire pour le vide (grosse cloche).
*   Un petit $\epsilon$ est optimal pour le niveau de la mer (pour éviter le décollement de flux).

## 3. LE PROBLÈME THERMIQUE : GÉRER L'ENFER
────────────────────────────────────────────────────────────────────
La température de combustion ($T_c$) dépasse souvent 3500 K (3200°C). Aucun matériau solide connu ne résiste à cette température sur le long terme.

### 3.1 Points de fusion vs Combustion
*   **Combustion LOX/RP-1** : ~3600 K
*   **Tungstène (Métal le plus résistant)** : 3695 K (limite, lourd et cassant)
*   **Cuivre (Meilleur conducteur)** : 1358 K
*   **Inconel (Superalliage)** : ~1600 K

**ATTENTION:** **Conclusion** : La paroi du moteur est toujours en péril immédiat. Elle ne survit que grâce au refroidissement actif.

### 3.2 Le Flux Thermique ($q$)
Ce n'est pas seulement la température qui compte, mais la quantité d'énergie transférée par seconde et par mètre carré.

$$ q = h_g (T_{aw} - T_{wg}) $$

*   $h_g$ : Coefficient de convection des gaz (très élevé au col).
*   $T_{aw}$ : Température adiabatique de paroi (proche de la temp. gaz).
*   $T_{wg}$ : Température de la paroi côté gaz.

Le flux thermique au col peut dépasser **50 MW/m²** (l'équivalent de la puissance de 5000 fers à repasser concentrée sur 1 mètre carré).

## 4. LE REFROIDISSEMENT RÉGÉNÉRATIF
────────────────────────────────────────────────────────────────────
C'est la solution élégante utilisée sur presque tous les moteurs à ergols liquides performants (Raptor, Merlin, RS-25, Vulcain).

### 4.1 Le Concept
On utilise l'un des propergols (généralement le carburant, ex: Hydrogène ou Kérosène) comme liquide de refroidissement.
1.  Le carburant froid circule dans des canaux usinés dans la paroi de la chambre.
2.  Il absorbe la chaleur de la paroi (agissant comme un radiateur).
3.  Le carburant réchauffé est ensuite injecté dans la chambre pour brûler.

### 4.2 Bilan Énergétique
L'énergie n'est pas perdue (contrairement au refroidissement ablatif ou radiatif), elle est réinjectée dans le cycle. Cela augmente l'enthalpie initiale des réactifs et améliore légèrement le rendement global.

### 4.3 Limites Physiques
Le refroidissement est limité par deux facteurs :
1.  **Ébullition (Boiling)** : Si le liquide bout dans les canaux, il forme un film de vapeur isolant (Film Boiling / crise d'ébullition). La paroi n'est plus refroidie et fond instantanément.
2.  **Cokéfaction (Pour les hydrocarbures)** : Si le Kérosène ou le Méthane chauffe trop, il se polymérise et dépose de la suie isolante ("coke") qui bouche les canaux.


════════════════════════════════════════════════════════════════════
   PARTIE 2 : THÉORIE AVANCÉE (POUR CONCEVOIR)
════════════════════════════════════════════════════════════════════
## 5. CHIMIE DE COMBUSTION (NASA CEA)
────────────────────────────────────────────────────────────────────
Pour prédire les performances, il faut comprendre la chimie. Le logiciel utilise les données standard NASA CEA (Chemical Equilibrium with Applications).

### 5.1 La Réaction de Combustion
C'est une réaction d'oxydoréduction exothermique rapide.
$$ \text{Oxydant} + \text{Carburant} \rightarrow \text{Produits de Combustion} + \text{Chaleur} $$

Exemple (Méthalox) :
$$ CH_4 + 2O_2 \rightarrow CO_2 + 2H_2O $$

### 5.2 Le Ratio de Mélange ($O/F$)
C'est le paramètre de contrôle principal de l'injecteur :
$$ O/F = \frac{\dot{m}_{oxydant}}{\dot{m}_{carburant}} $$

*   **O/F Stœchiométrique** : Combustion complète parfaite. Température MAXIMALE.
*   **O/F Optimal ($I_{sp}$ max)** : Généralement légèrement riche en carburant (Fuel Rich). Pourquoi ? Parce que l'hydrogène imbrûlé est léger, ce qui baisse la masse molaire moyenne ($M$) des gaz.

### 5.3 La Vitesse Caractéristique ($c^*$)
$c^*$ ("C-star") est la mesure de l'efficacité de la chambre de combustion, indépendamment de la tuyère.

$$ c^* = \frac{P_c \cdot A_t}{\dot{m}} = \frac{\sqrt{R \cdot T_c}}{\sqrt{\gamma} \cdot \Gamma} $$

*   $P_c$ : Pression chambre.
*   $A_t$ : Aire au col.
*   $T_c$ : Température de combustion.
*   $R$ : Constante des gaz spécifiques ($8314/M$).
*   **Objectif** : Maximiser $T_c$ et minimiser la masse molaire $M$. C'est pourquoi l'Hydrogène ($H_2$, $M=2$) est le roi.
## 6. TRANSFERT THERMIQUE : L'ÉQUATION DE BARTZ
────────────────────────────────────────────────────────────────────
Pour estimer le flux de chaleur qui attaque la paroi ($q$), il faut connaître le coefficient de convection côté gaz ($h_g$). C'est le cœur du problème thermique.

### 6.1 L'équation semi-empirique
Bartz (1957) a dérivé une corrélation pour les écoulements turbulents supersoniques à haute température :

$$ h_g = \frac{0.026}{D_t^{0.2}} \left( \frac{\mu^{0.2} C_p}{Pr^{0.6}} \right) \left( \frac{P_c}{c^*} \right)^{0.8} \left( \frac{A_t}{A} \right)^{0.9} \sigma $$

Cette formule nous dit trois choses capitales :
1.  **Effet d'échelle ($D_t^{-0.2}$)** : Plus le moteur est PETIT, plus le coefficient $h_g$ est GRAND. Les petits moteurs sont plus difficiles à refroidir que les gros !
2.  **Effet de pression ($P_c^{0.8}$)** : Si vous doublez la pression chambre, le flux thermique augmente de 74%.
3.  **Localisation** : Le flux est maximal au col ($A_t/A = 1$).

### 6.2 La Couche Limite ($\sigma$)
Le facteur $\sigma$ corrige les propriétés du gaz dans la couche limite (film de gaz stagnant contre la paroi). Si la paroi est froide, le gaz devient plus dense et visqueux près de la paroi, ce qui modifie le transfert.
## 7. DIMENSIONNEMENT DES CANAUX (SOLVEUR COOLANT)
────────────────────────────────────────────────────────────────────
Le refroidissement régénératif est un problème de résistances thermiques en série. L'énergie doit traverser trois barrières.

### 7.1 Le circuit thermique
$$ q = h_g (T_{aw} - T_{wh}) = \frac{k}{e} (T_{wh} - T_{wc}) = h_c (T_{wc} - T_{cool}) $$
*(Flux Convectif Gaz = Flux Conductif Paroi = Flux Convectif Coolant)*

*   $T_{wh}$ : Température paroi chaude (Hot).
*   $T_{wc}$ : Température paroi froide (Cold).
*   $k$ : Conductivité du matériau (W/mK).
*   $e$ : Épaisseur de la paroi.

### 7.2 Corrélations de Nusselt
Pour calculer l'efficacité du refroidissement ($h_c$), on utilise des nombres adimensionnels : Reynolds ($Re$) et Prandtl ($Pr$).

**Corrélation de Dittus-Boelter** (Simple, écoulement turbulent standard) :
$$ Nu = 0.023 \cdot Re^{0.8} \cdot Pr^{0.4} $$

**Corrélation de Gnielinski** (Plus précise, surtout pour $Re < 10^4$) :
$$ Nu = \frac{(f/8)(Re-1000)Pr}{1 + 12.7\sqrt{f/8}(Pr^{2/3}-1)} $$

Une fois $Nu$ connu, on trouve $h_c$ :
$$ h_c = \frac{Nu \cdot k_{fluide}}{D_h} $$

-> **Le secret** : Pour augmenter $h_c$, il faut augmenter la vitesse ($Re \uparrow$) ou réduire le diamètre hydraulique ($D_h \downarrow$). C'est pourquoi on utilise beaucoup de petits canaux (ex: 100 canaux de 1mm) plutôt que peu de gros canaux.
## 8. MÉCANIQUE DES FLUIDES : LE PRIX À PAYER
────────────────────────────────────────────────────────────────────
Refroidir coûte de la pression. Pousser un fluide à haute vitesse dans des canaux étroits génère des pertes de charge ($\Delta P$) considérables.

### 8.1 Équation de Darcy-Weisbach
La perte de pression est proportionnelle au carré de la vitesse :

$$ \Delta P = f \cdot \frac{L}{D_h} \cdot \frac{\rho v^2}{2} $$

*   $f$ : Facteur de friction (dépend de la rugosité).
*   $L$ : Longueur du canal.
*   $v$ : Vitesse du fluide.

### 8.2 Le compromis de design
C'est tout le dilemme de l'ingénieur propulsion :
*   **Vitesse élevée** $\Rightarrow$ Bon refroidissement ($h_c \uparrow$) MAIS Perte de charge énorme ($\Delta P \uparrow \uparrow$).
*   **Vitesse faible** $\Rightarrow$ Faible perte de charge MAIS Risque de fusion du moteur.

Si $\Delta P$ est trop grand, vos pompes ne pourront pas suivre, ou la pression dans la chemise sera inférieure à la pression dans la chambre, ce qui risque d'écraser la paroi interne (Buckling).

════════════════════════════════════════════════════════════════════
   PARTIE 3 : SCIENCE DES MATÉRIAUX
════════════════════════════════════════════════════════════════════

## 9. CRITÈRES DE SÉLECTION
────────────────────────────────────────────────────────────────────
Pour une chambre de combustion, on cherche le compromis impossible :
## 1. Conductivité Thermique (k) ÉLEVÉE : Pour évacuer la chaleur.
## 2. Température de Fusion ÉLEVÉE : Pour ne pas fondre.
## 3. Résistance Mécanique (σ_y) ÉLEVÉE : Pour tenir la pression.

## 10. BASE DE DONNÉES DÉTAILLÉE
────────────────────────────────────────────────────────────────────

🟢 LES CUIVRES (Le choix standard)
• Cuivre pur (Cu-OFHC) : Conductivité extrême (390 W/mK), mais très mou. Ne tient pas la pression à chaud.
• Cuivre-Chrome (CuCr) : Le compromis classique. Bonne conductivité (~320), résistance correcte.
• Cuivre-Zirconium (CuZr) : Similaire au CuCr, utilisé dans les applications haute température.
• GlidCop (Al-15) : Cuivre dopé à l'alumine. Reste dur même très proche de son point de fusion. Très utilisé par la NASA.
• CuCrNb (GRCop-42) : Le roi actuel (développé pour SpaceX/Raptor). Excellente tenue au fluage, imprimable en 3D.

⚪ LES SUPERALLIAGES (Pour les gros moteurs ou les tuyères)
• Inconel 718 / 625 : Alliages Nickel-Chrome. Tiennent très chaud (1200°C+) et très fort. MAIS conductivité pourrie (10-12 W/mK). Utilisés si le refroidissement est mauvais ou pour les extensions de tuyère.
• Monel 400 : Résiste exceptionnellement bien à l'oxygène pur (évite de brûler avec le moteur).

🔘 LES ALUMINIUMS (Pour les petits moteurs simples)
• AlSi10Mg : Aluminium de fonderie (Impression 3D). Conductivité correcte (110-130), très léger. Mais fond très vite (570°C). Demandent un refroidissement parfait.

🟣 LES RÉFRACTAIRES (L'exotisme)
• Niobium C-103 : Utilisé pour les extensions de tuyère radiatives (Apollo, Merlin Vacuum). Tient 2200°C mais s'oxyde instantanément à l'air (nécessite un revêtement siliciure).
• Tungstène : Tient 3400°C. Très lourd, cassant. Utilisé pour les cols non refroidis.

════════════════════════════════════════════════════════════════════
   PARTIE 4 : GUIDE DU LOGICIEL SITH MISCHUNG
════════════════════════════════════════════════════════════════════

## 11. GUIDE DE L'INTERFACE ET ANALYSE
────────────────────────────────────────────────────────────────────
Cette section vous guide à travers l'interface utilisateur et l'interprétation des résultats.

### 11.1 FLUX DE TRAVAIL (WORKFLOW)
Le logiciel est organisé en onglets suivant la logique de conception :

**A) ONGLET "DESIGN" (GÉOMÉTRIE)**
C'est le point de départ.
- **Paramètres de base** : Poussée cible, Pression de chambre, Ratio de mélange (O/F).
- **Géométrie de la chambre** : Diamètre, Longueur (L*), Rayon de contraction.
- **Géométrie de la tuyère** : Rapport de section (Area Ratio), Angles.
- **Contour** : Visualisation en temps réel du profil 2D.
NOTE: *Astuce* : Le L* est crucial pour la stabilité (typ. 0.8-1.2m).

**B) ONGLET "COOLING" (THERMIQUE)**
Le cœur de l'analyse régénérative.
- **Canaux** : Nombre, largeur, hauteur.
- **Matériaux** : Liner (interne) et Jacket (externe).
- **Type** : Co-courant ou Contre-courant.

**C) ONGLET "INJECTOR"**
- **Éléments** : Coaxial, Doublet, Triplet.
- **Stabilité** : Vérification du ΔP (viser 15-20% de Pc).

### 11.2 ANALYSE DES RÉSULTATS
Une fois les paramètres définis, le logiciel calcule les performances.

**GRAPHIQUES PRINCIPAUX :**
- **Température** : Profils de T_gaz, T_paroi, T_coolant.
  **ATTENTION:** *Surveillez T_paroi_chaude < T_fusion !*
- **Pression** : Évolution statique et totale.
- **Mach** : Accélération des gaz.
- **Flux Thermique** : Visualisez le pic au col.

**INDICATEURS CLÉS :**
- **Isp** : Efficacité globale.
- **C*** : Efficacité combustion.
- **Cf** : Efficacité tuyère.

## 12. OUTILS AVANCÉS ET PRODUCTION
────────────────────────────────────────────────────────────────────
Fonctionnalités pour l'optimisation automatique et la fabrication.

### 12.1 UTILISATION DE L'OPTIMISEUR
L'onglet "Optimiseur" utilise l'algorithme "Differential Evolution" (Scipy).

**CONFIGURATION :**
1. **Variables** : Cochez les paramètres modifiables (ex: Épaisseur paroi).
2. **Contraintes** : Cochez les limites (ex: T_paroi_max).
3. **Objectif** : Min Masse, Max Marge, ou Min Delta P.

**INTERPRÉTATION :**
L'algorithme lance des centaines de simulations. Vérifiez toujours manuellement la solution proposée !

### 12.2 EXPORT CAD & FABRICATION
Générez des fichiers pour la CAO et la simulation externe.

**FORMATS D'EXPORT :**
- **STEP (.stp)** : Solide 3D complet (CFD, Thermique, Intégration).
- **DXF (.dxf)** : Profil 2D (Esquisse/Sketch pour Révolution).
- **STL (.stl)** : Maillage (Impression 3D rapide, Rendu).
- **CSV (.csv)** : Données brutes (Excel, Matlab).

**NOTES FABRICATION (IMPRESSION 3D) :**
- Les canaux sont rectangulaires par défaut.
- Évitez les angles vifs internes.
- Attention aux porte-à-faux (overhangs) > 45°.
- Prévoyez des surépaisseurs pour l'usinage des surfaces fonctionnelles.

════════════════════════════════════════════════════════════════════
   PARTIE 5 : DOCUMENTATION TECHNIQUE APPROFONDIE
════════════════════════════════════════════════════════════════════
"May the Thrust be with you."

 ANALYSE THERMIQUE DES MOTEURS-FUSÉES - GUIDE COMPLET
═══════════════════════════════════════════════════════════════

Ce guide exhaustif couvre tous les aspects du refroidissement
régénératif des moteurs-fusées à propergols liquides.


## 13. INTRODUCTION ET CONCEPTS FONDAMENTAUX
═══════════════════════════════════════════════════════════════

### 13.1 POURQUOI LE REFROIDISSEMENT EST-IL CRITIQUE ?
───────────────────────────────────────────────────────────────

Un moteur-fusée à propergols liquides génère des températures
extrêmement élevées lors de la combustion:

  • Couple LOX/RP-1:    T_c ≈ 3500-3600 K
  • Couple LOX/LH2:     T_c ≈ 3200-3400 K
  • Couple LOX/CH4:     T_c ≈ 3500-3600 K
  • Couple N2O4/UDMH:   T_c ≈ 3200-3400 K
  • Couple H2O2/RP-1:   T_c ≈ 2800-3000 K

**ATTENTION:**  PROBLÈME CRITIQUE:
Ces températures dépassent largement le point de fusion de TOUS
les métaux et alliages connus:

  • Cuivre fond à:      1358 K (1085°C)
  • Inconel fond à:     1609 K (1336°C)
  • Tungstène fond à:   3695 K (3422°C)

Sans refroidissement, la paroi de la chambre fondrait en
quelques MILLISECONDES à quelques SECONDES selon:
  - Le flux thermique local
  - L'épaisseur de la paroi
  - La conductivité thermique du matériau
  - La capacité thermique massique

EXEMPLE NUMÉRIQUE - Temps avant fusion sans refroidissement:
  Données: CuCr, e=3mm, ρ=8900 kg/m³, Cp=385 J/kg·K
  Flux entrant: q = 30 MW/m² (typique au col)

  Énergie pour chauffer 1m² de ΔT = 1000K:
  E = ρ × e × Cp × ΔT = 8900 × 0.003 × 385 × 1000 = 10.3 MJ

  Temps: t = E/q = 10.3×10⁶ / 30×10⁶ = 0.34 seconde!

**DANGER:** En moins d'une demi-seconde, la paroi atteint sa température
   de fusion sans refroidissement actif!


### 13.2 LES DIFFÉRENTES STRATÉGIES DE REFROIDISSEMENT
───────────────────────────────────────────────────────────────

Il existe plusieurs méthodes pour gérer la charge thermique:

A) REFROIDISSEMENT RÉGÉNÉRATIF (traité dans ce guide)
   Le propergol (fuel ou oxydant) circule dans des canaux
   autour de la chambre AVANT d'être injecté et brûlé.

   Avantages:
   *   Récupère l'énergie thermique (améliore Isp)
   *   Pas de perte de masse propulsive
   *   Permet fonctionnement continu longue durée
   *   Contrôle précis des températures

   Inconvénients:
   *   Complexité de fabrication (canaux, soudures)
   *   Risque de cokéfaction avec hydrocarbures
   *   Pertes de charge hydrauliques
   *   Coût élevé de fabrication

B) REFROIDISSEMENT PAR FILM (Film Cooling)
   Une couche de propergol liquide ou gazeux est injectée
   le long de la paroi, créant une barrière protectrice.

   Avantages:
   *   Simple à implémenter
   *   Réduit le flux thermique effectif

   Inconvénients:
   *   Perte d'Isp (propergol non brûlé de façon optimale)
   *   Peut perturber la combustion
   *   Efficacité limitée dans le temps

C) REFROIDISSEMENT ABLATIF
   La paroi est faite d'un matériau qui s'érode progressivement,
   absorbant l'énergie par changement de phase.

   Avantages:
   *   Très simple (pas de circulation)
   *   Léger pour moteurs à courte durée
   *   Fiable (pas de pompes, pas de canaux)

   Inconvénients:
   *   Durée limitée
   *   Changement de géométrie pendant le tir
   *   Débris dans l'écoulement

D) REFROIDISSEMENT RADIATIF
   La paroi rayonne sa chaleur vers l'espace.
   Utilisé principalement pour les tuyères de moteurs
   spatiaux à faible poussée.

   Avantages:
   *   Très simple, léger
   *   Pas de fluide de refroidissement

   Inconvénients:
   *   Limité aux faibles flux (< 5 MW/m²)
   *   Nécessite matériaux réfractaires (Nb, Mo, W)

E) TRANSPIRATION (Sweat Cooling)
   Le coolant suinte à travers un matériau poreux.

   Avantages:
   *   Très efficace thermiquement

   Inconvénients:
   *   Risque de bouchage des pores
   *   Difficulté de fabrication
   *   Rarement utilisé en pratique


### 13.3 SCHÉMA DU TRANSFERT THERMIQUE
───────────────────────────────────────────────────────────────

Vue en coupe de la paroi d'un moteur à refroidissement régénératif:

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

PRINCIPE DE CONSERVATION:
En régime permanent (steady-state), le flux est CONSTANT
à travers toutes les couches:

  q₁ = q₂ = q₃ = q

  q = h_g×(T_gaz - T_wh) = (k/e)×(T_wh - T_wc) = h_c×(T_wc - T_cool)


### 13.4 ÉQUATIONS FONDAMENTALES DU TRANSFERT
───────────────────────────────────────────────────────────────

La résolution du problème thermique repose sur l'ANALOGIE
ÉLECTRIQUE: le flux de chaleur est analogue au courant,
la différence de température à la tension.

RÉSISTANCES THERMIQUES EN SÉRIE:

  ┌─────────┐    ┌─────────┐    ┌─────────┐
  │  R_gaz  │────│ R_paroi │────│ R_cool  │
  │  1/h_g  │    │   e/k   │    │  1/h_c  │
  └─────────┘    └─────────┘    └─────────┘
       ↑              ↑              ↑
    T_gaz          T_wall         T_cool

Résistance totale:
  R_total = R_gaz + R_paroi + R_cool
  R_total = 1/h_g + e/k + 1/h_c   [m²·K/W]

Flux thermique:
  q = ΔT_total / R_total
  q = (T_gaz - T_coolant) / (1/h_g + e/k + 1/h_c)   [W/m²]

REMARQUE IMPORTANTE:
Cette formule suppose des coefficients h constants et une
paroi plane. En réalité:
  - h_g varie avec la position (maximum au col)
  - La géométrie est cylindrique/conique
  - T_coolant augmente le long du canal
  - Les propriétés varient avec T


### 13.5 ORDRES DE GRANDEUR TYPIQUES
───────────────────────────────────────────────────────────────

Pour un moteur LOX/RP-1 de 100 kN:

**PARAMÈTRES DE CONCEPTION:**

| Paramètre | Valeur typique |
| :--- | :--- |
| Pression chambre | 30-100 bar |
| Température chambre | 3400-3600 K |
| Diamètre col | 50-150 mm |
| Diamètre chambre | 100-300 mm |
| Rapport de section | 15-40 (selon altitude) |
| Épaisseur paroi | 1-5 mm |
| Nombre de canaux | 50-200 |

**FLUX THERMIQUES:**

| Zone | Flux q (MW/m²) |
| :--- | :--- |
| Injecteur | 5 - 15 |
| Chambre cylindrique | 5 - 15 |
| Convergent | 10 - 30 |
| Col (MAXIMUM!) | 20 - 80 |
| Divergent (début) | 10 - 30 |
| Divergent (sortie) | 1 - 5 |

**COEFFICIENTS DE TRANSFERT:**

| Coefficient | Valeur (W/m²·K) |
| :--- | :--- |
| h_g (chambre) | 2,000 - 10,000 |
| h_g (col) | 10,000 - 50,000 |
| h_c (RP-1) | 5,000 - 30,000 |
| h_c (LH2) | 20,000 - 150,000 |
| h_c (CH4) | 10,000 - 50,000 |

**TEMPÉRATURES DE PAROI:**

| Surface | Température (K) |
| :--- | :--- |
| T_wall_hot (typique) | 600 - 1000 |
| T_wall_hot (max admis) | 800 - 1200 selon matériau |
| T_wall_cold | 400 - 800 |
| T_coolant entrée | 150 - 300 |
| T_coolant sortie | 300 - 500 |


## 14. THÉORIE DÉTAILLÉE DU TRANSFERT THERMIQUE
═══════════════════════════════════════════════════════════════

Cette section développe les fondements physiques et
mathématiques du transfert de chaleur dans les moteurs-fusées.


### 14.1 LA CONDUCTION THERMIQUE
───────────────────────────────────────────────────────────────

2.1.1 Loi de Fourier

La conduction est le transfert d'énergie thermique par
agitation moléculaire et interaction électronique dans
un milieu solide (ou fluide immobile).

ÉQUATION DE FOURIER (forme différentielle):

  q⃗ = -k × ∇T

Où:
  q⃗  = vecteur flux thermique [W/m²]
  k  = conductivité thermique [W/(m·K)]
  ∇T = gradient de température [K/m]

Le signe négatif indique que le flux va des zones chaudes
vers les zones froides.

Pour une paroi plane 1D:

  q = -k × dT/dx = k × (T_hot - T_cold) / e

  q = k × ΔT / e   [W/m²]

RÉSISTANCE THERMIQUE DE CONDUCTION:

  R_cond = e / k   [m²·K/W]

  ΔT = q × R_cond

Plus k est élevé, plus la résistance est faible, plus le
transfert est efficace.

2.1.2 Conductivité des matériaux pour moteurs-fusées

La conductivité k varie selon:
  - La composition du matériau
  - La température (généralement ↓ quand T ↑ pour métaux)
  - L'état cristallin
  - Les impuretés

**TABLEAU DES CONDUCTIVITÉS DÉTAILLÉ:**

| Matériau | k (W/m·K) @ 300K | @ 500K | @ 800K | @ 1000K |
| :--- | :---: | :---: | :---: | :---: |
| **Cuivre pur** | 401 | 386 | 357 | 337 |
| **CuCr (C18200)** | 324 | 315 | 298 | 285 |
| **CuCrZr** | 315 | 305 | 288 | 275 |
| **GRCop-84** | 298 | 285 | 265 | 250 |
| **Inconel 718** | 11.4 | 14.7 | 19.2 | 22.1 |
| **Inconel 625** | 9.8 | 12.8 | 17.3 | 20.5 |
| **Inox 316L** | 16.3 | 18.9 | 22.5 | 25.2 |
| **Inox 304** | 16.2 | 18.6 | 22.0 | 24.5 |
| **Niobium** | 53.7 | 55.1 | 59.3 | 62.0 |
| **C103** | 44.2 | 46.5 | 51.2 | 54.5 |
| **Molybdène** | 138 | 126 | 112 | 105 |
| **TZM** | 120 | 115 | 105 | 98 |
| **Tungstène** | 173 | 156 | 132 | 118 |
| **Rhénium** | 47.9 | 44.5 | 40.2 | 38.0 |
| **Tantale** | 57.5 | 56.0 | 57.5 | 59.0 |
| **AlSi10Mg** | 130 | 138 | (fond) | (fond) |
| **Ti-6Al-4V** | 6.7 | 8.5 | 12.0 | 15.0 |
| **Graphite** | 120 | 100 | 80 | 70 |
| **C/C** | 50-150 | 70-120 | 80-100 | 85-95 |

REMARQUES SUR LES ALLIAGES DE CUIVRE:

• CuCr (C18200 / "Chromium Copper"):
  - Contient ~1% Cr
  - Bonne conductivité + résistance mécanique
  - T_max service ≈ 1050 K (ramollissement)
  - Très utilisé: Merlin (SpaceX), RS-25 (NASA)

• CuCrZr (C18150):
  - Contient ~0.8% Cr + 0.08% Zr
  - Meilleure tenue à chaud que CuCr
  - T_max service ≈ 1100 K
  - Utilisé: RD-170 (Energomash)

• GRCop-84 (NASA Glenn):
  - Cu + 8% Cr + 4% Nb (nano-particules)
  - Développé spécifiquement pour moteurs-fusées
  - Excellente résistance au fluage à haute T
  - T_max service ≈ 1200 K
  - Utilisé: SLS RS-25 upgrades, Relativity Terran

2.1.3 Géométrie cylindrique

Pour une paroi cylindrique (chambre, tuyère):

  q_radial = (2π × k × L × ΔT) / ln(r_ext/r_int)

  Résistance: R_cyl = ln(r_ext/r_int) / (2π × k × L)

Pour des parois minces (e << r_moy), on peut approximer:
  R_cyl ≈ e / (k × A_moy)  où A_moy = 2π × r_moy × L


### 14.2 LA CONVECTION THERMIQUE
───────────────────────────────────────────────────────────────

14.2.1 Loi de Newton du refroidissement

La convection est le transfert d'énergie entre une surface
solide et un fluide en mouvement.

ÉQUATION DE NEWTON:

  q = h × (T_surface - T_fluide)   [W/m²]

Où:
  h  = coefficient de transfert convectif [W/(m²·K)]
  T_surface = température de la paroi [K]
  T_fluide = température du fluide [K]

Le coefficient h dépend de nombreux facteurs:
  - Type d'écoulement (laminaire, turbulent)
  - Vitesse du fluide
  - Propriétés thermophysiques (ρ, μ, Cp, k_fluide)
  - Géométrie du canal
  - Rugosité de surface
  - Effets d'entrée

RÉSISTANCE THERMIQUE DE CONVECTION:

  R_conv = 1 / h   [m²·K/W]

2.2.2 Types de convection

CONVECTION NATURELLE:
  Le mouvement du fluide est dû à la différence de densité
  causée par le gradient de température.
  h ≈ 5-25 W/m²·K (air)
  → Non pertinent pour les moteurs-fusées!

CONVECTION FORCÉE:
  Le mouvement du fluide est imposé par une pompe/turbine.
  h ≈ 50 - 200,000 W/m²·K selon le fluide et les conditions.
  → C'est le cas dans les moteurs-fusées.

ÉBULLITION:
  Changement de phase liquide → vapeur.
  h peut atteindre 100,000+ W/m²·K
  **ATTENTION:** Éviter l'ébullition non contrôlée (DNB = crise d'ébullition)

2.2.3 Couche limite thermique

Près de la paroi, il existe une "couche limite thermique" où
la température varie de T_surface à T_fluide.

CÔTÉ GAZ CHAUD:
  - Épaisseur couche limite: δ_th ≈ 0.1-1 mm
  - C'est là que se concentre la résistance thermique
  - La turbulence améliore le mélange → h_g plus élevé

CÔTÉ COOLANT:
  - Épaisseur couche limite: δ_th ≈ 0.01-0.5 mm
  - Canaux étroits → meilleur transfert
  - Turbulence très importante pour h_c élevé

LIEN AVEC h:
  h ≈ k_fluide / δ_th

Plus la couche limite est mince, plus h est élevé.


### 14.3 LES NOMBRES ADIMENSIONNELS
───────────────────────────────────────────────────────────────

Les corrélations de transfert thermique utilisent des
groupements adimensionnels permettant de généraliser les
résultats expérimentaux.

14.3.1 Nombre de Reynolds (Re)

DÉFINITION:
  Re = ρ × v × D_h / μ = v × D_h / ν

Où:
  ρ   = masse volumique [kg/m³]
  v   = vitesse moyenne [m/s]
  D_h = diamètre hydraulique [m]
  μ   = viscosité dynamique [Pa·s]
  ν   = viscosité cinématique [m²/s] = μ/ρ

SIGNIFICATION PHYSIQUE:
  Re = Forces d'inertie / Forces visqueuses

**RÉGIMES D'ÉCOULEMENT:**

| Re | Régime | Description |
| :--- | :--- | :--- |
| **Re < 2,300** | LAMINAIRE | Écoulement ordonné. Profil parabolique. Transfert faible. |
| **2,300 < Re < 10,000** | TRANSITOIRE | Intermittent. Imprévisible. À éviter. |
| **Re > 10,000** | TURBULENT | Mélange chaotique. Profil aplati. Excellent transfert. |

**DIAMÈTRE HYDRAULIQUE:**
Pour un canal non-circulaire:
$$ D_h = \frac{4 \cdot A}{P} $$

Où:
*   $A$ = aire de la section [m²]
*   $P$ = périmètre mouillé [m]

Exemples:
*   Canal rectangulaire ($w \times h$): $D_h = \frac{2wh}{w+h}$
*   Canal carré ($a \times a$): $D_h = a$
*   Anneau ($R_{ext}, R_{int}$): $D_h = 2(R_{ext} - R_{int})$

**VALEURS TYPIQUES DANS LES MOTEURS:**

| Fluide/Zone | Re typique |
| :--- | :--- |
| Gaz chambre | $10^5 - 10^7$ (hautement turbulent) |
| RP-1 dans canaux | $10^4 - 10^5$ |
| LH2 dans canaux | $10^5 - 10^6$ |
| CH4 dans canaux | $10^4 - 10^5$ |
| LOX dans canaux | $10^4 - 10^5$ |

### 14.3.2 Nombre de Prandtl (Pr)

**DÉFINITION:**
$$ Pr = \frac{\mu \cdot C_p}{k} = \frac{\nu}{\alpha} $$

Où:
*   $\mu$  = viscosité dynamique [Pa·s]
*   $C_p$ = capacité thermique massique [J/(kg·K)]
*   $k$  = conductivité thermique [W/(m·K)]
*   $\nu$  = viscosité cinématique [m²/s]
*   $\alpha$  = diffusivité thermique [m²/s]

**SIGNIFICATION PHYSIQUE:**
Pr = Diffusivité de quantité de mouvement / Diffusivité thermique
Pr = Épaisseur couche limite dynamique / Épaisseur couche limite thermique

**INTERPRÉTATION:**

| Pr | Signification | Exemples |
| :--- | :--- | :--- |
| **Pr << 1** (0.001-0.03) | MÉTAUX LIQUIDES | Na, K, Hg, Li |
| **Pr ≈ 0.7-1.0** | GAZ | Air, N2, O2, Gaz combustion |
| **Pr > 1** (1-1000) | LIQUIDES | H2O (6), RP-1 (20-50) |

**VALEURS TYPIQUES:**

| Fluide | Pr (approx) |
| :--- | :--- |
| Gaz de combustion | 0.7 - 0.9 |
| Hydrogène liquide | 0.7 - 1.5 |
| Méthane liquide | 2 - 5 |
| LOX | 2 - 4 |
| RP-1 / Kérosène | 10 - 100 |
| Éthanol | 10 - 50 |
| Eau | 1 - 10 |

2.3.3 Nombre de Nusselt (Nu)

DÉFINITION:
  Nu = h × D_h / k_fluide

Où:
  h        = coefficient de convection [W/(m²·K)]
  D_h      = diamètre hydraulique [m]
  k_fluide = conductivité du fluide [W/(m·K)]

SIGNIFICATION PHYSIQUE:
  Nu = Transfert convectif réel / Transfert conductif pur

  Nu = 1 signifie que la convection n'améliore pas le
       transfert par rapport à la conduction seule.
  Nu >> 1 signifie une amélioration significative.

UTILISATION:
Une fois Nu calculé via une corrélation, on obtient h:

  h = Nu × k_fluide / D_h

VALEURS TYPIQUES:
  - Écoulement laminaire: Nu ≈ 3.66-4.36
  - Écoulement turbulent: Nu ≈ 100-1000
  - Ébullition: Nu >> 1000

2.3.4 Autres nombres utiles

NOMBRE DE STANTON (St):
  St = h / (ρ × v × Cp) = Nu / (Re × Pr)

  Utilisé dans les analyses de couche limite.
  Représente le transfert thermique adimensionnel.

NOMBRE DE BIOT (Bi):
  Bi = h × L_c / k_solide

  Où L_c = caractéristique longueur du solide (e.g., épaisseur)

  Si Bi << 0.1: Température uniforme dans le solide
  Si Bi >> 0.1: Gradient de température significatif

NOMBRE DE FOURIER (Fo):
  Fo = α × t / L²

  Temps adimensionnel pour les problèmes transitoires.
  α = diffusivité thermique du solide.

NOMBRE DE MACH (Ma):
  Ma = v / a  (a = vitesse du son)

  Important côté gaz: effets de compressibilité.


## 15. MODÈLE DE BARTZ POUR h_g
═══════════════════════════════════════════════════════════════

L'équation de Bartz est la corrélation de référence pour
calculer le coefficient de transfert convectif côté gaz
chaud dans les moteurs-fusées.


### 15.1 HISTORIQUE ET DÉVELOPPEMENT
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


### 15.2 ÉQUATION COMPLÈTE DE BARTZ
───────────────────────────────────────────────────────────────

FORME GÉNÉRALE:

### 0.026      ⎛  μ^0.2 × Cp  ⎞   ⎛ p_c ⎞^0.8
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


### 15.3 FORMULE SIMPLIFIÉE (utilisée dans le code)
───────────────────────────────────────────────────────────────

Pour simplifier l'implémentation, on utilise:

ÉTAPE 1 - Calcul de h_g au col (référence):

### 0.026      ⎛  μ^0.2 × Cp  ⎞   ⎛ P_c ⎞^0.8
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


### 15.4 PROPRIÉTÉS DES GAZ DE COMBUSTION
───────────────────────────────────────────────────────────────

Les propriétés thermo-physiques des gaz de combustion sont
calculées à une température de film:

  T_film = (T_wall_hot + T_adiabatique) / 2

**PROPRIÉTÉS TYPIQUES (LOX/RP-1, T ≈ 2500 K):**

| Propriété | Valeur approximative |
| :--- | :--- |
| $\mu$ (viscosité) | $7-9 \times 10^{-5}$ Pa·s |
| $C_p$ | 2000-2500 J/(kg·K) |
| $k_{gaz}$ | 0.15-0.25 W/(m·K) |
| $Pr$ | 0.75-0.85 |
| $\gamma$ (gamma) | 1.15-1.25 |
| $M$ (masse molaire) | 22-28 kg/kmol |

**VARIATION AVEC LE MÉLANGE O/F:**

| O/F (LOX/RP-1) | 2.0 | 2.6 | 3.2 |
| :--- | :---: | :---: | :---: |
| T_chambre (K) | 3350 | 3600 | 3500 |
| M (kg/kmol) | 21.5 | 24.0 | 27.5 |
| $\gamma$ | 1.22 | 1.18 | 1.15 |
| c* (m/s) | 1680 | 1750 | 1700 |

**EFFET SUR h_g:**
*   O/F élevé: T_c plus élevé, mais M plus élevé
*   h_g varie peu avec O/F (effets compensatoires)


### 15.5 VALEURS TYPIQUES DE h_g
───────────────────────────────────────────────────────────────

| Zone | h_g (W/m²·K) | Commentaires |
| :--- | :--- | :--- |
| Injecteur | 3,000 - 10,000 | Dépend du design |
| Chambre (cyl.) | 2,000 - 8,000 | Écoulement subsonique |
| Convergent | 5,000 - 20,000 | Accélération du gaz |
| Col (throat) | 10,000 - 50,000 | MAXIMUM! Ma = 1 |
| Divergent début | 8,000 - 25,000 | Expansion commence |
| Divergent mi | 3,000 - 10,000 | Refroidissement gaz |
| Divergent sortie | 500 - 3,000 | Gaz très dilatés |

**FACTEURS INFLUENÇANT h_g:**

| Facteur | Effet sur h_g |
| :--- | :--- |
| Pression chambre $\uparrow$ | $h_g \uparrow$ ($\propto P^{0.8}$) |
| Diamètre col $\downarrow$ | $h_g \uparrow$ ($\propto D^{-0.2}$) |
| Position $\rightarrow$ col | $h_g \uparrow$ (max au col) |
| Position $\rightarrow$ sortie | $h_g \downarrow$ (min à sortie) |
| T_chambre $\uparrow$ | $h_g \downarrow$ légèrement |
| T_paroi $\downarrow$ | $h_g \uparrow$ légèrement |


### 15.6 LIMITATIONS DU MODÈLE DE BARTZ
───────────────────────────────────────────────────────────────

Le modèle de Bartz a des limitations importantes:

**NE PREND PAS EN COMPTE:**
  - Rayonnement thermique (important si T > 3000 K)
  - Dissociation/recombinaison des gaz
  - Effets de couche limite réactive
  - Turbulence de combustion
  - Effets 3D près de l'injecteur
  - Rugosité de surface
  - Dépôts de suie (cokéfaction)

**ATTENTION:** PRÉCISION:
  - Généralement ±20-30% pour h_g
  - Peut être pire dans des conditions extrêmes
  - Sous-estime parfois h_g au col

**RECOMMANDATIONS:**
  - Utiliser des marges de sécurité (facteur 1.2-1.5)
  - Valider par essais si possible
  - Utiliser CFD pour conception détaillée
  - Comparer avec d'autres corrélations (Rao, Cinjarew)


### 15.7 COMPARAISON AVEC AUTRES CORRÉLATIONS
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


## 16. CALCUL DES TEMPÉRATURES DE PAROI
═══════════════════════════════════════════════════════════════

Le calcul précis des températures de paroi est l'objectif
principal de l'analyse thermique. C'est ce qui détermine
si le moteur survivra ou non.


### 16.1 SYSTÈME D'ÉQUATIONS THERMIQUES
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


### 16.2 CALCUL DE T_WALL_HOT (température critique)
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

**INFLUENCE DES PARAMÈTRES SUR T_wall_hot:**

| Si on augmente... | Effet sur T_wall_hot |
| :--- | :--- |
| h_g $\uparrow$ | T_wall_hot $\uparrow$ (plus de flux entrant) |
| h_c $\uparrow$ | T_wall_hot $\downarrow$ (meilleure évacuation) |
| k $\uparrow$ | T_wall_hot $\downarrow$ (gradient réduit) |
| e $\uparrow$ | T_wall_hot $\uparrow$ (résistance accrue) |
| T_gaz $\uparrow$ | T_wall_hot $\uparrow$ (source plus chaude) |
| T_coolant $\downarrow$ | T_wall_hot $\downarrow$ (puits plus froid) |


### 16.3 CALCUL DE T_WALL_COLD
───────────────────────────────────────────────────────────────

**MÉTHODE 1 - À partir du flux:**
$$ T_{wall\_cold} = T_{coolant} + \frac{q}{h_c} $$

**MÉTHODE 2 - À partir de T_wall_hot:**
$$ T_{wall\_cold} = T_{wall\_hot} - \frac{q \cdot e}{k} $$

**IMPORTANCE DE T_WALL_COLD:**
*   Détermine le $\Delta T$ dans la paroi
*   Influence le stress thermique (dilatation différentielle)
*   Affecte les propriétés du coolant (ébullition possible?)

**ATTENTION:** **ATTENTION À L'ÉBULLITION:**
Si $T_{wall\_cold} > T_{ébullition}$ du coolant (à la pression locale):
*   → Formation de bulles
*   → Risque de DNB (Departure from Nucleate Boiling)
*   → Chute drastique de $h_c$ → SURCHAUFFE → DESTRUCTION

**TEMPÉRATURES D'ÉBULLITION (à pression atmosphérique):**

| Coolant | T_boil @ 1 bar (K) |
| :--- | :--- |
| LH2 | 20.3 K |
| LOX | 90.2 K |
| LN2 | 77.4 K |
| CH4 | 111.7 K |
| C2H6 | 184.6 K |
| NH3 | 239.8 K |
| C2H5OH | 351.4 K |
| H2O | 373.2 K |
| N2H4 | 387.0 K |
| RP-1 | 490-540 K (plage) |

À haute pression, T_boil augmente (selon courbe de saturation).


### 16.4 PROFIL DE TEMPÉRATURE DANS LA PAROI
───────────────────────────────────────────────────────────────

En régime permanent avec flux constant, le profil est LINÉAIRE:

$$ T(x) = T_{wall\_hot} - \frac{q}{k} \cdot x $$

Où:
*   $x$ = distance depuis la surface chaude ($0 \leq x \leq e$)
*   $T(0) = T_{wall\_hot}$
*   $T(e) = T_{wall\_cold}$

**GRADIENT DE TEMPÉRATURE:**
$$ \frac{dT}{dx} = -\frac{q}{k} \quad [K/m] $$

Exemple numérique:
$q = 20 MW/m^2$, $k = 320 W/m·K$ (CuCr)
$dT/dx = -20 \times 10^6 / 320 = -62,500 K/m = -62.5 K/mm$

Pour une épaisseur $e = 2 mm$:
$\Delta T = 62.5 \times 2 = 125 K$


### 16.5 CONTRAINTES THERMIQUES (STRESS THERMIQUE)
───────────────────────────────────────────────────────────────

Le gradient de température crée des contraintes mécaniques dues à la dilatation différentielle.

**CONTRAINTE THERMIQUE MAXIMALE:**

$$ \sigma_{th} = \frac{E \cdot \alpha \cdot \Delta T}{2 \cdot (1 - \nu)} $$

Où:
*   $E$ = module de Young [Pa]
*   $\alpha$ = coefficient de dilatation thermique [1/K]
*   $\Delta T = T_{wall\_hot} - T_{wall\_cold}$ [K]
*   $\nu$ = coefficient de Poisson [-]

**PROPRIÉTÉS THERMOMÉCANIQUES:**

| Matériau | E (GPa) | $\alpha$ ($10^{-6}/K$) | $\nu$ |
| :--- | :--- | :--- | :--- |
| Cuivre | 117 | 17.0 | 0.34 |
| CuCr | 130 | 16.5 | 0.34 |
| Inconel 718 | 200 | 13.0 | 0.29 |
| Inox 316L | 193 | 16.0 | 0.27 |
| Niobium | 105 | 7.3 | 0.40 |
| Molybdène | 329 | 5.0 | 0.31 |
| Tungstène | 411 | 4.5 | 0.28 |

**EXEMPLE DE CALCUL:**
CuCr, $\Delta T = 150 K$, $E = 130 GPa$, $\alpha = 16.5 \times 10^{-6}/K$, $\nu = 0.34$

$\sigma_{th} = 130 \times 10^9 \times 16.5 \times 10^{-6} \times 150 / (2 \times (1-0.34))$
$\sigma_{th} = 244 MPa$

Cette contrainte s'ajoute aux contraintes de pression!


### 16.6 RÉGIME TRANSITOIRE (DÉMARRAGE/ARRÊT)
───────────────────────────────────────────────────────────────

Pendant les phases de démarrage et d'arrêt, le régime n'est pas permanent. Les équations deviennent:

**ÉQUATION DE LA CHALEUR (1D):**

$$ \frac{\partial T}{\partial t} = \frac{k}{\rho \cdot C_p} \cdot \frac{\partial^2 T}{\partial x^2} = \alpha \cdot \frac{\partial^2 T}{\partial x^2} $$

Où $\alpha = k/(\rho \cdot C_p)$ est la diffusivité thermique [m²/s].

**TEMPS CARACTÉRISTIQUE:**
$$ \tau = \frac{e^2}{\alpha} $$

C'est le temps pour atteindre ~63% du régime permanent.

**VALEURS TYPIQUES DE $\tau$:**

| Matériau | $\alpha$ (mm²/s) | $\tau$ pour e=2mm (s) |
| :--- | :--- | :--- |
| Cuivre | 117 | 0.034 |
| CuCr | 104 | 0.038 |
| Inconel 718 | 3.1 | 1.3 |
| Inox 316L | 4.0 | 1.0 |
| Niobium | 24.3 | 0.16 |
| Molybdène | 53.7 | 0.074 |
| Tungstène | 68.3 | 0.058 |

IMPLICATIONS:
  - Cuivre: réponse très rapide (~35 ms)
  - Superalliages: réponse lente (~1 s)
  - Pendant le transitoire, T_wall_hot peut DÉPASSER la valeur
    en régime permanent (overshoot)!

**ATTENTION:** RISQUE AU DÉMARRAGE:
Le coolant peut ne pas être à plein débit quand les gaz
chauds arrivent → surchauffe critique possible!


### 16.7 TEMPÉRATURE ADIABATIQUE DE PAROI
───────────────────────────────────────────────────────────────

En réalité, on n'utilise pas directement T_chambre mais la
température adiabatique de paroi T_aw.

DÉFINITION:
T_aw est la température qu'atteindrait une paroi parfaitement
isolée (adiabatique) exposée à l'écoulement.

CALCUL:
                          γ - 1
  T_aw = T_statique × (1 + r × ───── × M²)
                            2

Où:
  r = facteur de récupération ≈ Pr^(1/3) pour turbulent
  γ = rapport des chaleurs spécifiques
  M = nombre de Mach local

VALEURS DE r:
  - Écoulement laminaire:  r ≈ Pr^(1/2) ≈ 0.85
  - Écoulement turbulent:  r ≈ Pr^(1/3) ≈ 0.89

EFFET:
  T_aw < T_stagnation (à cause des frottements visqueux)

Typiquement: T_aw ≈ 0.9 × T_stagnation au col


### 16.8 CALCUL ITÉRATIF COMPLET
───────────────────────────────────────────────────────────────

En pratique, le calcul est itératif car h_g et h_c dépendent
des températures (via les propriétés des fluides).

ALGORITHME:
  1. Estimer T_wall_hot_init (e.g., 800 K)
  2. Calculer T_film_gaz = (T_aw + T_wall_hot)/2
  3. Calculer propriétés gaz à T_film_gaz
  4. Calculer h_g (Bartz)
  5. Estimer T_wall_cold
  6. Calculer T_film_cool = (T_wall_cold + T_cool)/2
  7. Calculer propriétés coolant à T_film_cool
  8. Calculer h_c (Dittus-Boelter ou Gnielinski)
  9. Calculer q = (T_aw - T_cool) / (1/h_g + e/k + 1/h_c)
  10. Calculer nouvelles T_wall_hot et T_wall_cold
  11. Si |T_new - T_old| > tolérance: retour à 2
  12. Sinon: CONVERGÉ!

CRITÈRE DE CONVERGENCE:
  |T_wall_hot_new - T_wall_hot_old| < 1 K

Typiquement convergence en 3-5 itérations.


## 17. CORRÉLATIONS CÔTÉ COOLANT - ANALYSE DÉTAILLÉE
═══════════════════════════════════════════════════════════════

Le calcul précis de h_c est crucial pour une conception fiable.
Cette section détaille les principales corrélations utilisées.


### 17.1 CORRÉLATION DE DITTUS-BOELTER
───────────────────────────────────────────────────────────────

C'est la corrélation la plus utilisée pour l'écoulement
turbulent en convection forcée dans des tubes.

HISTORIQUE:
  Publiée en 1930 par F.W. Dittus et L.M.K. Boelter.
  Basée sur des expériences avec de l'eau et de l'huile.

ÉQUATION:
  Nu = 0.023 × Re^0.8 × Pr^n

Où:
  n = 0.4 si le fluide est CHAUFFÉ (T_paroi > T_fluide)
  n = 0.3 si le fluide est REFROIDI (T_paroi < T_fluide)

Dans le cas du refroidissement régénératif:
  Le coolant est chauffé → n = 0.4

DONC:
  Nu = 0.023 × Re^0.8 × Pr^0.4

**CONDITIONS DE VALIDITÉ:**
*   Re > 10,000 (écoulement pleinement turbulent)
*   0.6 < Pr < 160
*   L/D > 10 (écoulement développé)
*   Propriétés évaluées à T_bulk (température moyenne)
*   Flux de chaleur modéré
*   Parois lisses

**CALCUL DE h_c:**
$$ h_c = \frac{Nu \cdot k_{coolant}}{D_h} $$

**EXEMPLE DÉTAILLÉ:**
Données:
Coolant: RP-1 à 350 K
$\rho = 780 kg/m^3$, $\mu = 0.0008 Pa·s$, $C_p = 2100 J/kg·K$, $k = 0.12 W/m·K$, $v = 25 m/s$, $D_h = 3 mm = 0.003 m$

Calculs:
$Re = \rho \cdot v \cdot D_h / \mu = 780 \cdot 25 \cdot 0.003 / 0.0008 = 73,125$
$Pr = \mu \cdot C_p / k = 0.0008 \cdot 2100 / 0.12 = 14.0$
$Nu = 0.023 \cdot 73125^{0.8} \cdot 14.0^{0.4} = 0.023 \cdot 8,547 \cdot 2.92 = 573$
$h_c = 573 \cdot 0.12 / 0.003 = 22,920 W/m^2·K$

**CORRECTIONS POUR CAS PARTICULIERS:**
a) Correction pour L/D court (effets d'entrée): $Nu_{corrigé} = Nu \cdot (1 + (D/L)^{0.7})$
b) Correction pour T_paroi ≠ T_bulk: $Nu_{corrigé} = Nu \cdot (\mu_{bulk}/\mu_{paroi})^{0.14}$
c) Correction pour canaux non-circulaires: Utiliser $D_h$ hydraulique, mais précision réduite.


### 17.2 CORRÉLATION DE GNIELINSKI
───────────────────────────────────────────────────────────────

Plus précise que Dittus-Boelter, surtout en régime transitoire. Publiée par V. Gnielinski en 1976.

**ÉQUATION PRINCIPALE:**

$$ Nu = \frac{(f/8) \cdot (Re - 1000) \cdot Pr}{1 + 12.7 \cdot (f/8)^{0.5} \cdot (Pr^{2/3} - 1)} $$

Où $f$ est le facteur de frottement de Darcy:
$f = (0.79 \cdot \ln(Re) - 1.64)^{-2}$ [Équation de Petukhov]
Ou avec l'équation explicite de Colebrook-White simplifiée:
$f = 0.316 \cdot Re^{-0.25}$ [Équation de Blasius, Re < 10⁵]

**CONDITIONS DE VALIDITÉ:**
*   2300 < Re < 5×10⁶
*   0.5 < Pr < 2000
*   Plus précise que Dittus-Boelter
*   Valide aussi en régime transitoire (Re > 2300)
*   Propriétés évaluées à T_bulk

**EXEMPLE DÉTAILLÉ:**
Reprenons l'exemple précédent (RP-1, Re = 73,125, Pr = 14.0)

Calculs:
$f = (0.79 \cdot \ln(73125) - 1.64)^{-2} = (0.79 \cdot 11.2 - 1.64)^{-2} = (8.85 - 1.64)^{-2} = 7.21^{-2} = 0.0192$

Numérateur = $(0.0192/8) \cdot (73125-1000) \cdot 14.0 = 0.0024 \cdot 72125 \cdot 14.0 = 2424$

Dénominateur = $1 + 12.7 \cdot (0.0024)^{0.5} \cdot (14.0^{0.667} - 1) = 1 + 12.7 \cdot 0.049 \cdot (5.19 - 1) = 1 + 2.61 = 3.61$

$Nu = 2424 / 3.61 = 671$
$h_c = 671 \cdot 0.12 / 0.003 = 26,840 W/m^2·K$

**COMPARAISON:**
Dittus-Boelter: $h_c = 22,920 W/m^2·K$
Gnielinski: $h_c = 26,840 W/m^2·K$ (17% plus élevé)

Gnielinski est généralement plus précise (+/-10% vs +/-25%).


### 17.3 RÉGIME LAMINAIRE (Re < 2300)
───────────────────────────────────────────────────────────────

**ATTENTION:** **À ÉVITER DANS LES MOTEURS-FUSÉES!**
Le transfert thermique est très faible en laminaire.

**CAS DU FLUX CONSTANT:**
*   Nu = 4.36 (tube circulaire)
*   Nu = 3.66 (température de paroi constante)

**POUR CANAUX RECTANGULAIRES:**

| Rapport a/b | Nu (flux constant) |
| :--- | :--- |
| 1.0 (carré) | 3.61 |
| 2.0 | 4.12 |
| 4.0 | 5.35 |
| 8.0 | 6.49 |
| ∞ (plaques) | 8.24 |

**CONSÉQUENCE:**
En laminaire: $h_c \approx 100-500 W/m^2·K$ seulement!
C'est 10 à 100 fois moins qu'en turbulent.
→ Toujours concevoir pour Re > 10,000 minimum.


### 17.4 RÉGIME TRANSITOIRE (2300 < Re < 10000)
───────────────────────────────────────────────────────────────

Zone difficile à prédire avec précision.

**APPROCHE RECOMMANDÉE:**
Utiliser Gnielinski (valide dès Re > 2300).

**ALTERNATIVE - Interpolation:**
$Nu = Nu_{lam} + (Nu_{turb} - Nu_{lam}) \cdot \frac{Re - 2300}{10000 - 2300}$

**RECOMMANDATION:**
Éviter cette zone! Concevoir pour Re > 10,000.


### 17.5 ÉBULLITION SOUS-REFROIDIE (SUBCOOLED BOILING)
───────────────────────────────────────────────────────────────

Si $T_{paroi} > T_{saturation}$ mais $T_{bulk} < T_{saturation}$:
→ Formation de bulles à la paroi
→ Les bulles se condensent dans le cœur du fluide
→ Transfert thermique AMÉLIORÉ!

**CORRÉLATION DE CHEN (1966):**
$h_{total} = h_{convection} + h_{ébullition}$
$h_{ébullition} = S \cdot h_{nucleation}$

Où S est un facteur de suppression tenant compte de la turbulence qui inhibe la nucléation.

**AVANTAGES:**
*   h peut augmenter de 2 à 5 fois
*   Utilisé intentionnellement dans certains moteurs

**RISQUES:**
*   Si $T_{bulk}$ approche $T_{sat}$ → ébullition en masse
*   DNB (Departure from Nucleate Boiling) → destruction
*   Instabilités hydrauliques possibles


### 17.6 EFFETS DE LA GÉOMÉTRIE DES CANAUX
───────────────────────────────────────────────────────────────

La géométrie des canaux influence fortement $h_c$.

**TYPES DE CANAUX COURANTS:**
*   **Canaux rectangulaires** (fraisage ou impression 3D)
*   **Canaux circulaires** (perçage ou tubes)
*   **Canaux hélicoïdaux** (meilleur mélange)

**DIAMÈTRE HYDRAULIQUE:**
*   Canal rectangulaire: $D_h = \frac{2wh}{w+h}$
*   Canal circulaire: $D_h = D$
*   Anneau: $D_h = D_{ext} - D_{int}$

**EFFET DU RAPPORT D'ASPECT (h/w):**

| h/w | Effet |
| :--- | :--- |
| h/w ≈ 1 | Optimal pour h_c |
| h/w > 3 | Canaux étroits, h_c réduit aux coins |
| h/w < 0.3 | Canaux larges/plats, efficace |

**EFFET DU NOMBRE DE CANAUX:**
Plus de canaux → Plus petits $D_h$ → Re plus bas MAIS $D_h$ plus petit
$h_c \propto Nu \cdot k / D_h$

Si $D_h \downarrow$ de moitié:
*   Re $\downarrow$ de moitié
*   Nu $\downarrow$ d'environ 40% ($\propto Re^{0.8}$)
*   Mais $D_h \downarrow$ de 50%
*   Net: $h_c \uparrow$ d'environ 20%

**OPTIMISATION:**
Compromis entre:
*   $h_c$ élevé (petits canaux)
*   Pertes de charge acceptables (grands canaux)
*   Fabricabilité (dépend du procédé)


### 17.7 PERTES DE CHARGE DANS LES CANAUX
───────────────────────────────────────────────────────────────

Les pertes de charge sont liées au transfert thermique:
Plus de turbulence → meilleur $h_c$ MAIS plus de $\Delta P$

**ÉQUATION DE DARCY-WEISBACH:**
$$ \Delta P = \frac{f \cdot L \cdot \rho \cdot v^2}{2 \cdot D_h} $$

Où:
*   $f$ = facteur de frottement (Darcy)
*   $L$ = longueur du canal [m]
*   $\rho$ = masse volumique [kg/m³]
*   $v$ = vitesse [m/s]
*   $D_h$ = diamètre hydraulique [m]

**FACTEUR DE FROTTEMENT:**
*   Laminaire: $f = 64/Re$
*   Turbulent: $f \approx 0.316 \cdot Re^{-0.25}$ (Blasius)
*   Turbulent: $f = (0.79 \cdot \ln(Re) - 1.64)^{-2}$ (Petukhov)

**ORDRES DE GRANDEUR:**

| Configuration | $\Delta P$ typique (bar) |
| :--- | :--- |
| RP-1 dans canaux | 10 - 50 |
| LH2 dans canaux | 5 - 30 |
| LOX dans canaux | 10 - 40 |

**PUISSANCE DE POMPAGE:**
$P_{pompe} = \Delta P \cdot Q = \Delta P \cdot A \cdot v$

Cette puissance est "perdue" et doit être fournie par la turbopompe → impact sur les performances globales.


### 17.8 VALEURS TYPIQUES DE h_c - TABLEAU COMPLET
───────────────────────────────────────────────────────────────

| Coolant | T (K) | v (m/s) | h_c (W/m²·K) |
| :--- | :--- | :--- | :--- |
| LH2 | 25 | 50 | 50,000-150,000 |
| LH2 | 30 | 100 | 80,000-200,000 |
| LOX | 100 | 20 | 15,000-40,000 |
| LOX | 100 | 40 | 25,000-60,000 |
| CH4 | 150 | 20 | 10,000-30,000 |
| CH4 | 150 | 40 | 18,000-50,000 |
| RP-1 | 300 | 15 | 5,000-15,000 |
| RP-1 | 350 | 25 | 10,000-25,000 |
| RP-1 | 400 | 30 | 15,000-35,000 |
| C2H5OH | 300 | 20 | 8,000-20,000 |
| H2O | 350 | 10 | 15,000-40,000 |
| H2O | 350 | 30 | 30,000-80,000 |
| N2H4 | 320 | 15 | 8,000-22,000 |

CLASSEMENT PAR CAPACITÉ DE REFROIDISSEMENT:
  1. LH2 (meilleur! Cp très élevé, k élevé, μ faible)
  2. H2O (excellent mais T_boil basse)
  3. LOX (bon mais corrosif, limites de T)
  4. CH4 (très bon, propre, compatible)
  5. C2H5OH (bon, simple)
  6. RP-1 (correct mais cokéfaction)
  7. N2H4 (toxique, éviter si possible)


## 18. ÉPAISSEUR CRITIQUE, SERVICE ET ABLATION
═══════════════════════════════════════════════════════════════

Cette section traite des critères d'épaisseur et du phénomène d'ablation pour les parois trop épaisses.


### 18.1 ÉPAISSEUR CRITIQUE DE FUSION (e_melt)
───────────────────────────────────────────────────────────────

L'épaisseur critique est l'épaisseur MAXIMALE pour laquelle $T_{wall\_hot}$ reste inférieure à $T_{melt}$ (température de fusion).

**DÉRIVATION:**
En régime permanent: $T_{wall\_hot} = T_{wall\_cold} + q \cdot e/k$
Pour éviter la fusion: $T_{wall\_hot} \leq T_{melt}$
Donc: $T_{wall\_cold} + q \cdot e/k \leq T_{melt}$

Résolvant pour e:
$$ e \leq \frac{k \cdot (T_{melt} - T_{wall\_cold})}{q} $$

**FORMULE FINALE:**
$$ e_{melt} = \frac{k \cdot (T_{melt} - T_{wall\_cold})}{q} $$

**INTERPRÉTATION:**
*   Si $e < e_{melt}$: la paroi NE FOND PAS [OK]
*   Si $e = e_{melt}$: $T_{wall\_hot} = T_{melt}$ exactement (limite)
*   Si $e > e_{melt}$: la surface FOND [DANGER]

**FACTEURS FAVORABLES (e_melt élevé = plus de marge):**
*   k élevé (bonne conductivité)
*   T_melt élevé (matériau réfractaire)
*   T_wall_cold bas (bon refroidissement)
*   q faible (position loin du col)

**EXEMPLE NUMÉRIQUE - CuCr:**
$k = 320 W/m·K$
$T_{melt} = 1350 K$
$T_{wall\_cold} = 600 K$
$q = 25 MW/m^2$ (au col)

$e_{melt} = 320 \cdot (1350 - 600) / 25e6 = 320 \cdot 750 / 25e6 = 240,000 / 25e6 = 0.0096 m = 9.6 mm$

→ La paroi peut faire jusqu'à 9.6 mm avant de fondre.

**EXEMPLE - COMPARAISON MATÉRIAUX:**
Même conditions: $T_{wc} = 600 K, q = 25 MW/m^2$

| Matériau | k | T_melt | e_melt (mm) |
| :--- | :--- | :--- | :--- |
| Cuivre | 385 | 1358 K | 11.7 |
| CuCr | 320 | 1350 K | 9.6 |
| Inconel 718 | 11.4 | 1609 K | 0.46 |
| Inox 316L | 16.3 | 1673 K | 0.70 |
| AlSi10Mg | 130 | 870 K | 1.4 |
| Niobium | 53.7 | 2750 K | 4.6 |
| Molybdène | 138 | 2896 K | 12.7 |
| Tungstène | 173 | 3695 K | 21.4 |

**OBSERVATIONS:**
*   Cuivre et alliages: $e_{melt} \approx 10 mm$ (excellent)
*   Superalliages: $e_{melt} < 1 mm$ (faible conductivité!)
*   Réfractaires: $e_{melt}$ élevé grâce à $T_{melt}$ très haut


### 18.2 ÉPAISSEUR DE SERVICE (e_max)
───────────────────────────────────────────────────────────────

En pratique, on ne veut pas atteindre $T_{melt}$ mais rester en dessous de $T_{max\_service}$ pour éviter:
*   Perte de propriétés mécaniques
*   Fluage (déformation lente sous charge)
*   Oxydation accélérée
*   Changements métallurgiques

**FORMULE:**
$$ e_{max} = \frac{k \cdot (T_{max\_service} - T_{wall\_cold})}{q} $$

**TEMPÉRATURES MAX DE SERVICE:**

| Matériau | T_max_service (K) et raison |
| :--- | :--- |
| Cuivre | 800-900 K (ramollissement) |
| CuCr | 1000-1050 K (perte de dureté) |
| CuCrZr | 1050-1100 K |
| GRCop-84 | 1100-1200 K (excellent!) |
| Inconel 718 | 1100-1200 K (fluage) |
| Inconel 625 | 1150-1250 K |
| Inox 316L | 1000-1100 K |
| AlSi10Mg | 500-573 K (très bas!) |
| Niobium | 2000-2200 K (oxydation si pas vide) |
| Molybdène | 2200-2400 K |
| Tungstène | 2800-3000 K |

**MARGE DE SÉCURITÉ:**
Typiquement: $T_{design} = T_{max\_service} - 50$ à $100 K$

**EXEMPLE - CuCr:**
$k = 320 W/m·K$
$T_{max} = 1050 K$
$T_{wall\_cold} = 600 K$
$q = 25 MW/m^2$

$e_{max} = 320 \cdot (1050 - 600) / 25e6 = 320 \cdot 450 / 25e6 = 5.76 mm$

→ Épaisseur max pour rester sous $T_{max} = 5.76 mm$


### 6.3 PROCESSUS D'ABLATION
───────────────────────────────────────────────────────────────

Que se passe-t-il si l'épaisseur initiale e₀ > e_melt?

RÉPONSE: La surface fond et s'érode jusqu'à atteindre e_melt.

MÉCANISME PHYSIQUE DÉTAILLÉ:

  INSTANT t = 0 (allumage):
  ┌────────────────────────────────────────────────────────────┐
  │  Gaz chauds arrivent                                       │
  │  T_wall_hot commence à monter rapidement                   │
  │  (régime transitoire)                                      │
  └────────────────────────────────────────────────────────────┘
           ↓
  INSTANT t = τ (temps caractéristique):
  ┌────────────────────────────────────────────────────────────┐
  │  T_wall_hot atteint le régime "quasi-permanent"            │
  │  Si e₀ > e_melt: T_wall_hot > T_melt                       │
  │  → La surface commence à FONDRE                            │
  └────────────────────────────────────────────────────────────┘
           ↓
  PHASE D'ABLATION:
  ┌────────────────────────────────────────────────────────────┐
  │  • Métal fondu à la surface                                │
  │  • Gouttelettes emportées par le flux gazeux               │
  │  • Épaisseur diminue progressivement                       │
  │  • T_wall_hot reste ≈ T_melt (latent heat)                 │
  └────────────────────────────────────────────────────────────┘
           ↓
  ÉQUILIBRE (t >> τ):
  ┌────────────────────────────────────────────────────────────┐
  │  e final = e_melt                                          │
  │  T_wall_hot = T_melt                                       │
  │  Plus de fusion, état stable                               │
  └────────────────────────────────────────────────────────────┘


### 18.3 ÉPAISSEUR SACRIFICIELLE ET MASSE PERDUE
───────────────────────────────────────────────────────────────

**DÉFINITION:**
$e_{sacrificielle} = e_0 - e_{melt}$ (si $e_0 > e_{melt}$)
$e_{sacrificielle} = 0$ (si $e_0 \leq e_{melt}$)

C'est l'épaisseur qui va fondre et être emportée.

**MASSE PERDUE PAR UNITÉ DE SURFACE:**
$$ \Delta m/A = \rho_{métal} \cdot e_{sacrificielle} \quad [kg/m^2] $$

**MASSE TOTALE PERDUE:**
$$ \Delta m = \rho_{métal} \cdot A_{surface} \cdot e_{sacrificielle} \quad [kg] $$

**EXEMPLE NUMÉRIQUE:**
Données:
Matériau: CuCr
$\rho = 8900 kg/m^3$
$e_0 = 12 mm$ (épaisseur initiale)
$e_{melt} = 9.6 mm$ (calculé précédemment)
$A_{surface} = 0.05 m^2$ (surface au col)

Calculs:
$e_{sacrificielle} = 12 - 9.6 = 2.4 mm = 0.0024 m$
$\Delta m = 8900 \cdot 0.05 \cdot 0.0024 = 1.07 kg$

→ 1.07 kg de cuivre va fondre et être éjecté!


### 18.4 TEMPS D'ABLATION
───────────────────────────────────────────────────────────────

Combien de temps dure l'ablation?

**BILAN ÉNERGÉTIQUE:**
L'énergie pour fondre $e_{sac}$ d'épaisseur sur 1 m² est:
$$ E_{fusion} = \rho \cdot e_{sac} \cdot (C_p \cdot (T_{melt} - T_0) + L_{fusion}) $$

Où $L_{fusion}$ est la chaleur latente de fusion.

**CHALEUR LATENTE DE FUSION:**

| Matériau | L_fusion (kJ/kg) |
| :--- | :--- |
| Cuivre | 205 |
| Aluminium | 397 |
| Fer/Acier | 247 |
| Nickel | 298 |
| Niobium | 285 |
| Molybdène | 390 |
| Tungstène | 192 |

**FLUX DISPONIBLE POUR LA FUSION:**
Le flux "excédentaire" qui cause la fusion est:
$q_{fusion} = q_{entrant} - q_{évacué\_à\_T_{melt}}$

**TEMPS D'ABLATION (approximation):**
$$ t_{ablation} \approx \frac{\rho \cdot e_{sac} \cdot L_{fusion}}{q_{fusion}} $$

En pratique: quelques secondes à quelques dizaines de secondes.


### 6.6 QUAND L'ABLATION EST-ELLE ACCEPTABLE?
───────────────────────────────────────────────────────────────

L'ablation peut être:
  - ACCEPTÉE volontairement (moteurs ablatifs)
  - TOLÉRÉE accidentellement
  - CATASTROPHIQUE

CAS 1 - MOTEURS ABLATIFS (acceptable):
  ┌────────────────────────────────────────────────────────────┐
  │ • Conception prévue pour l'ablation                        │
  │ • Matériau sacrificiel (phénolique, silice)               │
  │ • Durée de fonctionnement limitée (quelques secondes)      │
  │ • Pas de refroidissement régénératif                       │
  │ • Simple, léger, fiable                                    │
  │ • Exemple: moteurs de missiles, boosters                   │
  └────────────────────────────────────────────────────────────┘

CAS 2 - ABLATION TOLÉRÉE:
  ┌────────────────────────────────────────────────────────────┐
  │ • Légère sur-épaisseur de sécurité                         │
  │ • Ablation minime (< 0.5 mm)                               │
  │ • Moteur reste fonctionnel après ablation                  │
  │ • Vérifié par calcul et tests                              │
  └────────────────────────────────────────────────────────────┘

CAS 3 - ABLATION CATASTROPHIQUE (à éviter!):
  ┌────────────────────────────────────────────────────────────┐
  │ * Percement de la paroi → fuite de gaz chauds             │
  │ * Contamination du coolant par métal fondu                │
  │ * Modification de la géométrie → perte de performances    │
  │ * Débris métalliques endommageant l'injecteur             │
  │ * Explosion possible!                                      │
  └────────────────────────────────────────────────────────────┘


### 6.7 DIMENSIONNEMENT POUR ÉVITER L'ABLATION
───────────────────────────────────────────────────────────────

RÈGLE DE CONCEPTION:

  e_design < e_max < e_melt

Où:
  e_design = épaisseur choisie
  e_max = épaisseur pour T_wall_hot = T_max_service
  e_melt = épaisseur pour T_wall_hot = T_melt

MARGES RECOMMANDÉES:

  e_design = 0.7 à 0.8 × e_max

Cette marge couvre:
  - Incertitudes sur h_g (±20-30%)
  - Variations locales de flux
  - Transitoires (démarrage/arrêt)
  - Vieillissement du matériau

PROCÉDURE DE DIMENSIONNEMENT:
  1. Calculer q_max (au col)
  2. Choisir le matériau (k, T_melt, T_max)
  3. Calculer e_melt et e_max
  4. Choisir e_design avec marge
  5. Vérifier résistance mécanique (pression)
  6. Vérifier stress thermique
  7. Itérer si nécessaire


### 6.8 CARTE THERMIQUE ET VARIATION AXIALE
───────────────────────────────────────────────────────────────

Le flux q varie le long du moteur:
  - Maximum au COL
  - Décroissant vers la chambre et le divergent

CONSÉQUENCE:
  e_melt et e_max VARIENT aussi le long du moteur!

APPROCHE DE CONCEPTION:
  ┌────────────────────────────────────────────────────────────┐
  │ OPTION 1: Épaisseur constante                              │
  │  + Simple à fabriquer                                      │
  │  - Sur-dimensionné dans chambre et divergent               │
  │  - Sous-dimensionné potentiel au col                       │
  ├────────────────────────────────────────────────────────────┤
  │ OPTION 2: Épaisseur variable                               │
  │  + Optimisé thermiquement                                  │
  │  + Masse minimale                                          │
  │  - Fabrication plus complexe                               │
  │  - Usinage ou impression 3D                                │
  ├────────────────────────────────────────────────────────────┤
  │ OPTION 3: Matériau variable (hybride)                      │
  │  + Optimal pour chaque zone                                │
  │  + CuCr au col, Inconel dans divergent, etc.               │
  │  - Joints complexes                                        │
  │  - Dilatation différentielle                               │
  └────────────────────────────────────────────────────────────┘

PROFIL TYPIQUE D'UN MOTEUR MODERNE:
  - Chambre: e = 3-5 mm (CuCr ou GRCop)
  - Convergent/Col: e = 1.5-3 mm (minimum pour q max)
  - Divergent: e = 2-4 mm (CuCr) ou transition vers acier


## 19. PROPRIÉTÉS DES MATÉRIAUX POUR MOTEURS-FUSÉES
═══════════════════════════════════════════════════════════════

Cette section détaille les matériaux utilisés pour les parois
de chambres de combustion et tuyères à refroidissement régénératif.


### 19.1 TABLEAU RÉCAPITULATIF DES PROPRIÉTÉS
───────────────────────────────────────────────────────────────

| Matériau | k (W/m·K) | T_melt (K) | T_max (K) | ρ (kg/m³) |
| :--- | :--- | :--- | :--- | :--- |
| Cuivre (Cu) | 385 | 1358 | 900 | 8960 |
| CuCr (C18200) | 320 | 1350 | 1050 | 8900 |
| CuCrZr (C18150) | 315 | 1355 | 1100 | 8890 |
| GRCop-84 (NASA) | 298 | 1350 | 1200 | 8870 |
| GRCop-42 | 310 | 1355 | 1150 | 8850 |
| AlSi10Mg (SLM) | 130 | 870 | 573 | 2670 |
| Al 6061-T6 | 167 | 925 | 573 | 2700 |
| Inconel 718 | 11.4 | 1609 | 1200 | 8190 |
| Inconel 625 | 9.8 | 1623 | 1250 | 8440 |
| Inconel X-750 | 12.0 | 1620 | 1150 | 8280 |
| Haynes 230 | 8.9 | 1635 | 1350 | 8970 |
| Haynes 188 | 10.4 | 1635 | 1320 | 8980 |
| Inox 316L | 16.3 | 1673 | 1100 | 8000 |
| Inox 304L | 16.2 | 1673 | 1050 | 7900 |
| Ti-6Al-4V | 6.7 | 1933 | 700 | 4430 |
| Niobium (Nb) | 53.7 | 2750 | 2200 | 8570 |
| C103 (Nb alloy) | 44.2 | 2685 | 2000 | 8860 |
  │ Molybdène (Mo)   │  138  │  2896   │  2400   │ 10280   │
  │ TZM (Mo alloy)   │  120  │  2895   │  2500   │ 10220   │
  │ Tungstène (W)    │  173  │  3695   │  3000   │ 19300   │
  │ W-Re (W alloy)   │  100  │  3450   │  2800   │ 19700   │
  │ Rhénium (Re)     │ 47.9  │  3459   │  2800   │ 21020   │
  │ Tantale (Ta)     │ 57.5  │  3290   │  2600   │ 16650   │
  │ Graphite         │  120  │  3900*  │  3500   │  2200   │
  │ C/C Composite    │ 50-150│  3900*  │  3200   │  1800   │
  │ SiC (CVD)        │  120  │  3100*  │  2000   │  3210   │
  └──────────────────┴───────┴─────────┴─────────┴─────────┘
  * Sublime au lieu de fondre


### 19.2 ALLIAGES DE CUIVRE - LES CHAMPIONS DU REFROIDISSEMENT
───────────────────────────────────────────────────────────────

Les alliages de cuivre sont les matériaux de choix pour les zones à haut flux thermique (chambre, col) grâce à leur excellente conductivité thermique.

**A) CUIVRE PUR (Cu - C10200, OFHC)**
*   **Composition:** Cu > 99.95%
*   **Propriétés:**
    *   k = 385-401 W/m·K (le meilleur!)
    *   $T_{melt} = 1358 K$ (1085°C)
    *   $T_{max} = 800-900 K$ (ramollissement)
    *   $\sigma_{yield} @ 20°C = 70 MPa$ (très faible)
    *   $\sigma_{yield} @ 500°C = 35 MPa$
*   **Avantages:** Conductivité maximale, Facile à usiner, Bon marché
*   **Inconvénients:** Très faible résistance mécanique, Ramollit rapidement à T > 500 K, Fluage important
*   **Utilisation:** Rarement seul pour moteurs haute pression, Parfois pour petits moteurs < 10 bar, Inserts ou revêtements

**B) CUIVRE-CHROME (CuCr - C18200)**
*   **Composition:** Cu + 0.6-1.2% Cr
*   **Propriétés:**
    *   k = 315-324 W/m·K
    *   $T_{melt} = 1350 K$
    *   $T_{max} = 1000-1050 K$
    *   $\sigma_{yield} @ 20°C = 310-450 MPa$ (traité)
    *   $\sigma_{yield} @ 500°C = 180 MPa$
    *   E = 130 GPa
    *   $\alpha = 16.5 \times 10^{-6} /K$
*   **Avantages:** Excellent compromis k / résistance, Très bien maîtrisé industriellement, Soudable (TIG, EBW, FSW), Disponible et économique
*   **Inconvénients:** Perd sa dureté si surchauffe > 800 K, Recristallisation possible
*   **Traitement thermique:** Mise en solution: 980°C, trempe eau; Vieillissement: 450-500°C, 2-4h
*   **Utilisation:** Merlin (SpaceX), RS-25 SSME (NASA/Aerojet), Vulcain (ESA), RD-180, RD-191 (Energomash) - TRÈS COURANT!

**C) CUIVRE-CHROME-ZIRCONIUM (CuCrZr - C18150)**
*   **Composition:** Cu + 0.5-1.5% Cr + 0.05-0.15% Zr
*   **Propriétés:**
    *   k = 310-320 W/m·K
    *   $T_{melt} = 1355 K$
    *   $T_{max} = 1050-1100 K$
    *   $\sigma_{yield} @ 20°C = 380-500 MPa$
    *   $\sigma_{yield} @ 600°C = 220 MPa$
*   **Avantages:** Meilleure tenue à chaud que CuCr, Résistance au fluage améliorée, Zr stabilise les précipités de Cr
*   **Inconvénients:** Plus cher que CuCr, Traitement thermique critique
*   **Utilisation:** RD-170/171 (Energomash), Moteurs russes haute performance, Réacteurs de fusion (ITER)

**D) GRCop-84 (NASA Glenn Research Center)**
*   **Composition:** Cu + 8% Cr + 4% Nb (nano-dispersions)
*   **Propriétés:**
    *   k = 285-300 W/m·K
    *   $T_{melt} = 1350 K$
    *   $T_{max} = 1150-1200 K$
    *   $\sigma_{yield} @ 20°C = 250 MPa$
    *   $\sigma_{yield} @ 800°C = 150 MPa$ (EXCELLENT!)
    *   Résistance au fluage: 100× meilleure que CuCr
*   **Avantages:** Excellente résistance à haute T, Résistance au fluage exceptionnelle, Stable microstructuralement, Idéal pour impression 3D (SLM/DMLS)
*   **Inconvénients:** Développé par NASA, accès limité, Fabrication spécialisée, Plus cher
*   **Fabrication:** Atomisation plasma, Impression 3D (SLM avec laser 400W+), HIP (Hot Isostatic Pressing)
*   **Utilisation:** RS-25 upgrades (SLS), Relativity Space (Terran 1, Aeon), Virgin Orbit (NewtonThree), Aerojet Rocketdyne (RL10 upgrades)

**E) GRCop-42 (variante)**
*   **Composition:** Cu + 4% Cr + 2% Nb
*   **Propriétés:**
    *   k = 305-315 W/m·K (meilleur que GRCop-84)
    *   $T_{max} = 1100-1150 K$
    *   Compromis entre k et résistance haute T
*   **Utilisation:** Applications où k est prioritaire, Développement en cours


### 7.3 SUPERALLIAGES BASE NICKEL
───────────────────────────────────────────────────────────────

Les superalliages sont utilisés pour les zones moins sollicitées
thermiquement mais nécessitant haute résistance mécanique.

A) INCONEL 718

  Composition: Ni-52%, Cr-19%, Fe-18%, Nb-5%, Mo-3%

  Propriétés:
    k = 11.4 W/m·K (faible!)
    T_melt = 1609 K
    T_max = 1100-1200 K
    σ_yield @ 20°C = 1035-1240 MPa (très élevé!)
    σ_yield @ 650°C = 1000 MPa
    E = 200 GPa

  **Avantages:**
    - Excellente résistance mécanique
    - Bonne résistance à l'oxydation
    - Soudable
    - Bien maîtrisé pour impression 3D

  **Inconvénients:**
    - Conductivité très faible (11× moins que CuCr)
    - Limite thermique malgré T_melt élevé
    - Usinage difficile

  Utilisation:
    - Structures de tuyères
    - Brides, collecteurs
    - Divergent (partie froide)
    - Chambres basse pression

B) INCONEL 625

  Composition: Ni-62%, Cr-22%, Mo-9%, Nb-3.5%

  Propriétés:
    k = 9.8 W/m·K
    T_melt = 1623 K
    T_max = 1200-1250 K
    σ_yield @ 20°C = 460-760 MPa
    Excellente résistance à la corrosion

  **Avantages:**
    - Meilleure résistance corrosion que 718
    - Soudable sans traitement post-soudure
    - Bon pour environnements agressifs

  Utilisation:
    - Divergent de tuyères
    - Environnements corrosifs
    - Propergols agressifs (N2O4, HNO3)

C) HAYNES 230

  Composition: Ni-57%, Cr-22%, W-14%, Mo-2%

  Propriétés:
    k = 8.9 W/m·K
    T_melt = 1635 K
    T_max = 1300-1350 K (excellent!)
    σ_yield @ 20°C = 390 MPa
    Résistance à l'oxydation exceptionnelle

  Utilisation:
    - Tuyères haute température
    - Applications spatiales réutilisables
    - Turbines, échangeurs

D) HAYNES 188

  Composition: Co-39%, Ni-22%, Cr-22%, W-14%

  Propriétés:
    k = 10.4 W/m·K
    T_max = 1300-1320 K
    Excellente résistance à l'oxydation

  Utilisation:
    - Tuyères pour moteurs réutilisables
    - Applications haute température longue durée


### 19.4 ALLIAGES D'ALUMINIUM
───────────────────────────────────────────────────────────────

Utilisés pour les petits moteurs ou prototypes grâce à leur légèreté et facilité d'usinage/impression 3D.

**A) AlSi10Mg (impression 3D)**
*   **Composition:** Al + 10% Si + 0.3% Mg
*   **Propriétés:**
    *   k = 120-140 W/m·K
    *   $T_{melt} = 870 K$ (597°C) - TRÈS BAS!
    *   $T_{max} = 473-573 K$ (200-300°C)
    *   $\rho = 2670 kg/m^3$ (léger!)
    *   $\sigma_{yield} @ 20°C = 230-280 MPa$ (SLM)
*   **Avantages:** Très léger (3× moins que CuCr), Excellente imprimabilité 3D, Conductivité correcte, Économique, Prototypage rapide
*   **Inconvénients:** $T_{max}$ TRÈS BASSE! (~300°C), Fond facilement, Limité aux faibles flux, Résistance chute rapidement avec T
*   **ATTENTION:** **ATTENTION:** SEULEMENT pour moteurs faible pression/flux ou zones très bien refroidies!
*   **Utilisation:** Prototypes, Petits moteurs (< 5 kN), Moteurs basse pression, Zones froides (divergent loin)

**B) Al 6061-T6**

  Composition: Al + 1% Mg + 0.6% Si + 0.3% Cu

  Propriétés:
    k = 167 W/m·K
    T_melt = 925 K
    T_max = 473-573 K
    σ_yield = 275 MPa

  Utilisation:
    - Structures, brides
    - Pas pour parois chaudes!


### 7.5 MÉTAUX RÉFRACTAIRES
───────────────────────────────────────────────────────────────

Pour les tuyères à rayonnement ou hautes températures extrêmes.
Utilisés principalement pour les divergents non refroidis.

A) NIOBIUM (Nb) et C103

  Nb pur:
    k = 53.7 W/m·K
    T_melt = 2750 K
    T_max = 2000-2200 K (sous vide!)
    ρ = 8570 kg/m³

  C103 (Nb-10Hf-1Ti):
    k = 44 W/m·K
    T_melt = 2685 K
    T_max = 1800-2000 K
    σ_yield @ 20°C = 310 MPa
    σ_yield @ 1200°C = 140 MPa

  **ATTENTION:** OXYDATION:
    Nb s'oxyde catastrophiquement à T > 700 K dans l'air!
    → Utilisable uniquement dans le VIDE spatial
    → Ou avec revêtement siliciure (MoSi2, WSi2)

  Revêtements protecteurs:
    - R512E (Si-20Cr-20Fe)
    - R512A (Si-20Cr-5Ti-5Fe)
    - Durée: quelques heures à 1600 K

  Utilisation:
    - Divergents de moteurs spatiaux
    - Apollo LM Descent Engine
    - RL10 (extension de tuyère)
    - Moteurs d'apogée

B) MOLYBDÈNE (Mo) et TZM

  Mo pur:
    k = 138 W/m·K (excellent pour réfractaire!)
    T_melt = 2896 K
    T_max = 2200-2400 K
    ρ = 10280 kg/m³

  TZM (Mo-0.5Ti-0.08Zr):
    k = 115-125 W/m·K
    T_melt = 2895 K
    T_max = 2300-2500 K
    σ_yield @ 20°C = 700 MPa
    σ_yield @ 1000°C = 420 MPa

  **ATTENTION:** OXYDATION:
    Forme MoO3 volatil à T > 800 K dans l'air
    → "Peste du molybdène"
    → Vide ou atmosphère inerte obligatoire

  Utilisation:
    - Inserts de col (vide spatial)
    - Tuyères haute température
    - Propulsion électrique (résistojets)

C) TUNGSTÈNE (W) et W-Re

  W pur:
    k = 173 W/m·K
    T_melt = 3695 K (le plus haut des métaux!)
    T_max = 2800-3000 K
    ρ = 19300 kg/m³ (très lourd!)
    σ_yield @ 20°C = 700-1000 MPa

  W-Re (W + 3-25% Re):
    k = 80-120 W/m·K
    T_melt = 3200-3450 K
    Meilleure ductilité que W pur
    σ_yield @ 1500°C = 300 MPa

  **ATTENTION:** CARACTÉRISTIQUES:
    - Très fragile à température ambiante
    - DBTT (ductile-brittle) ≈ 400°C
    - Usinage très difficile (EDM)
    - Oxyde à T > 700 K dans l'air

  Utilisation:
    - Inserts de col (cas extrêmes)
    - Propulsion électrique (résistojets, arcjets)
    - Protection thermique

D) RHÉNIUM (Re)

  Propriétés:
    k = 47.9 W/m·K
    T_melt = 3459 K
    T_max = 2600-2800 K
    ρ = 21020 kg/m³ (2ème plus dense)

  **Avantages:**
    - Ductile à toutes températures
    - Pas de DBTT comme W
    - Excellente résistance au fluage

  **Inconvénients:**
    - EXTRÊMEMENT cher (~5000 $/kg)
    - Rare (production mondiale: 50 tonnes/an)
    - Lourd

  Utilisation:
    - Revêtement sur W ou Ir
    - Applications spatiales critiques
    - Très limité (coût prohibitif)


### 7.6 MATÉRIAUX CÉRAMIQUES ET COMPOSITES
───────────────────────────────────────────────────────────────

A) GRAPHITE

  Propriétés:
    k = 80-150 W/m·K (selon orientation)
    T_sublime = 3900 K (pas de fusion!)
    T_max = 3200-3500 K (vide)
    ρ = 1800-2200 kg/m³ (léger!)

  **ATTENTION:** OXYDATION:
    Brûle à T > 700 K dans l'air!
    → Vide spatial uniquement
    → Ou revêtement SiC

  Utilisation:
    - Insertions de col (moteurs solides)
    - Tuyères de rentrée atmosphérique

B) COMPOSITE CARBONE-CARBONE (C/C)

  Propriétés:
    k = 50-150 W/m·K (selon orientation)
    T_max = 3000-3200 K
    ρ = 1600-1900 kg/m³
    σ_tension = 200-400 MPa

  **Avantages:**
    - Très léger
    - k augmente avec T (!!)
    - Résistance maintenue à haute T

  **Inconvénients:**
    - Oxydation catastrophique si air
    - Fabrication longue et coûteuse
    - Anisotrope

  Utilisation:
    - Navette spatiale (bords d'attaque)
    - Tuyères de moteurs solides
    - Freins d'avions (non-spatial)

C) CARBURE DE SILICIUM (SiC)

  Propriétés:
    k = 120 W/m·K
    T_décompose = 3100 K
    T_max = 1900-2000 K
    ρ = 3210 kg/m³

  **Avantages:**
    - Résistant à l'oxydation
    - Dur et résistant à l'érosion

  Utilisation:
    - Revêtements protecteurs
    - Échangeurs de chaleur


### 7.7 CRITÈRES DE SÉLECTION DES MATÉRIAUX
───────────────────────────────────────────────────────────────

POUR LA CHAMBRE ET LE COL (flux max):

  Priorité 1: k élevé (évacuer la chaleur)
  Priorité 2: T_max adéquat
  Priorité 3: Résistance mécanique

  → CHOIX: CuCr, CuCrZr, GRCop-84

POUR LE DIVERGENT (flux modéré):

  Option A: Refroidissement régénératif
    → CuCr ou transition vers Inconel

  Option B: Rayonnement (spatial)
    → Nb/C103, Mo/TZM, ou composites

POUR PROTOTYPES/TESTS:

  → AlSi10Mg (impression 3D, économique)
  → Durée de vie limitée acceptable

ARBRE DE DÉCISION:

  ┌─ Flux > 20 MW/m² ? ─────────────────────────────────────┐
  │                                                          │
  │ OUI                              NON                     │
  │  │                                │                      │
  │  ↓                                ↓                      │
  │ CuCr/CuCrZr/GRCop              Inconel ou                │
  │ (OBLIGATOIRE)                   matériau économique      │
  │                                                          │
  └──────────────────────────────────────────────────────────┘

  ┌─ Réutilisable ? ────────────────────────────────────────┐
  │                                                          │
  │ OUI → GRCop-84 (résistance fluage)                       │
  │ NON → CuCr (économique)                                  │
  │                                                          │
  └──────────────────────────────────────────────────────────┘

  ┌─ Impression 3D ? ───────────────────────────────────────┐
  │                                                          │
  │ OUI → GRCop-84 (optimal)                                 │
  │       Inconel 718 (structures)                           │
  │       AlSi10Mg (prototypes)                              │
  │                                                          │
  │ NON → CuCr forgé/usiné (économique)                      │
  │                                                          │
  └──────────────────────────────────────────────────────────┘


### 7.8 EXEMPLES DE MOTEURS RÉELS
───────────────────────────────────────────────────────────────

MERLIN 1D (SpaceX):
  - Chambre/col: CuCr (usiné)
  - Divergent: Nb-C103 (rayonnement)
  - Épaisseur: 1.5-3 mm
  - Pression: 97 bar

RS-25 / SSME (NASA/Aerojet):
  - Chambre: CuCr (fraisé + électroformé Ni)
  - Col: CuCr
  - Divergent: Inconel 718
  - Canaux: 430 canaux de refroidissement
  - Pression: 206 bar

RAPTOR (SpaceX):
  - Chambre/col: GRCop-84 ou variante (SLM)
  - Fabrication additive
  - Pression: 300+ bar

RD-170/180 (Energomash):
  - Chambre: CuCrZr (brasé)
  - Col: CuCrZr
  - Divergent: Inox + Nb
  - Canaux: tubes enroulés

BE-4 (Blue Origin):
  - Chambre: CuCr ou GRCop
  - Fabrication hybride (SLM + traditionnel)
  - Pression: 135 bar

VULCAIN 2 (ESA):
  - Chambre: CuCr (fraisé)
  - Divergent: Inconel + tubes
  - Pression: 115 bar


## 20. PROPRIÉTÉS DES COOLANTS - GUIDE COMPLET
═══════════════════════════════════════════════════════════════

Cette section détaille les propriétés thermophysiques des
fluides utilisés pour le refroidissement régénératif.


### 20.1 TABLEAU RÉCAPITULATIF DES COOLANTS

| Coolant | Cp (J/kg·K) | T_boil (K) | T_crit (K) | ρ (kg/m³) | μ (mPa·s) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| LH2 | 14300 | 20.3 | 33.2 | 71 | 0.013 |
| LOX | 1700 | 90.2 | 154.6 | 1141 | 0.19 |
| LN2 | 2040 | 77.4 | 126.2 | 808 | 0.16 |
| CH4 (LCH4) | 3500 | 111.7 | 190.6 | 422 | 0.12 |
| C2H6 (éthane) | 2500 | 184.6 | 305.3 | 544 | 0.18 |
| C3H8 (propane) | 2500 | 231.1 | 369.8 | 582 | 0.20 |
| RP-1 | 2000 | 490 | 678 | 810 | 1.2 |
| Jet-A | 2100 | 450 | 650 | 800 | 1.5 |
| C2H5OH | 2440 | 351.4 | 514.0 | 789 | 1.1 |
| CH3OH | 2530 | 337.8 | 512.6 | 791 | 0.55 |
| N2H4 | 3100 | 387.0 | 653.0 | 1004 | 0.97 |
| MMH | 2900 | 360.5 | 585.0 | 874 | 0.78 |
| UDMH | 2750 | 336.0 | 523.0 | 791 | 0.51 |
| H2O | 4186 | 373.2 | 647.1 | 1000 | 1.0 |
| H2O2 (90%) | 2800 | 423.0 | 730 | 1390 | 1.2 |
| NH3 | 4700 | 239.8 | 405.4 | 682 | 0.26 |
| N2O | 1900 | 184.7 | 309.6 | 1220 | 0.14 |

Note: Propriétés au point d'ébullition @ 1 bar sauf indication.


### 8.2 HYDROGÈNE LIQUIDE (LH2) - LE MEILLEUR COOLANT

L'hydrogène liquide est le MEILLEUR coolant pour plusieurs raisons:

PROPRIÉTÉS DÉTAILLÉES:

| Propriété | Valeur |
| :--- | :--- |
| Masse molaire | 2.016 g/mol |
| Température ébullition | 20.3 K (-253°C) @ 1 bar |
| Température critique | 33.2 K |
| Pression critique | 13.0 bar |
| Densité liquide | 70.8 kg/m³ @ 20 K |
| Densité gaz | 1.34 kg/m³ @ NBP |
| Cp liquide | 9,700-14,300 J/kg·K |
| Cp gaz | 14,300 J/kg·K |
| Conductivité (liq) | 0.10 W/m·K |
| Conductivité (gaz) | 0.017 W/m·K |
| Viscosité (liq) | 13 μPa·s (très faible!) |
| Prandtl | 0.7-1.3 |
| Chaleur latente | 448 kJ/kg |

**AVANTAGES THERMIQUES:**
  - Cp ÉNORME (14,300 J/kg·K) → absorbe beaucoup d'énergie
  - Viscosité très faible → Re élevé → h_c élevé
  - k/μ élevé → excellent transfert
  - h_c typique: 50,000-200,000 W/m²·K!

**INCONVÉNIENTS:**
  - Très basse température → isolation critique
  - Densité très faible → gros réservoirs
  - Fuit facilement (petite molécule)
  - Fragilisation hydrogène des métaux
  - Coût de production/stockage

**PRÉCAUTIONS:**
  - Matériaux compatibles: Al, Inox 304/316, Inconel
  - Éviter: aciers au carbone (fragilisation)
  - Joints: PTFE, Indium, soudures
  - Risque d'explosion si mélange avec O2!

MOTEURS UTILISANT LH2:
  - RS-25 / SSME (NASA)
  - RL10 (Aerojet Rocketdyne)
  - J-2, J-2X (Saturn V, SLS)
  - Vulcain (Ariane)
  - LE-7, LE-9 (Japon)
  - CE-20 (Inde)


### 8.3 OXYGÈNE LIQUIDE (LOX)

Le LOX est parfois utilisé comme coolant (cycles oxydizer-rich).

PROPRIÉTÉS DÉTAILLÉES:

| Propriété | Valeur |
| :--- | :--- |
| Masse molaire | 32.0 g/mol |
| Température ébullition | 90.2 K (-183°C) @ 1 bar |
| Température critique | 154.6 K |
| Pression critique | 50.4 bar |
| Densité liquide | 1141 kg/m³ @ 90 K |
| Cp liquide | 1,700 J/kg·K |
| Conductivité (liq) | 0.15 W/m·K |
| Viscosité (liq) | 190 μPa·s |
| Prandtl | 2.2 |
| Chaleur latente | 213 kJ/kg |

**AVANTAGES:**
  - Disponible (c'est l'oxydant!)
  - Bonne densité → compact
  - Température modérée (90 K vs 20 K pour LH2)

**INCONVÉNIENTS:**
  - Cp modéré seulement
  - TRÈS réactif → risques d'ignition
  - Incompatible avec hydrocarbures chauds
  - Corrosif à haute température

**ATTENTION EXTRÊME:**
  - LOX + matière organique = EXPLOSION
  - Nettoyage LOX obligatoire (dégraissage)
  - Matériaux: Inox, Monel, Inconel
  - Éviter: Al (sauf alliages spéciaux), Ti

UTILISATION:
  - RD-170/180 (cycle oxidizer-rich)
  - Quelques moteurs à cycle ox-rich
  - Généralement le FUEL est préféré comme coolant


### 8.4 MÉTHANE LIQUIDE (LCH4)

Le méthane gagne en popularité (Raptor, BE-4, etc.)

PROPRIÉTÉS DÉTAILLÉES:

| Propriété | Valeur |
| :--- | :--- |
| Masse molaire | 16.04 g/mol |
| Température ébullition | 111.7 K (-161°C) @ 1 bar |
| Température critique | 190.6 K |
| Pression critique | 46.0 bar |
| Densité liquide | 422 kg/m³ @ 112 K |
| Cp liquide | 3,500 J/kg·K |
| Conductivité (liq) | 0.19 W/m·K |
| Viscosité (liq) | 120 μPa·s |
| Prandtl | 2.2 |
| Chaleur latente | 510 kJ/kg |

**AVANTAGES:**
  - Cp élevé (meilleur que RP-1)
  - Température modérée (112 K)
  - PAS DE COKÉFACTION! (propre)
  - Compatible avec O2 (ISRU Mars)
  - Densité acceptable
  - Viscosité faible → bon Re

**INCONVÉNIENTS:**
  - Moins dense que RP-1
  - Cryogénique (infrastructure)
  - Plage de T plus étroite que H2

AVANTAGE CLÉ - PAS DE COKE:
  Le méthane ne forme PAS de dépôts carbonés
  contrairement au RP-1/kérosène. Les moteurs peuvent
  être réutilisés sans nettoyage des canaux!

MOTEURS UTILISANT CH4:
  - Raptor (SpaceX) - full-flow staged combustion
  - BE-4 (Blue Origin) - oxygen-rich staged combustion
  - Prometheus (ESA)
  - Vulcan Centaur (ULA, via BE-4)


### 8.5 RP-1 / KÉROSÈNE

Le RP-1 est le fuel hydrocarbure le plus utilisé historiquement.

PROPRIÉTÉS DÉTAILLÉES:

| Propriété | Valeur (typique @ 300K) |
| :--- | :--- |
| Composition | C12H24 (moyenne) |
| Masse molaire | ~170 g/mol |
| Point éclair | 316 K (43°C) |
| Température ébullition | 490-540 K (plage) |
| Température critique | ~678 K |
| Densité @ 288 K | 799-815 kg/m³ |
| Cp @ 300 K | 2,000 J/kg·K |
| Cp @ 400 K | 2,300 J/kg·K |
| Cp @ 500 K | 2,800 J/kg·K |
| Conductivité @ 300 K | 0.12 W/m·K |
| Conductivité @ 400 K | 0.10 W/m·K |
| Viscosité @ 300 K | 1.2 mPa·s |
| Viscosité @ 400 K | 0.4 mPa·s |
| Prandtl @ 300 K | 20 |
| Prandtl @ 400 K | 9 |

**AVANTAGES:**
  - Stockable à température ambiante!
  - Haute densité → réservoirs compacts
  - Infrastructure existante (aviation)
  - Non toxique (relativement)
  - Économique

**INCONVÉNIENTS MAJEURS:**

  **COKÉFACTION (problème critique!):**

  À T > 450-500 K, le RP-1 se décompose et dépose du
  carbone (coke) sur les parois des canaux:

    - Réduit la section de passage
    - Réduit le transfert thermique
    - Peut boucher les canaux!
    - Limite la réutilisabilité

  TEMPÉRATURE LIMITE:
    T_paroi_froid < 480 K (idéal < 420 K)

  SOLUTIONS:
    - RP-2 (version purifiée, moins de soufre)
    - Additifs anti-coke
    - Vitesses élevées (moins de temps de résidence)
    - Canaux larges (plus faciles à nettoyer)

VARIATION DES PROPRIÉTÉS AVEC T:

| T (K) | 300 | 350 | 400 | 450 |
| :--- | :--- | :--- | :--- | :--- |
| ρ (kg/m³) | 810 | 775 | 740 | 700 |
| Cp (J/kg·K) | 2000 | 2150 | 2300 | 2500 |
| k (W/m·K) | 0.12 | 0.11 | 0.10 | 0.09 |
| μ (mPa·s) | 1.2 | 0.65 | 0.40 | 0.28 |
| Pr | 20 | 12.7 | 9.2 | 7.8 |

MOTEURS UTILISANT RP-1:
  - Merlin (SpaceX Falcon 9)
  - RD-180, RD-191 (Atlas V, Angara)
  - NK-33 (N1)
  - RS-27 (Delta II)
  - F-1 (Saturn V)
  - Rutherford (Rocket Lab) - électropompe


### 8.6 ÉTHANOL (C2H5OH)

Utilisé historiquement et par certains nouveaux acteurs.

PROPRIÉTÉS DÉTAILLÉES:

| Propriété | Valeur @ 300 K |
| :--- | :--- |
| Masse molaire | 46.07 g/mol |
| Température ébullition | 351.4 K (78°C) |
| Température critique | 514 K |
| Pression critique | 63 bar |
| Densité | 789 kg/m³ |
| Cp | 2,440 J/kg·K |
| Conductivité | 0.17 W/m·K |
| Viscosité | 1.1 mPa·s |
| Prandtl | 16 |
| Chaleur latente | 838 kJ/kg |

**AVANTAGES:**
  - Stockable, non cryogénique
  - Non toxique, biodégradable
  - Bonne capacité de refroidissement
  - Peut contenir de l'eau (refroidissement film)
  - Production renouvelable possible

**INCONVÉNIENTS:**
  - Point d'ébullition bas (78°C)
  - Risque d'ébullition dans les canaux
  - Isp inférieure au RP-1
  - Hygroscopique (absorbe l'eau)

UTILISATION HISTORIQUE:
  - V-2 (Allemagne WWII)
  - Redstone (USA)
  - Moteurs amateurs/universitaires

MOTEURS MODERNES:
  - MIRA (Espagne)
  - Copenhagen Suborbitals
  - Nombreux projets New Space


### 8.7 HYDRAZINE ET DÉRIVÉS (N2H4, MMH, UDMH)

**TOXIQUES ET DANGEREUX** - Usage spatial principalement

A) HYDRAZINE (N2H4)

| Propriété | Valeur |
| :--- | :--- |
| Masse molaire | 32.05 g/mol |
| Température fusion | 274.7 K (1.5°C) |
| Température ébullition | 387 K (114°C) |
| Densité | 1,004 kg/m³ |
| Cp | 3,100 J/kg·K |
| Conductivité | 0.35 W/m·K (élevé!) |
| Viscosité | 0.97 mPa·s |

  **Avantages:** Stockable, hypergolique avec N2O4
  **Inconvénients:** TRÈS TOXIQUE, cancérigène

B) MMH (Monométhylhydrazine - CH3NHNH2)

  Densité: 874 kg/m³
  T_boil: 360.5 K
  Cp: 2,900 J/kg·K

  Moins toxique que N2H4, plus stable.
  Utilisé: Apollo LM, systèmes orbitaux.

C) UDMH (Diméthylhydrazine asymétrique)

  Densité: 791 kg/m³
  T_boil: 336 K
  Cp: 2,750 J/kg·K

  Plus stable au stockage.
  Utilisé: Proton (Russie), Longue Marche (Chine).

UTILISATION:
  - Systèmes orbitaux et interplanétaires
  - Moteurs vernier et RCS
  - En diminution (toxicité)


### 8.8 EAU (H2O)
───────────────────────────────────────────────────────────────

L'eau est un EXCELLENT coolant mais rarement utilisée seule.

PROPRIÉTÉS:
  ┌────────────────────────┬──────────────────────────────────┐
  │ Propriété              │ Valeur @ 300 K                   │
  ├────────────────────────┼──────────────────────────────────┤
  │ Masse molaire          │ 18.02 g/mol                      │
  │ Température ébullition │ 373.2 K (100°C)                  │
  │ Température critique   │ 647.1 K                          │
  │ Pression critique      │ 220.6 bar                        │
  │ Densité                │ 1,000 kg/m³                      │
  │ Cp                     │ 4,186 J/kg·K (très élevé!)       │
  │ Conductivité           │ 0.60 W/m·K (excellent!)          │
  │ Viscosité              │ 1.0 mPa·s                        │
  │ Prandtl                │ 7                                │
  │ Chaleur latente        │ 2,257 kJ/kg (énorme!)            │
  └────────────────────────┴──────────────────────────────────┘

**AVANTAGES:**
  - Cp très élevé (4,186 J/kg·K)
  - Conductivité excellente (0.60 W/m·K)
  - Chaleur latente énorme (ébullition = super refroidissement)
  - Non toxique, disponible
  - Économique

**INCONVÉNIENTS:**
  - Point d'ébullition bas (100°C @ 1 bar)
  - Gel à 0°C (problème spatial)
  - Corrosif si impuretés
  - Non utilisé comme propergol directement

UTILISATION:
  - Tests au sol (refroidissement auxiliaire)
  - Injection pour refroidissement film (mélange éthanol-eau)
  - Systèmes terrestres


### 8.9 AMMONIAC (NH3)
───────────────────────────────────────────────────────────────

Utilisé dans certaines applications spatiales.

PROPRIÉTÉS:
  ┌────────────────────────┬──────────────────────────────────┐
  │ Propriété              │ Valeur                           │
  ├────────────────────────┼──────────────────────────────────┤
  │ Masse molaire          │ 17.03 g/mol                      │
  │ Température ébullition │ 239.8 K (-33°C)                  │
  │ Température critique   │ 405.4 K                          │
  │ Densité liquide        │ 682 kg/m³                        │
  │ Cp                     │ 4,700 J/kg·K (très élevé!)       │
  │ Conductivité           │ 0.52 W/m·K                       │
  │ Viscosité              │ 0.26 mPa·s                       │
  │ Prandtl                │ 2.4                              │
  │ Chaleur latente        │ 1,370 kJ/kg                      │
  └────────────────────────┴──────────────────────────────────┘

**AVANTAGES:**
  - Cp élevé (4,700 J/kg·K)
  - Bonne conductivité
  - Stockable sous pression modérée
  - Utilisable comme propergol (avec décomposition)

**INCONVÉNIENTS:**
  - Toxique (irritant)
  - Odeur forte
  - Corrosif pour cuivre et laiton

UTILISATION:
  - Systèmes de contrôle thermique (boucles)
  - Propulsion électrique (résistojets)
  - ISS (système de refroidissement)


### 8.10 COMPARAISON ET SÉLECTION DU COOLANT
───────────────────────────────────────────────────────────────

CLASSEMENT PAR CAPACITÉ DE REFROIDISSEMENT:

  ┌────────────────┬────────────┬──────────────────────────────┐
  │ Rang │ Coolant │ Cp×k/μ     │ Commentaire                  │
  ├──────┼─────────┼────────────┼──────────────────────────────┤
  │  1   │ LH2     │ 110,000    │ Le meilleur, mais cryogénique│
  │  2   │ H2O     │ 2,500      │ Excellent mais T_boil basse  │
  │  3   │ NH3     │ 1,900      │ Très bon, stockable          │
  │  4   │ LCH4    │ 550        │ Bon compromis, propre        │
  │  5   │ LOX     │ 130        │ Correct, mais réactif        │
  │  6   │ C2H5OH  │ 75         │ Acceptable, non toxique      │
  │  7   │ RP-1    │ 20         │ Médiocre mais stockable      │
  └──────┴─────────┴────────────┴──────────────────────────────┘

ARBRE DE DÉCISION:

  ┌─ Cycle propulsif ? ─────────────────────────────────────────┐
  │                                                              │
  │ LOX/LH2  → Utiliser LH2 comme coolant (toujours)            │
  │ LOX/CH4  → Utiliser CH4 comme coolant                        │
  │ LOX/RP-1 → Utiliser RP-1 (attention cokéfaction)            │
  │ N2O4/MMH → Utiliser MMH (fuel côté refroidissement)         │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘

  ┌─ Fuel ou Ox pour refroidir ? ───────────────────────────────┐
  │                                                              │
  │ FUEL PRÉFÉRÉ (99% des cas):                                  │
  │  - Moins réactif que l'oxydant                               │
  │  - Généralement meilleur Cp                                  │
  │  - Pas de risque d'ignition avec matériaux                   │
  │                                                              │
  │ OX UTILISÉ (rare):                                           │
  │  - Cycles oxydizer-rich (RD-170)                             │
  │  - Nécessite matériaux spéciaux (Monel, Inconel)            │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘

DIMENSIONNEMENT DU DÉBIT COOLANT:

  Le débit de coolant doit absorber toute la chaleur:

  Q_total = ṁ_coolant × Cp × ΔT_coolant

  ṁ_coolant = Q_total / (Cp × ΔT_max_admissible)

  Typiquement: ΔT_coolant = 100-300 K selon le fluide

EXEMPLE:
  Q_total = 5 MW (intégrale du flux sur la surface)
  Coolant: RP-1, Cp = 2100 J/kg·K, ΔT = 150 K

  ṁ_coolant = 5×10⁶ / (2100 × 150) = 15.9 kg/s

  Si ratio O/F = 2.5, et ṁ_total = 50 kg/s:
  ṁ_fuel = 50/3.5 = 14.3 kg/s

  → ATTENTION: ṁ_coolant > ṁ_fuel disponible!
  → Il faut réduire Q ou augmenter h_c


### 8.11 PROPRIÉTÉS EN FONCTION DE LA TEMPÉRATURE
───────────────────────────────────────────────────────────────

Les propriétés des fluides varient significativement avec T.
Cela affecte les calculs de h_c.

MÉTHANE (LCH4):
  ┌──────────┬────────┬────────┬────────┬────────┬────────┐
  │ T (K)    │  115   │  130   │  150   │  170   │  190   │
  ├──────────┼────────┼────────┼────────┼────────┼────────┤
  │ ρ (kg/m³)│  420   │  400   │  370   │  330   │  260   │
  │ Cp J/kg·K│  3450  │  3600  │  3900  │  4500  │  6000  │
  │ k W/m·K  │  0.19  │  0.17  │  0.14  │  0.11  │  0.08  │
  │ μ (μPa·s)│  115   │  90    │  65    │  45    │  30    │
  └──────────┴────────┴────────┴────────┴────────┴────────┘

HYDROGÈNE (LH2):
  ┌──────────┬────────┬────────┬────────┬────────┐
  │ T (K)    │   20   │   25   │   30   │   33   │
  ├──────────┼────────┼────────┼────────┼────────┤
  │ ρ (kg/m³)│   71   │   65   │   50   │   31   │
  │ Cp J/kg·K│  9700  │ 12000  │ 19000  │   ∞    │
  │ k W/m·K  │  0.10  │  0.10  │  0.09  │  0.07  │
  │ μ (μPa·s)│   13   │   11   │    8   │    5   │
  └──────────┴────────┴────────┴────────┴────────┘

Note: À T_critique, Cp → ∞ (transition de phase)

CONSEIL:
  Toujours utiliser les propriétés à T_film:

  T_film = (T_wall_cold + T_bulk) / 2


## 21. EXEMPLES DE CALCUL COMPLETS
═══════════════════════════════════════════════════════════════

Cette section présente plusieurs exemples de calcul détaillés pour
illustrer l'application des équations thermiques aux moteurs-fusées.
Chaque exemple suit une méthodologie complète et vérifie les résultats.


### 21.1 EXEMPLE 1 : PETIT MOTEUR LOX/RP-1 (TYPE AMATEUR AVANCÉ)

DONNÉES DU PROBLÈME:

| PARAMÈTRES DE CONCEPTION | |
| :--- | :--- |
| Propergols: | LOX / RP-1 |
| Pression chambre: | 25 bar (2.5 MPa) |
| Rapport O/F: | 2.4 |
| Débit total: | 0.8 kg/s |
| Diamètre col: | 30 mm |
| Ratio expansion: | 8:1 |
| T chambre: | 3200 K (calculé CEA) |
| γ gaz: | 1.21 |
| M gaz: | 22.5 kg/kmol |
| μ gaz: | 8.2×10⁻⁵ Pa·s |
| Cp gaz: | 2100 J/kg·K |
| **SYSTÈME DE REFROIDISSEMENT** | |
| Coolant: | RP-1 |
| T entrée coolant: | 300 K |
| Pression coolant: | 30 bar |
| Vitesse coolant: | 20 m/s |
| Dh canal: | 4 mm |
| **PAROI** | |
| Matériau: | CuCr1Zr |
| Conductivité: | 320 W/m·K |
| T limite: | 723 K (450°C) |
| T fusion: | 1350 K |
| Épaisseur: | 3 mm |

ÉTAPE 1 - CALCUL DU COEFFICIENT $h_g$ (ÉQUATION DE BARTZ)

Données nécessaires:
*   $D_t = 0.030 \text{ m}$ (diamètre col)
*   $A_t = \pi \times (0.030)^2 / 4 = 7.07 \times 10^{-4} \text{ m}^2$
*   $P_c = 25 \times 10^5 \text{ Pa}$
*   $c^* = 1650 \text{ m/s}$ (calculé ou table CEA)
*   $T_c = 3200 \text{ K}$
*   $M = 22.5 \text{ kg/kmol}$
*   $\gamma = 1.21$
*   $\mu = 8.2 \times 10^{-5} \text{ Pa}\cdot\text{s}$
*   $C_p = 2100 \text{ J/kg}\cdot\text{K}$
*   $Pr = \mu \times C_p / k_{gaz} \approx 0.72$

Calcul du nombre de Prandtl:
$$ Pr = \frac{C_p \mu}{k_{gaz}} $$
$$ k_{gaz} \approx \frac{C_p \mu}{Pr} = \frac{2100 \times 8.2 \times 10^{-5}}{0.72} = 0.239 \text{ W/m}\cdot\text{K} $$

Facteur de correction $\sigma$ (Bartz):
$T_{wall}$ estimée $\approx 900 \text{ K}$ (première itération)
$$ T_{aw} = T_c \left[1 + \frac{\gamma-1}{2} r M^2\right] $$
Au col ($M=1$): $T_{aw} \approx 0.91 \times T_c = 2912 \text{ K}$

$$ \sigma = \left[0.5 \frac{T_{wall}}{T_c} \left(1 + \frac{\gamma-1}{2} M^2\right) + 0.5\right]^{-0.68} $$
$$ \sigma = \left[0.5 \frac{900}{3200} \times 1.105 + 0.5\right]^{-0.68} $$
$$ \sigma = [0.655]^{-0.68} = 1.38 $$

Équation de Bartz au col:
$$ h_g = \frac{0.026}{D_t^{0.2}} \left(\frac{\mu^{0.2} C_p}{Pr^{0.6}}\right) \left(\frac{P_c}{c^*}\right)^{0.8} \left(\frac{D_t}{R_c}\right)^{0.1} \sigma $$

Avec $R_c = 1.5 \times D_t = 0.045 \text{ m}$ (rayon de courbure standard):

$$ h_g = \frac{0.026}{0.030^{0.2}} \frac{(8.2 \times 10^{-5})^{0.2} \times 2100}{0.72^{0.6}} \left(\frac{25 \times 10^5}{1650}\right)^{0.8} \left(\frac{0.030}{0.045}\right)^{0.1} \times 1.38 $$

Calcul terme par terme:
*   $0.026 / 0.030^{0.2} = 0.026 / 0.494 = 0.0527$
*   $(8.2 \times 10^{-5})^{0.2} = 0.0972$
*   $0.72^{0.6} = 0.823$
*   $(25 \times 10^5 / 1650)^{0.8} = (1515)^{0.8} = 405.7$
*   $(0.030/0.045)^{0.1} = 0.667^{0.1} = 0.960$
*   $\sigma = 1.38$

$$ h_g = 0.0527 \times 0.0972 \times \frac{2100}{0.823} \times 405.7 \times 0.960 \times 1.38 $$
$$ h_g = 0.0527 \times 247.5 \times 405.7 \times 0.960 \times 1.38 $$
$$ h_g \approx 7,020 \text{ W/m}^2\cdot\text{K} $$

**ATTENTION:** RÉSULTAT: $h_g$ au col $\approx 7,000 \text{ W/m}^2\cdot\text{K}$


ÉTAPE 2 - CALCUL DU COEFFICIENT $h_c$ (DITTUS-BOELTER)

Propriétés du RP-1 à $T_{film} \approx 350 \text{ K}$ (estimation):
*   $\rho = 780 \text{ kg/m}^3$
*   $\mu = 1.2 \times 10^{-3} \text{ Pa}\cdot\text{s}$
*   $k = 0.11 \text{ W/m}\cdot\text{K}$
*   $C_p = 2100 \text{ J/kg}\cdot\text{K}$
*   $Pr = C_p \mu / k = 2100 \times 1.2 \times 10^{-3} / 0.11 = 22.9$

Nombre de Reynolds:
$$ Re = \frac{\rho v D_h}{\mu} $$
$$ Re = \frac{780 \times 20 \times 0.004}{1.2 \times 10^{-3}} $$
$$ Re = 52,000 $$

**OK:** $Re > 10,000 \rightarrow$ Écoulement turbulent, Dittus-Boelter applicable

Nombre de Nusselt (Dittus-Boelter, chauffage):
$$ Nu = 0.023 Re^{0.8} Pr^{0.4} $$
$$ Nu = 0.023 (52,000)^{0.8} (22.9)^{0.4} $$
$$ Nu = 0.023 \times 5,893 \times 4.05 $$
$$ Nu = 549 $$

Coefficient de transfert:
$$ h_c = \frac{Nu k}{D_h} $$
$$ h_c = \frac{549 \times 0.11}{0.004} $$
$$ h_c = 15,100 \text{ W/m}^2\cdot\text{K} $$

**ATTENTION:** RÉSULTAT: $h_c \approx 15,100 \text{ W/m}^2\cdot\text{K}$


ÉTAPE 3 - CALCUL DU FLUX THERMIQUE ET TEMPÉRATURES

Résistance thermique totale:
$$ R_{total} = \frac{1}{h_g} + \frac{e}{k} + \frac{1}{h_c} $$

$$ R_{gaz} = \frac{1}{7,000} = 1.43 \times 10^{-4} \text{ m}^2\cdot\text{K/W} $$
$$ R_{paroi} = \frac{0.003}{320} = 9.38 \times 10^{-6} \text{ m}^2\cdot\text{K/W} $$
$$ R_{cool} = \frac{1}{15,100} = 6.62 \times 10^{-5} \text{ m}^2\cdot\text{K/W} $$

$$ R_{total} = 1.43 \times 10^{-4} + 9.38 \times 10^{-6} + 6.62 \times 10^{-5} $$
$$ R_{total} = 2.19 \times 10^{-4} \text{ m}^2\cdot\text{K/W} $$

Note: La résistance dominante est $R_{gaz}$ (65% du total)

Flux thermique:
$$ \Delta T = T_{aw} - T_{coolant} = 2912 - 300 = 2612 \text{ K} $$

  q = ΔT / R_total
  q = 2612 / 2.19×10⁻⁴
  q = 11.93×10⁶ W/m²

  **ATTENTION:** RÉSULTAT: q ≈ 12 MW/m²

Distribution des températures:
  T_wall_cold = T_coolant + q / h_c
  T_wall_cold = 300 + 11.93×10⁶ / 15,100
  T_wall_cold = 300 + 790 = 1090 K   (TROP ÉLEVÉ!)

  $$ T_{wall\_hot} = T_{wall\_cold} + \frac{q \times e}{k} $$
  $$ T_{wall\_hot} = 1090 + \frac{11.93 \times 10^6 \times 0.003}{320} $$
  $$ T_{wall\_hot} = 1090 + 112 = 1202 \text{ K} $$


ÉTAPE 4 - ANALYSE ET ITÉRATION

**ATTENTION:** PROBLÈME DÉTECTÉ:
  $T_{wall\_cold} = 1090 \text{ K} \gg T_{limite} (723 \text{ K})$
  La conception actuelle NE FONCTIONNE PAS!

SOLUTIONS POSSIBLES:
  1. Augmenter la vitesse du coolant
  2. Augmenter le débit du coolant
  3. Réduire le diamètre hydraulique
  4. Ajouter du refroidissement par film
  5. Changer de coolant (LH2 beaucoup plus efficace)

ITÉRATION - Augmentation vitesse à 40 m/s:
  $$ Re = \frac{780 \times 40 \times 0.004}{1.2 \times 10^{-3}} = 104,000 $$
  $$ Nu = 0.023 (104,000)^{0.8} (22.9)^{0.4} = 956 $$
  $$ h_c = \frac{956 \times 0.11}{0.004} = 26,300 \text{ W/m}^2\cdot\text{K} $$

  $$ R_{cool} = \frac{1}{26,300} = 3.80 \times 10^{-5} \text{ m}^2\cdot\text{K/W} $$
  $$ R_{total} = 1.43 \times 10^{-4} + 9.38 \times 10^{-6} + 3.80 \times 10^{-5} = 1.90 \times 10^{-4} \text{ m}^2\cdot\text{K/W} $$

  $$ q = \frac{2612}{1.90 \times 10^{-4}} = 13.7 \text{ MW/m}^2 $$

  $$ T_{wall\_cold} = 300 + \frac{13.7 \times 10^6}{26,300} = 821 \text{ K} \quad \text{ (Encore trop!)} $$

ITÉRATION - Avec refroidissement par film (15% fuel):
  Efficacité film: $\eta_{film} \approx 0.60$
  $$ T_{aw\_effective} = T_{coolant} + \eta_{film} (T_{aw} - T_{coolant}) $$
  $$ T_{aw\_effective} = 300 + 0.60 (2912 - 300) = 1867 \text{ K} $$

  $$ q = \frac{1867 - 300}{1.90 \times 10^{-4}} = 8.2 \text{ MW/m}^2 $$

  $$ T_{wall\_cold} = 300 + \frac{8.2 \times 10^6}{26,300} = 612 \text{ K} \quad \text{ OK!} $$
  $$ T_{wall\_hot} = 612 + \frac{8.2 \times 10^6 \times 0.003}{320} = 689 \text{ K} \quad \text{ OK!} $$

  **ATTENTION:** SOLUTION: Vitesse 40 m/s + film cooling 15% $\rightarrow T_{wall} < T_{limite}$


ÉTAPE 5 - CALCUL ÉPAISSEUR CRITIQUE

Avec la configuration finale (v=40 m/s, film 15%):

Épaisseur de fusion:
  $$ e_{melt} = \frac{k (T_{fusion} - T_{wall\_cold})}{q} $$
  $$ e_{melt} = \frac{320 (1350 - 612)}{8.2 \times 10^6} $$
  $$ e_{melt} = \frac{320 \times 738}{8.2 \times 10^6} $$
  $$ e_{melt} = 0.0288 \text{ m} = 28.8 \text{ mm} $$

Épaisseur limite opérationnelle:
  $$ e_{max} = \frac{k (T_{limite} - T_{wall\_cold})}{q} $$
  $$ e_{max} = \frac{320 (723 - 612)}{8.2 \times 10^6} $$
  $$ e_{max} = \frac{320 \times 111}{8.2 \times 10^6} $$
  $$ e_{max} = 0.00433 \text{ m} = 4.33 \text{ mm} $$

  **OK:** Épaisseur 3 mm < $e_{max}$ (4.33 mm) $\rightarrow$ Conception valide

Marge de sécurité sur épaisseur:
  $$ \text{Marge} = \frac{e_{max} - e_{actuelle}}{e_{actuelle}} \times 100 $$
  $$ \text{Marge} = \frac{4.33 - 3}{3} \times 100 = 44\% \quad \text{ Marge acceptable} $$


ÉTAPE 6 - RÉCAPITULATIF CONCEPTION FINALE

| RÉSUMÉ DE LA CONCEPTION VALIDÉE | |
| :--- | :--- |
| Vitesse coolant: | 40 m/s |
| Film cooling: | 15% du débit fuel |
| h_g: | 7,000 W/m²·K |
| h_c: | 26,300 W/m²·K |
| Flux thermique: | 8.2 MW/m² |
| T_wall_hot: | 689 K |
| T_wall_cold: | 612 K |
| Marge vs T_limite: | 34 K (5%) |
| Épaisseur: | 3 mm (marge 44%) |


### 9.2 EXEMPLE 2 : MOTEUR LOX/LH2 HAUTE PERFORMANCE

DONNÉES DU PROBLÈME:

| PARAMÈTRES DE CONCEPTION | |
| :--- | :--- |
| Propergols: | LOX / LH2 |
| Pression chambre: | 100 bar (10 MPa) |
| Rapport O/F: | 6.0 |
| Débit total: | 25 kg/s |
| Diamètre col: | 80 mm |
| Ratio expansion: | 40:1 |
| T chambre: | 3550 K (calculé CEA) |
| γ gaz: | 1.14 |
| M gaz: | 13.5 kg/kmol |
| c*: | 2350 m/s |
| **SYSTÈME DE REFROIDISSEMENT** | |
| Coolant: | LH2 supercritique |
| T entrée coolant: | 40 K |
| Pression coolant: | 150 bar |
| Débit H2: | 3.57 kg/s (mdot_fuel) |
| Dh canal: | 2 mm |
| Nombre canaux: | 200 |
| **PAROI** | |
| Matériau: | NARloy-Z (Cu-Ag-Zr) |
| Conductivité: | 340 W/m·K |
| T limite: | 810 K |
| T fusion: | 1355 K |
| Épaisseur: | 1.5 mm |

ÉTAPE 1 - CALCUL $h_g$ (BARTZ)

  $\mu_{gaz} \approx 7.5 \times 10^{-5} \text{ Pa}\cdot\text{s}$ (à $T_c$)
  $C_{p\_gaz} = 3800 \text{ J/kg}\cdot\text{K}$ (H2O/H2 dominant)
  $Pr = 0.68$

  $\sigma \approx 1.42$ (avec $T_{wall}$ estimée 600 K)

  $$ h_g = \frac{0.026}{0.080^{0.2}} \frac{(7.5 \times 10^{-5})^{0.2} \times 3800}{0.68^{0.6}} \left(\frac{100 \times 10^5}{2350}\right)^{0.8} \sigma $$

  Calcul:
    *   $0.026 / 0.080^{0.2} = 0.026 / 0.574 = 0.0453$
    *   $(7.5 \times 10^{-5})^{0.2} = 0.0948$
    *   $0.68^{0.6} = 0.796$
    *   $(100 \times 10^5 / 2350)^{0.8} = (4255)^{0.8} = 846$

  $$ h_g = 0.0453 \times 0.0948 \times \frac{3800}{0.796} \times 846 \times 1.42 $$

  $$ h_g \approx 24,600 \text{ W/m}^2\cdot\text{K} $$

  Note: Plus élevé que LOX/RP-1 car $P_c$ plus haute et $C_p$ gaz plus élevé


ÉTAPE 2 - CALCUL $h_c$ (LH2 SUPERCRITIQUE)

L'hydrogène supercritique ($P > 13 \text{ bar}$, $T > 33 \text{ K}$) a des propriétés
exceptionnelles mais qui varient fortement avec la température.

Propriétés LH2 à 100 K, 150 bar:
*   $\rho = 45 \text{ kg/m}^3$
*   $\mu = 5.5 \times 10^{-6} \text{ Pa}\cdot\text{s}$
*   $k = 0.12 \text{ W/m}\cdot\text{K}$
*   $C_p = 14,500 \text{ J/kg}\cdot\text{K}$ (pic pseudo-critique)
*   $Pr = 0.67$

Section canal (rectangulaire 2×4 mm):
  $A_{canal} = 8 \text{ mm}^2 = 8 \times 10^{-6} \text{ m}^2$
  Périmètre = 12 mm
  $D_h = 4A/P = 4 \times 8/12 = 2.67 \text{ mm}$

Débit par canal:
  $\dot{m}_{canal} = 3.57 / 200 = 0.0179 \text{ kg/s}$
  $v = \dot{m} / (\rho A) = 0.0179 / (45 \times 8 \times 10^{-6}) = 49.7 \text{ m/s}$

Nombre de Reynolds:
  $$ Re = \frac{\rho v D_h}{\mu} $$
  $$ Re = \frac{45 \times 49.7 \times 0.00267}{5.5 \times 10^{-6}} $$
  $$ Re = 1,086,000 \quad (\text{très turbulent!}) $$

Corrélation Gnielinski (recommandée pour grandes variations Pr):
  $$ f = (0.79 \ln(Re) - 1.64)^{-2} $$
  $$ f = (0.79 \times 13.9 - 1.64)^{-2} = (9.34)^{-2} = 0.0115 $$

  $$ Nu = \frac{(f/8) (Re - 1000) Pr}{1 + 12.7 (f/8)^{0.5} (Pr^{2/3} - 1)} $$
  $$ Nu = \frac{(0.0115/8) (1,085,000) 0.67}{1 + 12.7 (0.0379) (-0.24)} $$
  $$ Nu = \frac{0.00144 \times 727,000}{0.884} $$
  $$ Nu = 1,183 $$

Coefficient de transfert:
  $$ h_c = \frac{Nu k}{D_h} $$
  $$ h_c = \frac{1,183 \times 0.12}{0.00267} $$
  $$ h_c = 53,200 \text{ W/m}^2\cdot\text{K} $$

  **ATTENTION:** RÉSULTAT: $h_c \approx 53,000 \text{ W/m}^2\cdot\text{K}$ (excellent!)


ÉTAPE 3 - FLUX ET TEMPÉRATURES

Résistances thermiques:
  $$ R_{gaz} = \frac{1}{24,600} = 4.07 \times 10^{-5} \text{ m}^2\cdot\text{K/W} $$
  $$ R_{paroi} = \frac{0.0015}{340} = 4.41 \times 10^{-6} \text{ m}^2\cdot\text{K/W} $$
  $$ R_{cool} = \frac{1}{53,200} = 1.88 \times 10^{-5} \text{ m}^2\cdot\text{K/W} $$

  $$ R_{total} = 6.39 \times 10^{-5} \text{ m}^2\cdot\text{K/W} $$

  Note: Distribution plus équilibrée grâce au h_c élevé

T_aw au col:
  r = Pr^0.33 = 0.68^0.33 = 0.88
  T_aw = Tc × [1 + r×(γ-1)/2] = 3550 × [1 + 0.88×0.07] = 3769 K

  (Pour LOX/LH2, T_aw ≈ 0.90 × Tc au col)

Flux thermique:
  ΔT = T_aw - T_bulk = 3769 - 100 = 3669 K

  q = 3669 / 6.39×10⁻⁵ = 57.4 MW/m²

  **ATTENTION:** FLUX TRÈS ÉLEVÉ - typique des moteurs LOX/LH2

Températures paroi:
  $$ T_{wall\_cold} = 100 + \frac{57.4 \times 10^6}{53,200} = 1,179 \text{ K} \quad \text{ (PROBLÈME!)} $$

  La température dépasse la limite (810 K) et même approche la fusion!


ÉTAPE 4 - OPTIMISATION NÉCESSAIRE

Le flux de 57 MW/m² est trop intense. Solutions:

## 1. AUGMENTER LE NOMBRE DE CANAUX:
   $N = 400$ canaux $\rightarrow v = 99 \text{ m/s} \rightarrow Re = 2.17 \times 10^6$
   $Nu = 2,100 \rightarrow h_c = 94,400 \text{ W/m}^2\cdot\text{K}$
   $$ T_{wall\_cold} = 100 + \frac{57.4 \times 10^6}{94,400} = 708 \text{ K} \quad \text{ OK!} $$

## 2. OU RÉDUIRE LE DIAMÈTRE HYDRAULIQUE:
   $D_h = 1.5 \text{ mm} \rightarrow Re$ augmente $\rightarrow h_c$ augmente

## 3. OU AJOUTER FILM COOLING:
   Film H2 5% $\rightarrow$ efficacité 0.40
   $$ T_{aw\_eff} = 100 + 0.40 (3769 - 100) = 1568 \text{ K} $$
   $$ q = \frac{1568 - 100}{6.39 \times 10^{-5}} = 23.0 \text{ MW/m}^2 $$
   $$ T_{wall\_cold} = 100 + \frac{23.0 \times 10^6}{53,200} = 533 \text{ K} \quad \text{OK} $$

CONCEPTION FINALE RETENUE: 400 canaux

| RÉSUMÉ LOX/LH2 | |
| :--- | :--- |
| h_g: | 24,600 W/m²·K |
| h_c: | 94,400 W/m²·K |
| Flux thermique: | 50.2 MW/m² (avec 400 canaux) |
| T_wall_cold: | 632 K |
| T_wall_hot: | 854 K |
| Marge vs T_limite: | -44 K (besoin film cooling) |
| **AVEC FILM COOLING 3%:** | |
| Flux effectif: | 32 MW/m² |
| T_wall_hot: | 615 K (OK) |


### 9.3 EXEMPLE 3 : MOTEUR LOX/CH4 (NOUVELLE GÉNÉRATION)

Le méthane est un compromis entre RP-1 et LH2, offrant de bonnes
propriétés de refroidissement sans les contraintes cryogéniques extrêmes.

DONNÉES:

| DONNÉES | |
| :--- | :--- |
| Propergols: | LOX / LCH4 |
| Pression chambre: | 80 bar |
| Rapport O/F: | 3.6 |
| Diamètre col: | 150 mm |
| T chambre: | 3450 K |
| Coolant: | LCH4 supercritique (120 K, 100 bar) |
| Matériau: | C-103 (Nb alloy, k=42 W/m·K) |
| Épaisseur: | 2 mm |

CALCULS RAPIDES:

$h_g$ (Bartz):
  $h_g \approx 18,500 \text{ W/m}^2\cdot\text{K}$ (estimé avec corrélation)

$h_c$ (CH4 supercritique à 150 K):
  Propriétés CH4: $\rho=200 \text{ kg/m}^3$, $\mu=30 \times 10^{-6} \text{ Pa}\cdot\text{s}$, $k=0.15 \text{ W/m}\cdot\text{K}$, $C_p=4000 \text{ J/kg}\cdot\text{K}$
  Avec $v=30 \text{ m/s}$, $D_h=3 \text{ mm}$:
  $$ Re = \frac{200 \times 30 \times 0.003}{30 \times 10^{-6}} = 600,000 $$
  $Nu = 1,850$ (Gnielinski)
  $$ h_c = \frac{1,850 \times 0.15}{0.003} = 92,500 \text{ W/m}^2\cdot\text{K} $$

Flux et températures:
  $$ R_{total} = \frac{1}{18,500} + \frac{0.002}{42} + \frac{1}{92,500} = 1.12 \times 10^{-4} \text{ m}^2\cdot\text{K/W} $$
  $$ T_{aw} \approx 0.92 \times 3450 = 3174 \text{ K} $$
  $$ q = \frac{3174 - 150}{1.12 \times 10^{-4}} = 27.0 \text{ MW/m}^2 $$

  $$ T_{wall\_cold} = 150 + \frac{27.0 \times 10^6}{92,500} = 442 \text{ K} $$
  $$ T_{wall\_hot} = 442 + \frac{27.0 \times 10^6 \times 0.002}{42} = 1,728 \text{ K} \quad \text{(Trop chaud)} $$

  **ATTENTION:** Le niobium ($T_{fusion} = 2750 \text{ K}$) supporte cette température, mais
     la durée de vie serait limitée. Une liner en cuivre serait préférable.

SOLUTION: Liner CuCrZr + coque Nb
  Liner 0.8 mm CuCrZr ($k=320$) + coque 2 mm Nb
  $$ R_{total} = \frac{1}{18,500} + \frac{0.0008}{320} + \frac{0.002}{42} + \frac{1}{92,500} = 1.14 \times 10^{-4} $$
  $$ T_{wall\_hot} = 150 + 27 \times 10^6 \times \left(\frac{1}{92,500} + \frac{0.0008}{320}\right) = 511 \text{ K} \quad \text{OK} $$


### 9.4 EXEMPLE 4 : DIMENSIONNEMENT CANAUX DE REFROIDISSEMENT

Cet exemple montre comment dimensionner les canaux pour atteindre
un $h_c$ cible avec un $\Delta p$ acceptable.

OBJECTIF:
  Atteindre $h_c = 50,000 \text{ W/m}^2\cdot\text{K}$ avec RP-1
  Contrainte: $\Delta p < 10 \text{ bar}$ sur 200 mm de longueur

DONNÉES:
*   Coolant: RP-1 @ 350 K
*   $\rho = 750 \text{ kg/m}^3$, $\mu = 8 \times 10^{-4} \text{ Pa}\cdot\text{s}$, $k = 0.10 \text{ W/m}\cdot\text{K}$, $Pr = 17$
*   Débit disponible: 2 kg/s
*   Circonférence col: $\pi \times 0.050 = 0.157 \text{ m}$

MÉTHODE DE RÉSOLUTION:

## 1. Déterminer Nu nécessaire:
   $$ h_c = \frac{Nu k}{D_h} $$
   $$ 50,000 = \frac{Nu \times 0.10}{D_h} $$
   $$ Nu D_h = 5000 \quad \dots (\text{Eq. 1}) $$

## 2. Exprimer Nu en fonction de Re (Dittus-Boelter):
   $$ Nu = 0.023 Re^{0.8} 17^{0.4} = 0.023 Re^{0.8} \times 3.65 $$
   $$ Nu = 0.084 Re^{0.8} \quad \dots (\text{Eq. 2}) $$

## 3. Exprimer Re en fonction de Dh:
   Soit $N$ canaux de largeur $w$ et profondeur $d$
   $$ D_h = \frac{4wd}{2w + 2d} $$

   Pour $w = 2d$: $D_h = 4 \times 2d^2 / 6d = 1.33d$

   Débit par canal: $\dot{m}_c = 2/N$
   Vitesse: $v = \dot{m}_c / (\rho w d) = 2 / (N \times 750 \times 2d^2)$

   $$ Re = \frac{750 v D_h}{8 \times 10^{-4}} $$

## 4. Itération:
   Essai $N = 80$, $d = 1.5 \text{ mm}$, $w = 3 \text{ mm}$:
   $D_h = 4 \times 3 \times 1.5 / 9 = 2 \text{ mm}$
   $A_{canal} = 4.5 \text{ mm}^2$
   $v = 2 / (80 \times 750 \times 4.5 \times 10^{-6}) = 7.4 \text{ m/s}$
   $Re = 750 \times 7.4 \times 0.002 / 8 \times 10^{-4} = 13,900$
   $Nu = 0.084 \times 13,900^{0.8} = 213$
   $h_c = 213 \times 0.10 / 0.002 = 10,650 \text{ W/m}^2\cdot\text{K} \quad \text{ (Trop bas!)}$

   Essai $N = 120$, $d = 1 \text{ mm}$, $w = 2 \text{ mm}$:
   $D_h = 4 \times 2 \times 1 / 6 = 1.33 \text{ mm}$
   $A_{canal} = 2 \text{ mm}^2$
   $v = 2 / (120 \times 750 \times 2 \times 10^{-6}) = 11.1 \text{ m/s}$
   $Re = 750 \times 11.1 \times 0.00133 / 8 \times 10^{-4} = 13,850$
   $Nu = 0.084 \times 13,850^{0.8} = 212$
   $h_c = 212 \times 0.10 / 0.00133 = 15,940 \text{ W/m}^2\cdot\text{K} \quad \text{ (Encore trop bas)}$

   Essai $N = 150$, $d = 0.8 \text{ mm}$, $w = 1.6 \text{ mm}$ (canaux fins):
   $D_h = 4 \times 1.6 \times 0.8 / 4.8 = 1.07 \text{ mm}$
   $v = 2 / (150 \times 750 \times 1.28 \times 10^{-6}) = 13.9 \text{ m/s}$
   $Re = 750 \times 13.9 \times 0.00107 / 8 \times 10^{-4} = 13,940$
   $h_c = 14,000 \text{ W/m}^2\cdot\text{K} \quad \text{(Insuffisant)}$

   PROBLÈME: avec RP-1, difficile d'atteindre $h_c > 30,000 \text{ W/m}^2\cdot\text{K}$
   sans pertes de charge excessives.

## 5. Vérification perte de charge:
   $$ f = 0.316 / Re^{0.25} = 0.316 / 13,940^{0.25} = 0.029 $$
   $$ \Delta p = f \frac{L}{D_h} \frac{\rho v^2}{2} $$
   $$ \Delta p = 0.029 \times \frac{0.2}{0.00107} \times \frac{750 \times 13.9^2}{2} $$
   $$ \Delta p = 5.42 \times 72,560 = 3.93 \text{ bar} \quad \text{ OK} $$

CONCLUSION:
  $h_{c\_max}$ réaliste avec RP-1 $\approx 25,000 \text{ W/m}^2\cdot\text{K}$
  Pour $h_c = 50,000 \text{ W/m}^2\cdot\text{K}$, utiliser LH2 ou LCH4


### 9.5 EXEMPLE 5 : CALCUL ÉLÉVATION TEMPÉRATURE COOLANT

Vérifier que le coolant ne surchauffe pas en traversant les canaux.

DONNÉES:
*   $Q_{total} = 850 \text{ kW}$ (puissance thermique totale)
*   Coolant: RP-1
*   Débit: 2 kg/s
*   $C_p = 2100 \text{ J/kg}\cdot\text{K}$
*   $T_{entrée} = 300 \text{ K}$
*   $T_{ébullition} = 490 \text{ K}$ à 30 bar

CALCUL:
  $$ \Delta T_{coolant} = \frac{Q_{total}}{\dot{m} C_p} $$
  $$ \Delta T_{coolant} = \frac{850,000}{2 \times 2100} $$
  $$ \Delta T_{coolant} = 202 \text{ K} $$

  $$ T_{sortie} = 300 + 202 = 502 \text{ K} \quad **ATTENTION:** > T_{ébullition}! $$

PROBLÈME: Le RP-1 risque de bouillir et former des dépôts (coking)

SOLUTIONS:
  1. Augmenter le débit coolant (si possible)
  2. Augmenter la pression coolant pour élever $T_{ébullition}$
  3. Utiliser du refroidissement par film pour réduire $Q_{total}$
  4. Multi-pass cooling (entrée au col, zones froides vers chambre)

AVEC FILM COOLING 20%:
  $Q_{effectif} = 0.65 \times 850 = 552 \text{ kW}$ (réduction typique avec film)
  $$ \Delta T_{coolant} = \frac{552,000}{2 \times 2100} = 132 \text{ K} $$
  $$ T_{sortie} = 300 + 132 = 432 \text{ K} \quad < T_{ébullition} $$


### 9.6 EXEMPLE 6 : ANALYSE DIMENSIONNELLE RAPIDE
───────────────────────────────────────────────────────────────

Méthode simplifiée pour estimation préliminaire.

RÈGLES EMPIRIQUES (moteurs conventionnels):

| ESTIMATIONS RAPIDES | |
| :--- | :--- |
| $h_g$ au col | $\approx 5000 \times (P_c/20)^{0.8} \times (30/D_t)^{0.8} \text{ W/m}^2\cdot\text{K}$ |
| | où $P_c$ en bar, $D_t$ en mm |
| $q_{col}$ | $\approx 0.4 \times h_g \times T_c \text{ (en W/m}^2\text{)}$ |
| | approximation avec $T_{wall}$ typique |
| $Q_{total}$ | $\approx q_{col} \times 0.3 \times A_{totale}$ |
| | car flux moyen $\approx 30\%$ du flux au col |
| $\Delta T_{coolant}$ | $\approx Q_{total} / (\dot{m}_{fuel} \times C_{p\_fuel})$ |

EXEMPLE RAPIDE:
  $P_c = 50 \text{ bar}$, $D_t = 60 \text{ mm}$, $T_c = 3400 \text{ K}$, LOX/RP-1

  $$ h_g \approx 5000 \times (50/20)^{0.8} \times (30/60)^{0.8} $$
  $$ h_g \approx 5000 \times 2.0 \times 0.57 = 5,700 \text{ W/m}^2\cdot\text{K} $$

  $$ q_{col} \approx 0.4 \times 5700 \times 3400 = 7.8 \text{ MW/m}^2 $$

  Cette estimation est généralement à ±30% de la valeur réelle.


### 9.7 TABLEAU RÉCAPITULATIF DES EXEMPLES

| Exemple | Pc (bar) | Dt (mm) | q (MW/m²) | h_g | Solution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| LOX/RP-1 | 25 | 30 | 8.2 | 7,000 | Film 15% + v↑ |
| LOX/LH2 | 100 | 80 | 32 | 24,600 | 400 can + film |
| LOX/CH4 | 80 | 150 | 27 | 18,500 | Liner Cu + Nb |

TENDANCES OBSERVÉES:
  *   $q$ augmente avec $P_c$ (quasi-linéairement)
  *   $h_g$ augmente quand $D_t$ diminue
  *   LOX/LH2 requiert le refroidissement le plus intense
  *   Le film cooling est souvent nécessaire pour $P_c > 50 \text{ bar}$


### 9.8 EXERCICES D'APPLICATION
───────────────────────────────────────────────────────────────

EXERCICE 1 - Calcul basique:
  Un moteur LOX/Ethanol a: Pc=15 bar, Dt=25 mm, Tc=3000 K
  Calculer h_g au col avec l'équation de Bartz.
  (Réponse: ≈ 4,800 W/m²·K)

EXERCICE 2 - Dimensionnement coolant:
  Avec q=5 MW/m² et h_c requis=20,000 W/m²·K
  Quelle élévation de température paroi côté froid?
  (Réponse: ΔT = q/h_c = 250 K)

EXERCICE 3 - Épaisseur critique:
  Paroi cuivre ($k=360 \text{ W/m}\cdot\text{K}$), $T_{limite}=700 \text{ K}$, $T_{cold}=400 \text{ K}$
  Flux $q=15 \text{ MW/m}^2$. Quelle épaisseur maximale?
  (Réponse: $e_{max} = k \times \Delta T/q = 7.2 \text{ mm}$)

EXERCICE 4 - Puissance thermique:
  Moteur 5 kN de poussée, $I_{sp}=280\text{s}$, $T_c=3200 \text{ K}$
  Estimer la puissance thermique à évacuer.
  (Réponse: $Q \approx 0.5-1 \text{ MW}$, selon géométrie et flux)


## 22. FORMULES RAPIDES (AIDE-MÉMOIRE COMPLET)

Cette section rassemble toutes les formules essentielles pour la conception thermique des moteurs-fusées, organisées par thème.


### 22.1 ÉQUATIONS FONDAMENTALES DU TRANSFERT THERMIQUE

**FLUX THERMIQUE (LOI DE FOURIER):**

$$ q = -k \frac{dT}{dx} \quad [\text{W/m}^2] $$

Pour une paroi plane:
$$ q = k \frac{T_1 - T_2}{e} \quad [\text{W/m}^2] $$

où:
*   $k$ = conductivité thermique [W/m·K]
*   $e$ = épaisseur [m]
*   $T_1, T_2$ = températures aux faces [K]

**CONVECTION (LOI DE NEWTON):**

$$ q = h (T_{fluide} - T_{paroi}) \quad [\text{W/m}^2] $$

où:
*   $h$ = coefficient de convection [W/m²·K]
*   $T_{fluide}$ = température du fluide [K]
*   $T_{paroi}$ = température de la paroi [K]

**RÉSISTANCES THERMIQUES EN SÉRIE:**

$$ R_{total} = R_{gaz} + R_{paroi} + R_{coolant} $$

$$ R_{gaz} = \frac{1}{h_g} \quad [\text{m}^2\cdot\text{K/W}] $$
$$ R_{paroi} = \frac{e}{k} \quad [\text{m}^2\cdot\text{K/W}] $$
$$ R_{coolant} = \frac{1}{h_c} \quad [\text{m}^2\cdot\text{K/W}] $$

Flux:
$$ q = \frac{\Delta T_{total}}{R_{total}} $$

**COEFFICIENT GLOBAL DE TRANSFERT:**

$$ U = \frac{1}{R_{total}} = \frac{1}{1/h_g + e/k + 1/h_c} $$

$$ q = U (T_{gaz} - T_{coolant}) $$


### 10.2 ÉQUATION DE BARTZ (CÔTÉ GAZ CHAUD)

**FORME COMPLÈTE:**

$$ h_g = \sigma \times \frac{0.026}{D_t^{0.2}} \times \frac{\mu^{0.2} C_p}{Pr^{0.6}} \times \left(\frac{P_c}{c^*}\right)^{0.8} \times \left(\frac{D_t}{R_c}\right)^{0.1} \times \left(\frac{A_t}{A}\right)^{0.9} $$

**FACTEUR DE CORRECTION $\sigma$:**

$$ \sigma = \left[\frac{1}{2}\frac{T_w}{T_c}\left(1 + \frac{\gamma-1}{2} M^2\right) + \frac{1}{2}\right]^{-0.68} \times \left[1 + \frac{\gamma-1}{2} M^2\right]^{-0.12} $$

Approximation au col ($M=1$):
$$ \sigma \approx \left[0.5 \frac{T_w}{T_c} \frac{\gamma+1}{2} + 0.5\right]^{-0.68} $$

**FORME SIMPLIFIÉE AU COL:**

$$ h_{g,throat} = C \times \frac{P_c^{0.8}}{D_t^{1.8}} \times \sigma $$

où $C$ dépend des propriétés du gaz.

Estimation rapide:
$$ h_g \approx 5000 \times \left(\frac{P_c}{20}\right)^{0.8} \times \left(\frac{30}{D_{t,mm}}\right)^{1.8} \quad [\text{W/m}^2\cdot\text{K}] $$

**VARIATION LE LONG DE LA TUYÈRE:**

$$ h_g(x) = h_{g,throat} \times \left(\frac{D_t}{D(x)}\right)^{1.8} $$

*   Au col: $h_g = h_{g,throat}$ (maximum)
*   Chambre: $h_g \approx 0.3 \times h_{g,throat}$
*   Sortie: $h_g \approx 0.05 \times h_{g,throat}$


### 10.3 NOMBRES ADIMENSIONNELS

**NOMBRE DE REYNOLDS:**

$$ Re = \frac{\rho v D_h}{\mu} = \frac{v D_h}{\nu} $$

où:
*   $\rho$ = masse volumique [kg/m³]
*   $v$ = vitesse [m/s]
*   $D_h$ = diamètre hydraulique [m]
*   $\mu$ = viscosité dynamique [Pa·s]
*   $\nu$ = viscosité cinématique [m²/s]

Régimes:
*   $Re < 2300$: Laminaire
*   $2300 < Re < 10^4$: Transition
*   $Re > 10^4$: Turbulent

**NOMBRE DE PRANDTL:**

$$ Pr = \frac{\mu C_p}{k} = \frac{\nu}{\alpha} $$

où:
*   $C_p$ = capacité thermique [J/kg·K]
*   $k$ = conductivité thermique [W/m·K]
*   $\alpha$ = diffusivité thermique [m²/s]

Valeurs typiques:
*   Gaz combustion: $Pr \approx 0.7-0.8$
*   Eau: $Pr \approx 7$ (à 20°C)
*   RP-1: $Pr \approx 15-25$
*   LH2: $Pr \approx 0.7-1.5$
*   Huiles: $Pr \approx 100-1000$

**NOMBRE DE NUSSELT:**

$$ Nu = \frac{h D_h}{k} $$

Interprétation: $Nu = \text{transfert convectif} / \text{conductif}$

Pour obtenir $h$:
$$ h = Nu \frac{k}{D_h} \quad [\text{W/m}^2\cdot\text{K}] $$

**DIAMÈTRE HYDRAULIQUE:**

$$ D_h = \frac{4 A}{P} $$
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


### 10.4 CORRÉLATIONS DE CONVECTION FORCÉE
───────────────────────────────────────────────────────────────

**DITTUS-BOELTER (turbulent, fluides simples):**

$$ Nu = 0.023 Re^{0.8} Pr^n $$

*   $n = 0.4$ (chauffage du fluide)
*   $n = 0.3$ (refroidissement du fluide)

Validité:
*   $Re > 10,000$
*   $0.6 < Pr < 160$
*   $L/D > 10$

**SIEDER-TATE (correction viscosité):**

$$ Nu = 0.027 Re^{0.8} Pr^{1/3} \left(\frac{\mu_{bulk}}{\mu_{wall}}\right)^{0.14} $$

Recommandé quand:
*   $T_{wall} \gg T_{bulk}$ (grande variation de $\mu$)

**GNIELINSKI (transition + turbulent):**

$$ Nu = \frac{(f/8)(Re - 1000)Pr}{1 + 12.7(f/8)^{0.5}(Pr^{2/3} - 1)} $$

avec $f = (0.79 \ln(Re) - 1.64)^{-2}$

Validité:
*   $2300 < Re < 5 \times 10^6$
*   $0.5 < Pr < 2000$

**PETUKHOV (haute précision, turbulent):**

$$ Nu = \frac{(f/8) Re Pr}{1.07 + 12.7(f/8)^{0.5}(Pr^{2/3} - 1)} $$

avec $f = (0.790 \ln(Re) - 1.64)^{-2}$

Précision: $\pm 5\%$ pour $10^4 < Re < 5 \times 10^6$

**LAMINAIRE ($Re < 2300$):**

*   Tube long, $T_{wall}$ constante:
    $$ Nu = 3.66 $$

*   Tube long, flux constant:
    $$ Nu = 4.36 $$

*   Tube court (développement thermique):
    $$ Nu = 1.86 \left(Re Pr \frac{D}{L}\right)^{1/3} \left(\frac{\mu_b}{\mu_w}\right)^{0.14} $$


### 10.5 ÉQUATIONS DE TEMPÉRATURE DE PAROI

**PROFIL DE TEMPÉRATURE À TRAVERS LA PAROI:**

$$ T_{gaz} \overset{h_g}{\longrightarrow} T_{wall,hot} \overset{k/e}{\longrightarrow} T_{wall,cold} \overset{h_c}{\longrightarrow} T_{coolant} $$

$$ T_{wall,hot} = T_{gaz} - \frac{q}{h_g} $$

$$ T_{wall,cold} = T_{wall,hot} - \frac{qe}{k} = T_{coolant} + \frac{q}{h_c} $$

Vérification:
$$ T_{wall,hot} = T_{coolant} + q \left(\frac{1}{h_c} + \frac{e}{k}\right) $$

**TEMPÉRATURE ADIABATIQUE DE PAROI ($T_{aw}$):**

$$ T_{aw} = T_{statique} \left[1 + r \frac{\gamma-1}{2} M^2\right] $$

Facteur de récupération $r$:
*   $r = Pr^{1/2}$ pour laminaire
*   $r = Pr^{1/3}$ pour turbulent

Au col ($M=1$):
$$ T_{aw} \approx 0.90 T_c \quad \text{(gaz combustion typique)} $$

**TEMPÉRATURE CRITIQUE DE PAROI:**

Marge thermique:
$$ \text{Marge} = T_{limite} - T_{wall,hot} $$

Condition de sécurité:
$$ T_{wall,hot} < T_{limite} \quad \text{(typiquement 20\% de marge)} $$

Limite absolue:
$$ T_{wall,hot} \ll T_{fusion} \quad \text{(facteur 1.5 minimum)} $$


### 10.6 ÉPAISSEUR DE PAROI

**ÉPAISSEUR MAXIMALE (critère thermique):**

$$ e_{max} = \frac{k (T_{limite} - T_{wall,cold})}{q} $$

Si $e > e_{max}$: $T_{wall,hot} > T_{limite} \rightarrow$ Défaillance!

**ÉPAISSEUR DE FUSION:**

$$ e_{melt} = \frac{k (T_{fusion} - T_{wall,cold})}{q} $$

Si $e > e_{melt}$: La paroi fond côté gaz!

**ÉPAISSEUR SACRIFICIELLE:**

$$ e_{sacrif} = e_{initial} - e_{melt} $$

Épaisseur de matériau qui peut fondre sans compromettre l'intégrité structurelle.

Condition: $e_{sacrif} > 0$ et $e_{restante} > e_{min,struct}$

**ÉPAISSEUR MINIMALE (critère mécanique):**

$$ e_{min} = \frac{P_c r}{\sigma_{admissible}} $$

où:
*   $P_c$ = pression chambre [Pa]
*   $r$ = rayon local [m]
*   $\sigma_{admissible}$ = contrainte admissible à $T$ [Pa]

Note: $\sigma_{admissible}$ diminue avec $T$!


### 10.7 PUISSANCE ET ÉNERGIE THERMIQUE

**PUISSANCE THERMIQUE TOTALE:**

$$ Q_{total} = \int q(x) dA $$

Approximation:
$$ Q_{total} \approx q_{moyen} A_{totale} $$

où: $q_{moyen} \approx 0.3 q_{col}$ (valeur typique)

**ÉLÉVATION DE TEMPÉRATURE DU COOLANT:**
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


### 10.8 PERTES DE CHARGE
───────────────────────────────────────────────────────────────

**ÉQUATION DE DARCY-WEISBACH:**

$$ \Delta p = f \frac{L}{D_h} \frac{\rho v^2}{2} $$

où:
*   $f$ = facteur de friction
*   $L$ = longueur du canal [m]
*   $D_h$ = diamètre hydraulique [m]

**FACTEUR DE FRICTION:**

*   Laminaire ($Re < 2300$):
    $$ f = \frac{64}{Re} $$

*   Turbulent lisse (Blasius, $Re < 10^5$):
    $$ f = \frac{0.316}{Re^{0.25}} $$

*   Turbulent (Petukhov, $Re > 3000$):
    $$ f = (0.790 \ln(Re) - 1.64)^{-2} $$

*   Avec rugosité (Colebrook-White):
    $$ \frac{1}{\sqrt{f}} = -2 \log_{10}\left(\frac{\varepsilon}{3.7D} + \frac{2.51}{Re\sqrt{f}}\right) $$

**PUISSANCE DE POMPAGE:**

$$ P_{pompe} = \frac{\Delta p Q_{volumique}}{\eta_{pompe}} = \frac{\Delta p \dot{m}}{\rho \eta_{pompe}} $$

où:
*   $Q_{volumique}$ = débit volumique [m³/s]
*   $\eta_{pompe}$ = rendement de la pompe


### 10.9 FILM COOLING

**EFFICACITÉ DU FILM:**

$$ \eta_{film} = \frac{T_{aw} - T_{aw,film}}{T_{aw} - T_{coolant}} $$

où:
*   $T_{aw,film}$ = température adiabatique avec film
*   $T_{coolant}$ = température du film injecté

$$ T_{aw,effective} = T_{coolant} + \eta_{film} (T_{aw} - T_{coolant}) $$

**DÉBIT DE FILM:**

Règle empirique:
*   $\dot{m}_{film} = 2-5\%$ du débit fuel pour protection locale
*   $\dot{m}_{film} = 10-20\%$ pour protection chambre complète

Efficacité typique:
*   $\eta_{film} \approx 0.3 - 0.6$ selon injection et géométrie

**RÉDUCTION DE FLUX EFFECTIVE:**

$$ q_{avec\_film} = h_g (T_{aw,effective} - T_{wall,hot}) $$

Réduction typique: 30-60% du flux sans film


### 10.10 PROPRIÉTÉS DES GAZ DE COMBUSTION

**ESTIMATION DES PROPRIÉTÉS:**

Viscosité dynamique (loi de Sutherland):
$$ \mu = \mu_0 \left(\frac{T}{T_0}\right)^{1.5} \frac{T_0 + S}{T + S} $$

Pour gaz de combustion (approximation):
$$ \mu \approx 3 \times 10^{-7} T^{0.7} \quad [\text{Pa}\cdot\text{s}] $$

Conductivité thermique:
$$ k = \frac{C_p \mu}{Pr} $$
$$ k \approx \frac{C_p \mu}{0.72} \quad [\text{W/m}\cdot\text{K}] $$

$C_p$ (J/kg·K) typique:
*   LOX/RP-1: 2000-2200
*   LOX/LH2:  3500-4000
*   LOX/CH4:  2400-2800


### 10.11 TABLEAU RÉCAPITULATIF DES FORMULES

| GRANDEUR | FORMULE |
| :--- | :--- |
| Flux thermique | $q = \Delta T / R_{total}$ |
| Résistance totale | $R = 1/h_g + e/k + 1/h_c$ |
| Coefficient global | $U = 1/R_{total}$ |
| T paroi chaude | $T_{hot} = T_{gaz} - q/h_g$ |
| T paroi froide | $T_{cold} = T_{coolant} + q/h_c$ |
| Gradient dans paroi | $\Delta T_{paroi} = q \times e / k$ |
| Reynolds | $Re = \rho v D_h / \mu$ |
| Prandtl | $Pr = \mu C_p / k$ |
| Nusselt (Dittus-Boelter) | $Nu = 0.023 Re^{0.8} Pr^{0.4}$ |
| h depuis Nu | $h = Nu k / D_h$ |
| Diamètre hydraulique | $D_h = 4 A / P$ |
| Épaisseur max thermique | $e_{max} = k(T_{lim} - T_{cold}) / q$ |
| Épaisseur fusion | $e_{melt} = k(T_{fus} - T_{cold}) / q$ |
| Épaisseur min mécanique | $e_{min} = P r / \sigma_{adm}$ |
| Puissance thermique | $Q = \int q dA \approx q_{moy} \times A$ |
| $\Delta T$ coolant | $\Delta T = Q / (\dot{m} C_p)$ |
| Perte de charge | $\Delta p = f (L/D_h) \rho v^2/2$ |


### 10.12 ORDRES DE GRANDEUR TYPIQUES

**FLUX THERMIQUE AU COL:**

*   Moteur amateur ($P_c < 10 \text{ bar}$): $1 - 5 \text{ MW/m}^2$
*   Petit moteur ($P_c \sim 20-50 \text{ bar}$): $5 - 20 \text{ MW/m}^2$
*   Moteur orbital ($P_c \sim 50-100 \text{ bar}$): $15 - 50 \text{ MW/m}^2$
*   Moteur haute $P_c$ ($> 150 \text{ bar}$): $30 - 80 \text{ MW/m}^2$
*   Record (SSME au col): $130 \text{ MW/m}^2$

**COEFFICIENTS DE TRANSFERT:**

*   $h_g$ au col:
    *   $P_c = 20 \text{ bar}$: $3,000 - 8,000 \text{ W/m}^2\cdot\text{K}$
    *   $P_c = 50 \text{ bar}$: $8,000 - 20,000 \text{ W/m}^2\cdot\text{K}$
    *   $P_c = 100 \text{ bar}$: $15,000 - 40,000 \text{ W/m}^2\cdot\text{K}$
    *   $P_c = 200 \text{ bar}$: $30,000 - 80,000 \text{ W/m}^2\cdot\text{K}$

*   $h_c$ (coolant):
    *   RP-1: $5,000 - 30,000 \text{ W/m}^2\cdot\text{K}$
    *   LCH4: $20,000 - 80,000 \text{ W/m}^2\cdot\text{K}$
    *   LH2: $50,000 - 200,000 \text{ W/m}^2\cdot\text{K}$
    *   Eau: $5,000 - 50,000 \text{ W/m}^2\cdot\text{K}$

**TEMPÉRATURES:**

*   T chambre:
    *   LOX/RP-1: $3200 - 3500 \text{ K}$
    *   LOX/LH2: $3400 - 3600 \text{ K}$
    *   LOX/CH4: $3300 - 3500 \text{ K}$
    *   N2O4/UDMH: $3000 - 3200 \text{ K}$

*   T paroi hot typique:
    *   Cuivre allié: $500 - 800 \text{ K}$
    *   Ni superalliage: $800 - 1100 \text{ K}$
    *   Réfractaires: $1200 - 2000 \text{ K}$

**GÉOMÉTRIE:**

*   Épaisseur paroi: $0.5 - 10 \text{ mm}$
*   Largeur canal: $1 - 5 \text{ mm}$
*   Profondeur canal: $1 - 10 \text{ mm}$
*   Nombre canaux: $20 - 500$
*   Vitesse coolant: $5 - 50 \text{ m/s}$
*   $\Delta p$ canaux: $2 - 20 \text{ bar}$


### 10.13 CONVERSIONS UTILES

| TEMPÉRATURE | |
| :--- | :--- |
| $K = °C + 273.15$ | |
| $°C = (°F - 32) \times 5/9$ | |
| $K = (°F + 459.67) \times 5/9$ | |

| PRESSION | |
| :--- | :--- |
| $1 \text{ bar} = 100,000 \text{ Pa} = 0.1 \text{ MPa}$ | |
| $1 \text{ bar} = 14.504 \text{ psi}$ | |
| $1 \text{ atm} = 101,325 \text{ Pa} = 1.01325 \text{ bar}$ | |

| ÉNERGIE / PUISSANCE | |
| :--- | :--- |
| $1 \text{ MW} = 10^6 \text{ W}$ | |
| $1 \text{ kW} = 1.341 \text{ hp}$ | |
| $1 \text{ BTU/s} = 1055 \text{ W}$ | |

| FLUX THERMIQUE | |
| :--- | :--- |
| $1 \text{ MW/m}^2 = 10^6 \text{ W/m}^2$ | |
| $1 \text{ BTU/(h}\cdot\text{ft}^2) = 3.155 \text{ W/m}^2$ | |

| COEFFICIENT DE TRANSFERT | |
| :--- | :--- |
| $1 \text{ W/(m}^2\cdot\text{K)} = 0.1761 \text{ BTU/(h}\cdot\text{ft}^2\cdot\text{°F)}$ | |
| $1 \text{ BTU/(h}\cdot\text{ft}^2\cdot\text{°F)} = 5.678 \text{ W/(m}^2\cdot\text{K)}$ | |

| CONDUCTIVITÉ THERMIQUE | |
| :--- | :--- |
| $1 \text{ W/(m}\cdot\text{K)} = 0.5778 \text{ BTU/(h}\cdot\text{ft}\cdot\text{°F)}$ | |


### 10.14 CONSTANTES PHYSIQUES

*   Constante des gaz parfaits:
    $R = 8.314 \text{ J/(mol}\cdot\text{K)}$

*   Constante de Stefan-Boltzmann:
    $\sigma = 5.67 \times 10^{-8} \text{ W/(m}^2\cdot\text{K}^4)$

*   Nombre d'Avogadro:
    $N_A = 6.022 \times 10^{23} \text{ mol}^{-1}$

*   Accélération gravitationnelle:
    $g_0 = 9.80665 \text{ m/s}^2$


## RÉFÉRENCES BIBLIOGRAPHIQUES

**OUVRAGES DE RÉFÉRENCE:**

*   Sutton & Biblarz - "Rocket Propulsion Elements" (9th ed., 2016) - Référence principale
*   Humble, Henry & Larson - "Space Propulsion Analysis and Design" (1995) - Conception détaillée
*   Huzel & Huang - "Modern Engineering for Design of Liquid-Propellant Rocket Engines" (1992)
*   Hill & Peterson - "Mechanics and Thermodynamics of Propulsion" (1992)

**PUBLICATIONS TECHNIQUES:**

*   Bartz, D.R. (1957) - "A Simple Equation for Rapid Estimation of Rocket Nozzle Convective Heat Transfer Coefficients" - Jet Propulsion, Vol. 27, No. 1
*   Dittus, F.W. & Boelter, L.M.K. (1930) - "Heat Transfer in Automobile Radiators of the Tubular Type" University of California Publications, Vol. 2
*   Gnielinski, V. (1976) - "New Equations for Heat and Mass Transfer in Turbulent Pipe and Channel Flow" Int. Chem. Eng., Vol. 16, No. 2
*   Sieder, E.N. & Tate, G.E. (1936) - "Heat Transfer and Pressure Drop of Liquids in Tubes" Industrial & Engineering Chemistry, Vol. 28

**DOCUMENTS NASA:**

*   NASA SP-125 - "Design of Liquid Propellant Rocket Engines" (Huzel & Huang, 1967)
*   NASA SP-8014 - "Entry Thermal Protection" (1968)
*   NASA TM-X-52386 - "Regenerative Cooling of Rocket Engines" (1967)
*   NASA CR-134806 - "High Pressure LOX/Hydrogen Regenerative Cooling" (1975)

**LOGICIELS ET BASES DE DONNÉES:**

*   CEA (Chemical Equilibrium with Applications) NASA Glenn Research Center [https://www.grc.nasa.gov/WWW/CEAWeb/](https://www.grc.nasa.gov/WWW/CEAWeb/)
*   NIST Chemistry WebBook [https://webbook.nist.gov/chemistry/](https://webbook.nist.gov/chemistry/)
*   RocketCEA (Python wrapper) [https://rocketcea.readthedocs.io/](https://rocketcea.readthedocs.io/)

═══════════════════════════════════════════════════════════════

## 23. CARTE THERMIQUE ET ANALYSE 2D/3D

L'analyse thermique 1D (Bartz + Dittus-Boelter) donne une moyenne.
L'onglet "Heatmap" permet d'affiner cette analyse en visualisant les gradients locaux, notamment entre les canaux de refroidissement.


### 23.1 EFFET D'AILETTE (FIN EFFECT)

Dans un moteur à canaux fraisés, la "nervure" (rib) entre deux canaux agit comme une ailette de refroidissement.

**EFFICACITÉ DE L'AILETTE ($\eta_{fin}$):**

$$ \eta_{fin} = \frac{\tanh(m H)}{m H} $$

où:
*   $m = \sqrt{2 h_c / (k w_{rib})}$
*   $H$ = hauteur du canal
*   $w_{rib}$ = largeur de la nervure

CONSÉQUENCE:
*   Le sommet de la nervure (côté chaud) est plus chaud que le fond du canal.
*   Si la nervure est trop fine ou trop haute, le sommet peut fondre même si le calcul 1D semble correct.


### 11.2 INTERPOLATION THERMIQUE 2D

Le logiciel génère une carte de température $T(x,y)$ en résolvant l'équation de la chaleur simplifiée sur la surface développée.

MODÈLE:
$$ T_{paroi}(\theta) = T_{base} + \Delta T_{rib} \cos(N_{canaux} \theta) $$

*   $T_{base}$: Température au-dessus du canal (zone la mieux refroidie)
*   $T_{peak}$: Température entre deux canaux (zone la plus chaude)
*   $\Delta T_{rib}$: Gradient thermique latéral

CRITÈRE DE CONCEPTION:
Il faut vérifier que $T_{peak} < T_{limite\_matériau}$.
Le calcul 1D donne souvent une valeur entre $T_{base}$ et $T_{peak}$.


### 11.3 VISUALISATIONS DISPONIBLES

**A) VUE EN COUPE RADIALE (Cross-Section):**
Montre la distribution $T$ dans l'épaisseur de la paroi.
Permet de voir le gradient radial ($T_{hot}$ vers $T_{cold}$).

**B) VUE DÉVELOPPÉE (Unrolled Surface):**
"Déroule" le cylindre/cône du moteur à plat.
*   Axe X: Position axiale ($z$)
*   Axe Y: Position circonférentielle ($\theta$)
*   Couleur: Température locale

Permet d'identifier les "Hot Spots" thermiques situés généralement au col et ENTRE les canaux.

**C) SURFACE 3D:**
Projection de la carte thermique sur la géométrie réelle.
Utile pour vérifier la continuité du refroidissement.


## 24. EXPORT CAD ET GÉOMÉTRIE

L'onglet "CAD" génère la géométrie solide du moteur pour la fabrication (CAM) ou l'intégration (CAD).


### 24.1 GÉNÉRATION DU PROFIL (LAVAL)

Le profil interne est généré par des courbes mathématiques:

1.  **CONVERGENT:**
    *   Arc de cercle ou courbe cubique
    *   Angle d'entrée (typiquement 30-45°)
    *   Rayon de courbure amont ($R_1 = 1.5 R_t$)

2.  **COL (THROAT):**
    *   Arc de cercle
    *   Rayon de courbure aval ($R_2 = 0.382 R_t$)

3.  **DIVERGENT:**
    *   Parabole (Méthode de Rao approximée) ou Conique
    *   Angle initial ($\theta_n$) et angle de sortie ($\theta_e$)
    *   $L = (R_e - R_t) / \tan(\theta_{moyen})$


### 12.2 MODÉLISATION DES CANAUX

Les canaux sont générés par soustraction booléenne:
$$ Volume_{Final} = Volume_{Paroi} - \sum(Volume_{Canaux}) $$

GÉOMÉTRIE DES CANAUX:
*   Section rectangulaire variable
*   Profondeur ($d$) et largeur ($w$) évoluent le long de l'axe Z
*   Suivent la courbure de la tuyère (conformal cooling)


### 12.3 FORMATS D'EXPORT

**A) STEP (.stp / .step) - RECOMMANDÉ:**
*   Format vectoriel standard ISO 10303
*   Géométrie exacte (NURBS)
*   Compatible: SolidWorks, Fusion 360, CATIA, FreeCAD
*   Idéal pour l'usinage CNC 5 axes

**B) STL (.stl):**
*   Maillage triangulaire
*   Résolution dépend du paramètre "Mesh Resolution"
*   Idéal pour l'impression 3D (Slicers: Cura, PrusaSlicer)
*   Difficile à modifier en CAD

**C) DXF (.dxf):**
*   Profil 2D (coupe longitudinale)
*   Utile pour le tournage (Lathe) ou la découpe jet d'eau


## 25. OPTIMISATION AUTOMATIQUE (ALGORITHME)

L'optimiseur cherche la "meilleure" configuration de refroidissement sans intervention manuelle, en résolvant un problème mathématique.


### 25.1 FONCTION OBJECTIF (COST FUNCTION)

On cherche à minimiser une fonction de coût $J(x)$:

$$ J(x) = w_M \frac{Masse}{M_{ref}} + w_P \frac{\Delta P}{P_{ref}} + w_T \times Penalté_T $$

Où:
*   Masse: Masse totale du moteur (cuivre + liner)
*   $\Delta P$: Perte de charge totale dans les canaux
*   $Penalté_T$: Augmente exponentiellement si $T_{paroi} > T_{cible}$

Les poids ($w$) sont ajustables:
*   "Masse Min": $w_M$ élevé
*   "Performance": $w_P$ élevé (minimiser perte de charge)
*   "Sécurité": $w_T$ élevé (maximiser marge thermique)


### 13.2 VARIABLES DE DÉCISION (x)

L'algorithme modifie itérativement:
1.  Nombre de canaux ($N$)
2.  Largeur des canaux ($w$)
3.  Profondeur des canaux ($d$)
4.  Épaisseur de paroi côté gaz ($e_{wg}$)


### 13.3 CONTRAINTES (CONSTRAINTS)

Le design doit respecter:
*   $g_1(x): T_{wall,hot} < T_{max,matériau}$ (ex: 900K pour Cu)
*   $g_2(x): \Delta P < \Delta P_{max,disponible}$ (ex: 20% de $P_c$)
*   $g_3(x): e_{wg} > e_{min,fabrication}$ (ex: 0.8 mm)
*   $g_4(x): w_{rib} > w_{min,fabrication}$ (ex: 1.0 mm)


### 13.4 ALGORITHME SLSQP

Utilise "Sequential Least Squares Programming" (SciPy):
1.  Calcule le gradient de $J(x)$
2.  Projette vers la direction de descente
3.  Vérifie les contraintes
4.  Converge quand $J(x)$ ne diminue plus

RÉSULTAT:
L'optimiseur trouve souvent des solutions non-intuitives, comme des canaux très profonds et fins au col (haute efficacité) et larges dans le divergent (faible perte de charge).


## 26. ANALYSE DES CONTRAINTES MÉCANIQUES

La paroi du moteur subit des charges extrêmes combinant pression et dilatation thermique.


### 26.1 CONTRAINTES PRIMAIRES (PRESSION)

Modèle du tube à paroi mince (Thin-walled pressure vessel):

$$ \sigma_{hoop} = \frac{(P_{int} - P_{ext}) R}{e} $$

*   $\sigma_{hoop}$: Contrainte circonférentielle (traction)
*   $P_{int}$: Pression gaz (chambre)
*   $P_{ext}$: Pression coolant (canaux)
*   $R$: Rayon moyen
*   $e$: Épaisseur effective

Note: Si $P_{coolant} > P_{gaz}$ (cycle expander/staged), la paroi interne est en COMPRESSION (risque de flambage/buckling).


### 14.2 CONTRAINTES THERMIQUES (SECONDAIRES)

Dues au gradient de température $\Delta T = T_{hot} - T_{cold}$.
La face chaude veut se dilater mais est retenue par la face froide.

$$ \sigma_{thermal} = \pm \frac{E \alpha \Delta T}{2 (1 - \nu)} $$

*   $E$: Module de Young (GPa)
*   $\alpha$: Coefficient de dilatation thermique (K⁻¹)
*   $\nu$: Coefficient de Poisson (~0.3)

DISTRIBUTION:
*   Face Chaude: COMPRESSION ($\sigma < 0$) car dilatation empêchée
*   Face Froide: TRACTION ($\sigma > 0$)

**ATTENTION:** C'est souvent la contrainte dominante (peut dépasser 500 MPa)!


### 14.3 CRITÈRE DE VON MISES

Pour prédire la plastification, on combine les contraintes:

$$ \sigma_{vm} = \sqrt{\sigma_{hoop}^2 + \sigma_{long}^2 + \sigma_{radial}^2 - ...} $$

Simplifié (état plan):
$$ \sigma_{vm} \approx \sqrt{\sigma_{hoop}^2 + \sigma_{thermal}^2 - \sigma_{hoop}\sigma_{thermal}} $$

CRITÈRE DE SÉCURITÉ:
$$ FoS = \frac{\sigma_{yield}}{\sigma_{vm}} $$

*   $FoS > 1.0$ : Domaine élastique (OK)
*   $FoS < 1.0$ : Plastification (Déformation permanente)


### 14.4 FATIGUE OLIGOCYCLIQUE (LCF)

Dans un moteur fusée, il est courant que $\sigma_{vm} > \sigma_{yield}$ localement ($FoS < 1$). La paroi plastifie à chaque allumage.

LOI DE COFFIN-MANSON:
$$ N_{cycles} = C (\Delta\epsilon_{plastique})^{-k} $$

*   Si on plastifie beaucoup, la durée de vie est courte (ex: 50 cycles).
*   C'est acceptable pour un moteur jetable (ELV).
*   Pour du réutilisable (RLV), il faut viser $FoS > 1.2$.


## 27. SIMULATION TRANSITOIRE (DÉMARRAGE)

Le régime permanent (Steady State) n'est atteint qu'après plusieurs secondes. Le pic de température peut survenir avant.


### 27.1 ÉQUATION DE LA CHALEUR INSTATIONNAIRE

$$ \rho C_p \frac{\partial T}{\partial t} = \nabla \cdot (k \nabla T) $$

Discrétisation 1D (Différences Finies Explicites):

$$ T_i^{n+1} = T_i^n + \frac{dt}{\rho C_p V} \sum Flux_{entrants} $$

Où $T_i^n$ est la température du nœud $i$ au temps $n$.


### 15.2 STABILITÉ NUMÉRIQUE (CRITÈRE DE FOURIER)

Pour que la simulation ne diverge pas, le pas de temps $dt$ doit être très petit:

$$ dt < \frac{\rho C_p dx^2}{2 k} $$

Pour le cuivre ($k$ élevé) et $dx$ petit (0.1 mm), $dt \approx 10^{-5} \text{ s}$ !
C'est pourquoi la simulation peut prendre du temps.


### 15.3 PHÉNOMÈNES TRANSITOIRES CLÉS

**A) OVERSHOOT AU DÉMARRAGE:**
Si le film de refroidissement met du temps à s'établir (lag hydraulique), la paroi peut chauffer brutalement avant d'être refroidie.
$\rightarrow$ Risque de fusion flash ("Burn-through").

**B) INERTIE THERMIQUE:**
Temps caractéristique $\tau = (\rho C_p e^2) / k$
*   Cuivre: $\tau$ très court (réponse rapide)
*   Inconel: $\tau$ long (la paroi chauffe lentement)

**C) SOAK-BACK (ARRÊT):**
À l'extinction, le refroidissement s'arrête mais la chaleur stockée dans la masse du moteur diffuse vers les injecteurs et les vannes.
$\rightarrow$ Risque de vaporisation du carburant résiduel (explosif).
$\rightarrow$ Nécessite souvent une purge à l'azote post-tir.

RÉFÉRENCES BIBLIOGRAPHIQUES
═══════════════════════════════════════════════════════════════
Document généré par Rocket Motor Design Plotter v6 - Décembre 2025
