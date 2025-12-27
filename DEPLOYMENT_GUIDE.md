# 🚀 Guide de Déploiement du Wiki

Ce guide explique comment déployer le wiki amélioré vers GitHub Wiki sur différentes plateformes.

---

## 📋 Prérequis

Avant de déployer, assurez-vous d'avoir :
- ✅ Git installé sur votre système
- ✅ Accès en écriture au dépôt GitHub
- ✅ Authentification GitHub configurée (HTTPS ou SSH)

---

## 💻 Windows

### Option 1 : Utiliser le script Batch (.bat)

Le moyen le plus simple sur Windows est d'utiliser le script `.bat` :

```cmd
deploy-wiki.bat
```

**Étapes :**
1. Ouvrir l'Invite de commandes (CMD) ou PowerShell
2. Naviguer vers le dossier du projet :
   ```cmd
   cd C:\chemin\vers\SITH_MISCHUNG_COMBUSTION
   ```
3. Exécuter le script :
   ```cmd
   deploy-wiki.bat
   ```

### Option 2 : Git Bash (recommandé)

Si vous avez installé Git pour Windows, vous avez accès à Git Bash qui peut exécuter des scripts `.sh` :

1. **Clic droit** dans le dossier du projet
2. Sélectionner **"Git Bash Here"**
3. Exécuter :
   ```bash
   ./deploy-wiki.sh
   ```

### Option 3 : WSL (Windows Subsystem for Linux)

Si vous utilisez WSL :

```bash
cd /mnt/c/chemin/vers/SITH_MISCHUNG_COMBUSTION
./deploy-wiki.sh
```

### Option 4 : Déploiement Manuel sur Windows

Si les scripts ne fonctionnent pas, voici les commandes manuelles :

```cmd
REM 1. Cloner le wiki
git clone https://github.com/Bestsage/SITH_MISCHUNG_COMBUSTION.wiki.git %TEMP%\wiki-deploy

REM 2. Copier les fichiers
copy /Y wiki\*.md %TEMP%\wiki-deploy\

REM 3. Naviguer vers le dossier
cd /d %TEMP%\wiki-deploy

REM 4. Ajouter et committer
git add .
git commit -m "Update wiki documentation"

REM 5. Pousser vers GitHub
git push origin master

REM 6. Retourner au dossier original
cd /d C:\chemin\vers\SITH_MISCHUNG_COMBUSTION

REM 7. Nettoyer
rmdir /s /q %TEMP%\wiki-deploy
```

---

## 🐧 Linux / macOS

### Utiliser le script Bash (.sh)

```bash
./deploy-wiki.sh
```

**Étapes :**
1. Ouvrir un terminal
2. Naviguer vers le dossier du projet :
   ```bash
   cd ~/chemin/vers/SITH_MISCHUNG_COMBUSTION
   ```
3. Rendre le script exécutable (première fois seulement) :
   ```bash
   chmod +x deploy-wiki.sh
   ```
4. Exécuter le script :
   ```bash
   ./deploy-wiki.sh
   ```

### Déploiement Manuel sur Linux/macOS

```bash
# 1. Cloner le wiki
git clone https://github.com/Bestsage/SITH_MISCHUNG_COMBUSTION.wiki.git /tmp/wiki-deploy

# 2. Copier les fichiers
cp wiki/*.md /tmp/wiki-deploy/

# 3. Naviguer et committer
cd /tmp/wiki-deploy
git add .
git commit -m "Update wiki documentation"

# 4. Pousser vers GitHub
git push origin master

# 5. Nettoyer
cd -
rm -rf /tmp/wiki-deploy
```

---

## 🔐 Authentification GitHub

### Si vous obtenez une erreur d'authentification :

#### Option 1 : HTTPS avec Personal Access Token
1. Créer un token sur GitHub : Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Donner les permissions `repo` et `wiki`
3. Utiliser le token comme mot de passe lors du push

#### Option 2 : SSH
1. Modifier l'URL du wiki dans le script :
   ```bash
   # Remplacer WIKI_URL par :
   WIKI_URL="git@github.com:Bestsage/SITH_MISCHUNG_COMBUSTION.wiki.git"
   ```
2. Configurer vos clés SSH GitHub

---

## ✅ Vérification

Après le déploiement, vérifier que le wiki est bien mis à jour :

🔗 **https://github.com/Bestsage/SITH_MISCHUNG_COMBUSTION/wiki**

Le script affichera :
```
✅ Wiki deployed successfully!
🔗 View at: https://github.com/Bestsage/SITH_MISCHUNG_COMBUSTION/wiki
```

---

## 🐛 Dépannage

### Problème : "command not found" sur Windows
**Solution :** Utiliser `deploy-wiki.bat` au lieu de `deploy-wiki.sh`

### Problème : "Permission denied"
**Solution :** 
- **Linux/macOS :** `chmod +x deploy-wiki.sh`
- **Windows :** Exécuter CMD/PowerShell en tant qu'administrateur

### Problème : "remote: Permission to wiki.git denied"
**Solution :** Vérifier vos permissions GitHub et votre authentification

### Problème : Le script ne trouve pas Git
**Solution :** 
- Vérifier que Git est installé : `git --version`
- Ajouter Git au PATH système

### Problème : "fatal: could not read Username"
**Solution :** Configurer Git :
```bash
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"
```

---

## 📝 Notes

- Les deux scripts (`.sh` et `.bat`) font exactement la même chose
- Le wiki est cloné dans un dossier temporaire et nettoyé après déploiement
- Si aucun changement n'est détecté, le déploiement est ignoré
- Les fichiers Markdown du dossier `wiki/` sont copiés vers le wiki GitHub

---

## 🆘 Besoin d'aide ?

Si vous rencontrez des problèmes :
1. Vérifier que Git est installé et configuré
2. Vérifier vos permissions sur le dépôt GitHub
3. Essayer le déploiement manuel (voir ci-dessus)
4. Ouvrir une issue sur GitHub avec les détails de l'erreur
