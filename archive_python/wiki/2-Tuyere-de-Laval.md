# 2. La Tuyère de Laval : Passer le Mur du Son

## 🎺 Une Forme Magique

Pour accélérer un gaz au-delà de la vitesse du son (Mach 1), il faut une forme très spécifique : **un sablier**.

Cette forme s'appelle une **tuyère de Laval** (ou convergent-divergent), du nom de l'ingénieur suédois Gustaf de Laval qui l'a inventée en 1888.

---

## 📐 Les Trois Zones de la Tuyère

### 1️⃣ Le Convergent : Accélération Subsonique

**Le gaz est subsonique (Mach < 1)**

- On rétrécit le passage
- Le gaz accélère (comme un tuyau d'arrosage pincé)
- La pression diminue
- La vitesse augmente

**Comportement :** Plus c'est étroit, plus ça va vite ✅

---

### 2️⃣ Le Col (Throat) : Blocage Sonique

**C'est le point le plus étroit**

- Le gaz atteint **EXACTEMENT** la vitesse du son (Mach = 1)
- On ne peut pas aller plus vite à cet endroit (phénomène de **blocage sonique**)
- C'est la "porte" qui contrôle tout le débit du moteur

**Point critique :** C'est ici que la chaleur est la plus intense ! 🔥

---

### 3️⃣ Le Divergent : Accélération Supersonique

**Le gaz est supersonique (Mach > 1)**

- Contre-intuitivement, pour l'accélérer encore, il faut **ÉLARGIR** le passage
- Le gaz se détend et transforme sa chaleur en vitesse cinétique
- La pression diminue encore
- La vitesse augmente jusqu'à la sortie (peut atteindre Mach 3-5)

**Comportement :** Plus c'est large, plus ça va vite ✅ (seulement en supersonique !)

---

## 🔬 Pourquoi ce Comportement Contre-Intuitif ?

### En Subsonique (Mach < 1)
Les molécules ont le temps de "voir" le rétrécissement et se réarrangent :
- Rétrécir → Vitesse augmente
- Élargir → Vitesse diminue

### En Supersonique (Mach > 1)
Les molécules vont plus vite que l'information (onde sonore) :
- Élargir → Vitesse augmente
- Rétrécir → Vitesse diminue

C'est l'inverse ! 🔄

---

## 📊 Schéma de la Tuyère

```
        Chambre de Combustion
              (Mach ~ 0.1)
                  │
                  ↓
        ╱╲        CONVERGENT        ╱╲
       ╱  ╲       Mach < 1         ╱  ╲
      ╱    ╲      Accélération    ╱    ╲
     ╱      ╲                    ╱      ╲
    ╱        ╲                  ╱        ╲
   ╱          ║                ║          ╲
  │           ║   COL (Throat) ║           │
  │           ║    Mach = 1    ║           │
   ╲          ║                ║          ╱
    ╲        ╱                  ╲        ╱
     ╲      ╱     DIVERGENT      ╲      ╱
      ╲    ╱      Mach > 1        ╲    ╱
       ╲  ╱       Accélération     ╲  ╱
        ╲╱                          ╲╱
         
                  Sortie
            (Mach 3-5 typique)
```

---

## 📏 Paramètres Importants

### Rapport d'Expansion (ε)
```
ε = A_sortie / A_col
```

- Plus ε est grand, plus le gaz est accéléré
- Typique : ε = 10 à 100
- Optimisé selon l'altitude d'utilisation

### Angle du Divergent
- Trop petit → tuyère trop longue et lourde
- Trop grand → pertes par friction et détachement de flux
- Optimal : 12-18 degrés

---

## 🎓 Points Clés à Retenir

1. ✅ La tuyère de Laval est essentielle pour accélérer au-delà de Mach 1
2. ✅ Le col bloque le débit et impose Mach = 1
3. ✅ Le comportement s'inverse entre subsonique et supersonique
4. ✅ Le col est le point le plus chaud et critique thermiquement

---

## 🔄 Navigation

- 🏠 [Retour à l'Accueil](Home)
- 📚 [Retour à Partie 1](Partie-1-Les-Bases)
- ⬅️ [Précédent : Introduction](1-Introduction)
- ➡️ [Suivant : Le Problème Thermique](3-Probleme-Thermique)
