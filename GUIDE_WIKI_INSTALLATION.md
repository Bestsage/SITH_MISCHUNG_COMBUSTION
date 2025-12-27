# 🚀 Guide de Finalisation du Wiki GitHub

Ce document explique comment finaliser l'installation du wiki sur GitHub.

## ✅ Ce qui a été fait

Le contenu du fichier `wiki.txt` a été **converti en 11 pages wiki** avec:
- ✅ Tables des matières interactives
- ✅ Navigation entre pages (précédent/suivant)
- ✅ Sidebar pour navigation latérale
- ✅ Footer cohérent sur toutes les pages
- ✅ 4,864 lignes de documentation

## 📋 Étapes de finalisation

### Option 1: Déploiement Automatique (Recommandé)

```bash
# Assurez-vous d'avoir les droits d'écriture sur le dépôt
chmod +x deploy-wiki.sh
./deploy-wiki.sh
```

Ce script va:
1. Cloner le wiki GitHub (ou le créer s'il n'existe pas)
2. Copier tous les fichiers markdown du dossier `wiki/`
3. Commit et push vers le wiki GitHub

### Option 2: Déploiement Manuel

Si vous préférez le faire manuellement:

```bash
# 1. Activer le wiki dans les settings GitHub
# Allez sur: https://github.com/Bestsage/SITH_MISCHUNG_COMBUSTION/settings
# Dans la section "Features", activez "Wikis"

# 2. Cloner le wiki
git clone https://github.com/Bestsage/SITH_MISCHUNG_COMBUSTION.wiki.git

# 3. Copier les fichiers
cp wiki/*.md SITH_MISCHUNG_COMBUSTION.wiki/

# 4. Commit et push
cd SITH_MISCHUNG_COMBUSTION.wiki
git add .
git commit -m "Import wiki complet d'analyse thermique des moteurs-fusées"
git push origin master
```

### Option 3: Garder dans le Dépôt Principal

Les fichiers wiki peuvent aussi servir de documentation directement dans le dépôt:
- Accessible via: `https://github.com/Bestsage/SITH_MISCHUNG_COMBUSTION/tree/main/wiki`
- GitHub affiche automatiquement le markdown formaté
- Pas besoin d'activer le wiki GitHub

## 🔍 Vérification

Après le déploiement, vérifiez que:
1. Le wiki est accessible à: `https://github.com/Bestsage/SITH_MISCHUNG_COMBUSTION/wiki`
2. La page d'accueil (Home) s'affiche correctement
3. Les liens de navigation fonctionnent
4. La sidebar apparaît sur le côté gauche (GitHub wiki)

## 📖 Structure du Wiki

```
wiki/
├── Home.md                                    # Page d'accueil
├── 1-Introduction-et-Concepts-Fondamentaux.md
├── 2-Theorie-Detaillee-du-Transfert-Thermique.md
├── 3-Modele-de-Bartz.md
├── 4-Calcul-des-Temperatures-de-Paroi.md
├── 5-Design-et-Dimensionnement.md
├── 9-Exemples-de-Calcul.md
├── 10-Formules-Rapides.md
├── 11-14-Analyses-Avancees.md
├── 15-Simulation-Transitoire.md
├── References.md
├── _Sidebar.md                                # Navigation latérale
├── _Footer.md                                 # Pied de page
└── README.md                                  # Instructions
```

## 🎯 Contenu du Wiki

Le wiki couvre l'**analyse thermique complète des moteurs-fusées**:

### Sections Théoriques
1. Introduction et concepts fondamentaux
2. Théorie détaillée du transfert thermique
3. Modèle de Bartz pour h_g
4. Calcul des températures de paroi

### Sections Pratiques
5-8. Design et dimensionnement des canaux
9. Exemples de calcul complets
10. Formules rapides (aide-mémoire)

### Sections Avancées
11-14. Analyses avancées (2D/3D, CAD, optimisation, contraintes mécaniques)
15. Simulation transitoire (démarrage)

### Annexes
- Références bibliographiques complètes

## 💡 Conseils d'Utilisation

### Pour les Lecteurs
- Commencez par la page [Home](wiki/Home.md)
- Utilisez la table des matières pour naviguer
- Les formules sont présentées avec leur contexte
- Les exemples incluent des calculs numériques détaillés

### Pour les Contributeurs
- Les fichiers sont en markdown standard
- Utilisez les ancres (#section-name) pour les liens internes
- Maintenez la cohérence de la navigation
- Testez les liens après modifications

## 🔧 Personnalisation

### Modifier la Sidebar
Éditez `wiki/_Sidebar.md` pour changer la navigation latérale.

### Modifier le Footer
Éditez `wiki/_Footer.md` pour changer le pied de page.

### Ajouter une Page
1. Créez un nouveau fichier `.md` dans `wiki/`
2. Ajoutez-le à la table des matières dans `Home.md`
3. Ajoutez-le à la `_Sidebar.md`
4. Ajoutez des liens de navigation vers/depuis les pages adjacentes

## ❓ Dépannage

### "Le wiki n'est pas activé"
Allez dans Settings > Features et activez "Wikis"

### "Permission denied"
Vérifiez que vous avez les droits d'écriture sur le dépôt

### "Les liens ne fonctionnent pas"
- Dans le dépôt principal: les liens relatifs (.md) fonctionnent
- Dans le wiki GitHub: GitHub supprime l'extension .md automatiquement
  - Utilisez les deux formats pour compatibilité maximale

### "Le formatage est cassé"
- Vérifiez la syntaxe markdown
- Assurez-vous que les tableaux ont des lignes vides avant/après
- Les blocs de code doivent être entourés de ```

## 📞 Support

Pour toute question ou problème:
1. Consultez la [documentation GitHub sur les wikis](https://docs.github.com/en/communities/documenting-your-project-with-wikis)
2. Ouvrez une issue sur le dépôt
3. Contactez les mainteneurs: @Bestsage ou @Sabu8c

---

**Bon usage du wiki! 🚀📖**
