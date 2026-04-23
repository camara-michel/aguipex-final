# Démarrage et prise en compte des changements

## Prérequis

- Python 3 (un environnement virtuel `venv` est fourni à la racine)
- MySQL en cours d’exécution, avec la base et l’utilisateur indiqués dans `.env`
- Fichier `.env` à la racine du projet (copié depuis `.env.example` puis rempli)

## Première configuration

1. Aller à la racine du dépôt : `aguipex-allManagement/`
2. Activer le virtualenv :
   - Linux / macOS : `source venv/bin/activate`
   - Windows (cmd) : `venv\Scripts\activate.bat`
3. Installer les dépendances : `pip install -r requirements.txt`
4. Créer le fichier d’environnement :
   - `cp .env.example .env`
   - Éditer `.env` : `SECRET_KEY`, `DB_*`, e-mail, `DEBUG`, `ALLOWED_HOSTS` selon votre machine
5. Appliquer les migrations : `python manage.py migrate`
6. (Optionnel) Créer un super-utilisateur : `python manage.py createsuperuser`
7. (Optionnel) Collecter les fichiers statiques : `python manage.py collectstatic` (hors `DEBUG` ou en vue du déploiement)

Lancer le serveur de développement :

```bash
python manage.py runserver 0.0.0.0:8000
```

## Faire en sorte que les modifications soient prises en compte

| Situation | Que faire |
|-----------|-----------|
| **Modification de `settings.py` ou de `.env`** | Redémarrer tout processus Python qui sert l’appli (arrêter puis relancer `runserver`, ou recharger Gunicorn/uWSGI, ou redémarrer le conteneur Docker / le service systemd). Le fichier `.env` est lu **au démarrage** de Django, pas en continu. |
| **Modification de templates, vues, URLs** | Avec `runserver` : la plupart des changements sont rechargés automatiquement. En production : redéployer / redémarrer le worker selon votre hébergeur. |
| **Modification de fichiers statiques (`static/`)** | En dev : recharger la page (vider le cache du navigateur si besoin). Après gros changements : `python manage.py collectstatic` en production. |
| **Nouveaux champs de modèles** | `python manage.py makemigrations` puis `python manage.py migrate` |
| **Nouveaux paquets Python (`requirements.txt`)** | `pip install -r requirements.txt` puis redémarrer le serveur. |

## Vérifier rapidement la configuration

```bash
source venv/bin/activate
python manage.py check
```

Pour tester la connexion base de données (après configuration de `.env`) :

```bash
python manage.py migrate --plan
```

(ou `python manage.py dbshell` si `dbshell` est disponible pour MySQL)

## Fichier `.env`

- Il est listé dans `.gitignore` : ne pas le commiter.
- `SECRET_KEY`, mots de passe base et clés API doivent rester privés.
- En production, définir `DEBUG=False` et `ALLOWED_HOSTS` avec le domaine réel du site.
