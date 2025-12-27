# 15. SIMULATION TRANSITOIRE (DÉMARRAGE)

[← Section précédente : Analyses Avancées](11-14-Analyses-Avancees.md) | [Retour à l'accueil](Home.md) | [Section suivante : Références →](References.md)

---

## Table des matières
- [15.1 Équation de la chaleur instationnaire](#151-équation-de-la-chaleur-instationnaire)
- [15.2 Stabilité numérique (critère de Fourier)](#152-stabilité-numérique-critère-de-fourier)
- [15.3 Phénomènes transitoires clés](#153-phénomènes-transitoires-clés)

---


15. SIMULATION TRANSITOIRE (DÉMARRAGE)
═══════════════════════════════════════════════════════════════

Le régime permanent (Steady State) n'est atteint qu'après
plusieurs secondes. Le pic de température peut survenir avant.

15.1 ÉQUATION DE LA CHALEUR INSTATIONNAIRE
───────────────────────────────────────────────────────────────
  ρ × Cp × (∂T/∂t) = ∇ · (k ∇T)

  Discrétisation 1D (Différences Finies Explicites):
  
  T_i^(n+1) = T_i^n + (dt / (ρ Cp V)) × Σ Flux_entrants

  Où T_i^n est la température du nœud i au temps n.

15.2 STABILITÉ NUMÉRIQUE (CRITÈRE DE FOURIER)
───────────────────────────────────────────────────────────────
Pour que la simulation ne diverge pas, le pas de temps dt doit
être très petit:

  dt < (ρ × Cp × dx²) / (2 × k)

  Pour le cuivre (k élevé) et dx petit (0.1 mm), dt ≈ 10⁻⁵ s !
  C'est pourquoi la simulation peut prendre du temps.

15.3 PHÉNOMÈNES TRANSITOIRES CLÉS
───────────────────────────────────────────────────────────────
A) OVERSHOOT AU DÉMARRAGE:
   Si le film de refroidissement met du temps à s'établir
   (lag hydraulique), la paroi peut chauffer brutalement
   avant d'être refroidie.
   → Risque de fusion flash ("Burn-through").

B) INERTIE THERMIQUE:
   Temps caractéristique τ = (ρ Cp e²) / k
   - Cuivre: τ très court (réponse rapide)
   - Inconel: τ long (la paroi chauffe lentement)

C) SOAK-BACK (ARRÊT):
   À l'extinction, le refroidissement s'arrête mais la chaleur
   stockée dans la masse du moteur diffuse vers les injecteurs
   et les vannes.
   → Risque de vaporisation du carburant résiduel (explosif).
   → Nécessite souvent une purge à l'azote post-tir.

RÉFÉRENCES BIBLIOGRAPHIQUES
═══════════════════════════════════════════════════════════════
Document généré par Rocket Motor Design Plotter v6 - Décembre 2025


---

[← Section précédente : Analyses Avancées](11-14-Analyses-Avancees.md) | [Retour à l'accueil](Home.md) | [Section suivante : Références →](References.md)
