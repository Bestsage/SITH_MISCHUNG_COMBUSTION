# 🔥 ANALYSE THERMIQUE DES MOTEURS-FUSÉES - GUIDE COMPLET

Ce guide exhaustif couvre tous les aspects du refroidissement régénératif des moteurs-fusées à propergols liquides.

---

## 📚 Table des Matières

### [1. Introduction et Concepts Fondamentaux](1-Introduction-et-Concepts-Fondamentaux.md)
- [1.1 Pourquoi le refroidissement est-il critique ?](1-Introduction-et-Concepts-Fondamentaux.md#11-pourquoi-le-refroidissement-est-il-critique-)
- [1.2 Les différentes stratégies de refroidissement](1-Introduction-et-Concepts-Fondamentaux.md#12-les-différentes-stratégies-de-refroidissement)
- [1.3 Schéma du transfert thermique](1-Introduction-et-Concepts-Fondamentaux.md#13-schéma-du-transfert-thermique)
- [1.4 Équations fondamentales du transfert](1-Introduction-et-Concepts-Fondamentaux.md#14-équations-fondamentales-du-transfert)
- [1.5 Ordres de grandeur typiques](1-Introduction-et-Concepts-Fondamentaux.md#15-ordres-de-grandeur-typiques)

### [2. Théorie Détaillée du Transfert Thermique](2-Theorie-Detaillee-du-Transfert-Thermique.md)
- [2.1 La conduction thermique](2-Theorie-Detaillee-du-Transfert-Thermique.md#21-la-conduction-thermique)
  - 2.1.1 Loi de Fourier
  - 2.1.2 Conductivité des matériaux pour moteurs-fusées
  - 2.1.3 Géométrie cylindrique
- [2.2 La convection thermique](2-Theorie-Detaillee-du-Transfert-Thermique.md#22-la-convection-thermique)
  - 2.2.1 Loi de Newton du refroidissement
  - 2.2.2 Types de convection
  - 2.2.3 Couche limite thermique
- [2.3 Les nombres adimensionnels](2-Theorie-Detaillee-du-Transfert-Thermique.md#23-les-nombres-adimensionnels)
  - 2.3.1 Nombre de Reynolds (Re)
  - 2.3.2 Nombre de Prandtl (Pr)
  - 2.3.3 Nombre de Nusselt (Nu)
  - 2.3.4 Autres nombres utiles

### [3. Modèle de Bartz pour h_g](3-Modele-de-Bartz.md)
- [3.1 Historique et développement](3-Modele-de-Bartz.md#31-historique-et-développement)
- [3.2 Équation complète de Bartz](3-Modele-de-Bartz.md#32-équation-complète-de-bartz)
- [3.3 Formule simplifiée (utilisée dans le code)](3-Modele-de-Bartz.md#33-formule-simplifiée-utilisée-dans-le-code)
- [3.4 Propriétés des gaz de combustion](3-Modele-de-Bartz.md#34-propriétés-des-gaz-de-combustion)
- [3.5 Valeurs typiques de h_g](3-Modele-de-Bartz.md#35-valeurs-typiques-de-h_g)
- [3.6 Limitations du modèle de Bartz](3-Modele-de-Bartz.md#36-limitations-du-modèle-de-bartz)
- [3.7 Comparaison avec autres corrélations](3-Modele-de-Bartz.md#37-comparaison-avec-autres-corrélations)

### [4. Calcul des Températures de Paroi](4-Calcul-des-Temperatures-de-Paroi.md)
- [4.1 Système d'équations thermiques](4-Calcul-des-Temperatures-de-Paroi.md#41-système-déquations-thermiques)
- [4.2 Calcul de T_WALL_HOT (température critique)](4-Calcul-des-Temperatures-de-Paroi.md#42-calcul-de-t_wall_hot-température-critique)
- [4.3 Calcul de T_WALL_COLD](4-Calcul-des-Temperatures-de-Paroi.md#43-calcul-de-t_wall_cold)
- [4.4 Profil de température dans la paroi](4-Calcul-des-Temperatures-de-Paroi.md#44-profil-de-température-dans-la-paroi)
- [4.5 Contraintes thermiques (stress thermique)](4-Calcul-des-Temperatures-de-Paroi.md#45-contraintes-thermiques-stress-thermique)
- [4.6 Régime transitoire (démarrage/arrêt)](4-Calcul-des-Temperatures-de-Paroi.md#46-régime-transitoire-démarragearrêt)

### [5-8. Design et Dimensionnement des Canaux](5-Design-et-Dimensionnement.md)
- [5. Coefficient de convection côté coolant](5-Design-et-Dimensionnement.md#5-coefficient-de-convection-côté-coolant)
- [6. Dimensionnement des canaux de refroidissement](5-Design-et-Dimensionnement.md#6-dimensionnement-des-canaux-de-refroidissement)
- [7. Pertes de charge hydrauliques](5-Design-et-Dimensionnement.md#7-pertes-de-charge-hydrauliques)
- [8. Choix des matériaux](5-Design-et-Dimensionnement.md#8-choix-des-matériaux)

### [9. Exemples de Calcul Complets](9-Exemples-de-Calcul.md)
- [9.1 Exemple 1 : Moteur LOX/RP-1 petit poussée](9-Exemples-de-Calcul.md#91-exemple-1--moteur-loxrp-1-petit-poussée)
- [9.2 Exemple 2 : Moteur LOX/LH2 haute performance](9-Exemples-de-Calcul.md#92-exemple-2--moteur-loxlh2-haute-performance)
- [9.3 Exemple 3 : Moteur LOX/CH4 (méthane)](9-Exemples-de-Calcul.md#93-exemple-3--moteur-loxch4-méthane)
- [9.4 Exemple 4 : Vérification coefficient h_c requis](9-Exemples-de-Calcul.md#94-exemple-4--vérification-coefficient-h_c-requis)
- [9.5 Exemple 5 : Calcul élévation température coolant](9-Exemples-de-Calcul.md#95-exemple-5--calcul-élévation-température-coolant)
- [9.6 Exemple 6 : Analyse dimensionnelle rapide](9-Exemples-de-Calcul.md#96-exemple-6--analyse-dimensionnelle-rapide)
- [9.7 Tableau récapitulatif des exemples](9-Exemples-de-Calcul.md#97-tableau-récapitulatif-des-exemples)
- [9.8 Exercices d'application](9-Exemples-de-Calcul.md#98-exercices-dapplication)

### [10. Formules Rapides (Aide-Mémoire Complet)](10-Formules-Rapides.md)
- [10.1 Équations fondamentales du transfert thermique](10-Formules-Rapides.md#101-équations-fondamentales-du-transfert-thermique)
- [10.2 Équation de Bartz (côté gaz chaud)](10-Formules-Rapides.md#102-équation-de-bartz-côté-gaz-chaud)
- [10.3 Nombres adimensionnels](10-Formules-Rapides.md#103-nombres-adimensionnels)
- [10.4 Corrélations de convection forcée](10-Formules-Rapides.md#104-corrélations-de-convection-forcée)
- [10.5 Équations de température de paroi](10-Formules-Rapides.md#105-équations-de-température-de-paroi)
- [10.6 Épaisseur de paroi](10-Formules-Rapides.md#106-épaisseur-de-paroi)
- [10.7 Puissance et énergie thermique](10-Formules-Rapides.md#107-puissance-et-énergie-thermique)
- [10.8 Pertes de charge](10-Formules-Rapides.md#108-pertes-de-charge)
- [10.9 Film cooling](10-Formules-Rapides.md#109-film-cooling)
- [10.10 Propriétés des gaz de combustion](10-Formules-Rapides.md#1010-propriétés-des-gaz-de-combustion)
- [10.11 Tableau récapitulatif des formules](10-Formules-Rapides.md#1011-tableau-récapitulatif-des-formules)
- [10.12 Ordres de grandeur typiques](10-Formules-Rapides.md#1012-ordres-de-grandeur-typiques)
- [10.13 Conversions utiles](10-Formules-Rapides.md#1013-conversions-utiles)
- [10.14 Constantes physiques](10-Formules-Rapides.md#1014-constantes-physiques)

### [11-14. Analyses Avancées](11-14-Analyses-Avancees.md)
- [11. Carte thermique et analyse 2D/3D](11-14-Analyses-Avancees.md#11-carte-thermique-et-analyse-2d3d)
- [12. Export CAD et géométrie](11-14-Analyses-Avancees.md#12-export-cad-et-géométrie)
- [13. Optimisation automatique (algorithme)](11-14-Analyses-Avancees.md#13-optimisation-automatique-algorithme)
- [14. Analyse des contraintes mécaniques](11-14-Analyses-Avancees.md#14-analyse-des-contraintes-mécaniques)

### [15. Simulation Transitoire (Démarrage)](15-Simulation-Transitoire.md)
- [15.1 Équation de la chaleur instationnaire](15-Simulation-Transitoire.md#151-équation-de-la-chaleur-instationnaire)
- [15.2 Stabilité numérique (critère de Fourier)](15-Simulation-Transitoire.md#152-stabilité-numérique-critère-de-fourier)
- [15.3 Phénomènes transitoires clés](15-Simulation-Transitoire.md#153-phénomènes-transitoires-clés)

### [Références Bibliographiques](References.md)
- [Ouvrages de référence](References.md#ouvrages-de-référence)
- [Publications techniques](References.md#publications-techniques)
- [Documents NASA](References.md#documents-nasa)
- [Logiciels et bases de données](References.md#logiciels-et-bases-de-données)

---

## 🚀 À propos

Ce guide technique est conçu pour accompagner l'utilisation du logiciel d'analyse thermique des moteurs-fusées. Il couvre à la fois les aspects théoriques fondamentaux et les applications pratiques pour la conception de systèmes de refroidissement régénératif.

**Version:** Décembre 2025  
**Document source:** Rocket Motor Design Plotter v6
