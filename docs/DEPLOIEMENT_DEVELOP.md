# Déploiement depuis la branche `develop`

Ce document décrit le cycle à suivre **après une modification** pour que le travail soit **sur la branche `develop` du dépôt distant** et **visible sur le site en ligne**. La branche **`master`** sert de **référence** pour l’ancienne version du site ; on ne l’utilise **pas** pour publier le site actuel.

---

## 1. Sur ton ordinateur (après avoir codé)

1. Vérifie que tu es sur **`develop`** :  
   `git branch` (l’astérisque doit être sur `develop`).

2. Enregistre tes changements :  
   ```bash
   git add .
   git commit -m "Description courte de la modification"
   ```

3. Envoie la branche **`develop`** vers le dépôt distant (GitHub, etc.) :  
   ```bash
   git push origin develop
   ```  
   Tant que cette étape n’est pas faite, le **serveur** ne peut pas récupérer ta dernière version.

---

## 2. Rôle de `master` (archive)

- **`develop`** = version **actuelle** du site, celle qu’on **déploie** en production.
- **`master`** = **sauvegarde** d’une version plus ancienne, pour comparaison ou retour en arrière manuel.  
- Tu **n’es pas obligé** de fusionner `develop` dans `master` à chaque livraison.  
  Si un jour tu veux figer l’état “archive” :  
  `git checkout master` puis `git merge develop` (ou un tag) — uniquement quand **tu** le décides.

---

## 3. Sur le serveur (site en ligne)

Connecte-toi en **SSH** au serveur, puis dans le dossier du projet, par exemple :

```bash
cd /home/ubuntu/aguipex-allManagement
```

Enchaîne (à adapter si ton chemin ou ta branche diffère) :

```bash
git fetch origin
git checkout develop
git pull origin develop
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
sudo systemctl restart backend.service
```

- **`git pull`** : aligne le code sur la dernière **`develop`** du dépôt.  
- **`migrate`** : applique les changements de base de données si le code en ajoute.  
- **`collectstatic`** : met à jour le dossier `staticfiles/` (CSS, JS, etc.) servi par Nginx.  
- **`restart backend.service`** : redémarre Gunicorn pour recharger le code Python et les templates.  
  *(Le nom du service peut varier : `systemctl list-units | grep -i gunicorn`.)*

Vérifie le site en **navigation privée** ou rechargement forcé (**Ctrl+F5**) pour limiter l’affichage d’une ancienne version en cache.

---

## 4. Résumé en une phrase

**Local :** `commit` sur `develop` → `git push origin develop`.  
**Serveur :** `git pull` sur `develop` → `migrate` → `collectstatic` → `restart` Gunicorn.

---

## 5. Rappel sur `.env`

Le fichier **`.env`** sur le serveur (secrets, BDD, `DEBUG`, etc.) ne doit en général **pas** être versionné. Après un `git pull`, contrôle qu’il est toujours correct ; ne le recopie jamais depuis le dépôt public sans vérification.
