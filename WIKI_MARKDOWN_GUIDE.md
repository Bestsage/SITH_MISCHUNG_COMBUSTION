# 📝 Wiki Markdown Support - Documentation

## Vue d'ensemble

Le système wiki supporte maintenant deux formats de fichiers:

1. **wiki.md** (recommandé) - Format Markdown avec tables propres, compatible GitHub wiki
2. **wiki.txt** (legacy) - Format texte avec formatage manuel ASCII

## 🎯 Avantages du Format Markdown

### ✅ Tables Propres
**Avant (ASCII):**
```
┌─────────┬──────────┐
│ Alliage │ Conduct. │
├─────────┼──────────┤
│ CuCr    │ ~320     │
└─────────┴──────────┘
```

**Après (Markdown):**
```markdown
| Alliage | Conductivité (W/mK) |
|---------|---------------------|
| CuCr    | ~320                |
```

### ✅ Compatibilité GitHub Wiki

Le même fichier `wiki.md` peut être utilisé:
- Dans l'application (rendu automatique)
- Sur GitHub wiki (.md supporté nativement)
- Dans n'importe quel éditeur Markdown

### ✅ Syntaxe Standard

Utilise la syntaxe Markdown standard - pas besoin d'apprendre un format custom!

## 📋 Syntaxe Supportée

### Headers (Titres)

```markdown
# Titre Principal (H1)
## Section (H2)
### Sous-section (H3)
#### Sous-sous-section (H4)
```

### Tables (Tableaux)

```markdown
| Colonne 1 | Colonne 2 | Colonne 3 |
|-----------|-----------|-----------|
| Valeur 1  | Valeur 2  | Valeur 3  |
| Data A    | Data B    | Data C    |
```

**Rendu:** Table avec header en cyan bold, contenu en monospace

**Note:** Les tables doivent respecter le format:
- Commencer et finir par `|` sur chaque ligne
- Ligne séparateur avec au moins un `-` : `|---|---|`

### Lists (Listes)

**Listes à puces:**
```markdown
- Premier item
- Deuxième item
  - Sous-item
```

**Listes numérotées:**
```markdown
1. Étape 1
2. Étape 2
3. Étape 3
```

### Code Blocks (Blocs de Code)

```markdown
\`\`\`
code_example = "Hello World"
print(code_example)
\`\`\`
```

**Rendu:** Monospace, fond sombre, vert

### Inline Formatting (Limitation actuelle)

**Note:** Le formatage inline (`**bold**`, `*italic*`, `` `code` ``) n'est pas encore supporté dans cette version. Le texte sera affiché normalement. Cette fonctionnalité pourra être ajoutée dans une future version si nécessaire.

## 🚀 Migration depuis wiki.txt

### Option 1: Conversion Manuelle

1. Créer `wiki.md`
2. Copier le contenu de `wiki.txt`
3. Remplacer les tables ASCII par des tables Markdown
4. Remplacer les séparateurs (═══, ───) par des headers (#, ##)
5. L'application détecte automatiquement le .md

### Option 2: Coexistence

Les deux fichiers peuvent coexister:
- Si `wiki.md` existe → utilisé en priorité
- Sinon → `wiki.txt` utilisé (legacy)

Pas besoin de supprimer `wiki.txt` immédiatement!

## 📊 Exemple de Table Complète

### Base de Données Matériaux

```markdown
| Alliage | Conductivité (W/mK) | T_fusion (°C) | Résistance (MPa) | Usage |
|---------|---------------------|---------------|------------------|-------|
| Cu-OFHC | 390 | 1085 | 200 | Chambre haute perf |
| CuCr | 320 | 1080 | 400 | Standard industrie |
| GRCop-42 | 330 | 1082 | 450 | SpaceX Raptor |
| Inconel 718 | 12 | 1336 | 1200 | Extensions tuyère |
| AlSi10Mg | 130 | 570 | 280 | Petits moteurs |
```

Cette table sera rendue avec:
- Header en **cyan bold** avec fond
- Colonnes alignées
- Facile à lire et maintenir

## 🎨 Styles Appliqués

| Élément | Tag Tkinter | Style Visuel |
|---------|-------------|--------------|
| # Header | h1 | 20pt, pink, grand espacement |
| ## Section | h2 | 15pt, orange, espacement moyen |
| ### Subsection | h3 | 13pt, cyan, petit espacement |
| Table header | table_header | Cyan bold, fond sombre |
| Table content | code | Monospace, aligné |
| - Bullet | bullet | Indenté 30-50px |
| 1. Numbered | numbered_list | Indenté 30-50px |
| ```code``` | code | Monospace, vert, fond sombre |

## 🔍 Détection Automatique

L'application vérifie dans cet ordre:

1. **wiki.md existe?** → Parser Markdown
2. **wiki.txt existe?** → Parser texte legacy
3. **Aucun?** → Message d'erreur

Code de détection:
```python
wiki_files = [
    ('wiki.md', 'markdown'),   # Priorité 1
    ('wiki.txt', 'text')       # Priorité 2 (fallback)
]
```

## 📝 Template de Base

Voici un template minimal pour commencer:

```markdown
# 🔥 MON PROJET

Description du projet...

## Section 1

Contenu de la section...

### 1.1 Sous-section

Plus de détails...

## Données Techniques

| Paramètre | Valeur | Unité |
|-----------|--------|-------|
| Pression | 50 | bar |
| Température | 3000 | K |

## Liste des Étapes

1. Première étape
2. Deuxième étape
3. Troisième étape

## Code Exemple

\`\`\`
def calculate():
    return 42
\`\`\`
```

## ⚙️ Configuration Technique

### Fichiers Modifiés

- `main.py`:
  - `load_wiki_content()` - Détection auto .md/.txt
  - `_load_markdown_wiki()` - Parser Markdown (nouveau)
  - `_load_text_wiki()` - Parser texte legacy

### Dépendances

Aucune dépendance externe requise! Le parser utilise:
- `re` (regex) - stdlib Python
- Parsing ligne par ligne
- Conversion vers tags tkinter

## 🐛 Dépannage

### "Erreur: Aucun fichier wiki trouvé"
→ Créer `wiki.md` ou `wiki.txt` dans le même dossier que `main.py`

### "Tables mal formatées"
→ Vérifier que chaque ligne commence et finit par `|`
→ La ligne séparateur doit contenir `|---|---|`

### "Headers non détectés"
→ S'assurer qu'il y a un espace après # (ex: `# Titre` pas `#Titre`)

## 🎓 Ressources Markdown

- [Guide Markdown GitHub](https://guides.github.com/features/mastering-markdown/)
- [Markdown Cheatsheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)
- [Markdown Table Generator](https://www.tablesgenerator.com/markdown_tables)

---

**Note:** Le fichier `wiki.md` fourni est un exemple avec tables, headers, et formatage complet. Utilisez-le comme template!

*"May the Thrust be with you." 🚀*
