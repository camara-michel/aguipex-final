# 📋 Modal de Collecte d'Informations - AGUIPEX

## 🎯 Description

Ce système permet de collecter les informations des visiteurs avant qu'ils puissent accéder à la liste des entreprises sur le site AGUIPEX. Lorsqu'un utilisateur clique sur le menu "Entreprises", un modal s'ouvre pour collecter ses informations personnelles.

## ✨ Fonctionnalités

- **Modal automatique** : S'ouvre automatiquement lors du clic sur "Entreprises"
- **Formulaire complet** : Collecte nom, email, pays, ville et téléphone
- **Validation** : Champs obligatoires avec validation côté client et serveur
- **Persistance** : Les informations sont sauvegardées en base de données
- **Session** : L'utilisateur n'a pas besoin de remplir le formulaire à nouveau
- **Responsive** : S'adapte aux écrans mobiles et desktop
- **Accessibilité** : Support des lecteurs d'écran et navigation clavier

## 🏗️ Architecture Technique

### Backend (Django)
- **Modèle** : `Visiteur` dans `core/models.py`
- **Vue** : `soumettre_info_visiteur` dans `core/views.py`
- **URL** : `/soumettre-info-visiteur/` dans `core/urls.py`
- **Admin** : Interface d'administration en lecture seule

### Frontend (JavaScript/CSS)
- **JavaScript** : `static/assets/js/visitor-modal.js`
- **CSS** : `static/assets/css/visitor-modal.css`
- **Dépendances** : Bootstrap 5, FontAwesome, SweetAlert2

## 📁 Structure des Fichiers

```
aguipex-allManagement/
├── core/
│   ├── models.py              # Modèle Visiteur
│   ├── views.py               # Vue de soumission
│   ├── admin.py               # Configuration admin
│   └── migrations/
│       └── 0008_visiteur.py  # Migration du modèle
├── static/
│   ├── assets/
│   │   ├── js/
│   │   │   └── visitor-modal.js    # Logique du modal
│   │   └── css/
│   │       └── visitor-modal.css   # Styles du modal
└── templates/
    └── partials/
        └── base.html          # Template principal
```

## 🚀 Installation

### 1. Créer et appliquer la migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Inclure les fichiers statiques
Ajouter dans votre template principal (`base.html`) :

```html
<!-- CSS du modal -->
<link rel="stylesheet" href="{% static 'assets/css/visitor-modal.css' %}">

<!-- JavaScript du modal -->
<script src="{% static 'assets/js/visitor-modal.js' %}"></script>
```

### 3. Vérifier les dépendances
Assurez-vous que ces packages sont installés :
- Bootstrap 5
- FontAwesome
- SweetAlert2

## 🔧 Configuration

### Variables d'environnement
Aucune variable d'environnement spécifique n'est requise.

### Paramètres Django
Le système utilise les sessions Django par défaut. Assurez-vous que :
- `MIDDLEWARE` contient `'django.contrib.sessions.middleware.SessionMiddleware'`
- `INSTALLED_APPS` contient `'django.contrib.sessions'`

## 📱 Utilisation

### Pour l'utilisateur
1. Cliquer sur le menu "Entreprises"
2. Remplir le formulaire avec ses informations
3. Soumettre le formulaire
4. Être redirigé vers la liste des entreprises

### Pour l'administrateur
1. Accéder à l'interface d'administration Django
2. Section "Visiteurs" pour consulter les données collectées
3. Les données sont en lecture seule pour la sécurité

## 🎨 Personnalisation

### Modifier les champs
Éditer le modèle `Visiteur` dans `core/models.py` et mettre à jour le formulaire dans `visitor-modal.js`.

### Changer le style
Modifier `visitor-modal.css` pour personnaliser l'apparence.

### Ajouter des validations
Étendre la logique de validation dans `visitor-modal.js` et `views.py`.

## 🔒 Sécurité

- **CSRF Protection** : Incluse automatiquement par Django
- **Validation** : Côté client et serveur
- **Admin en lecture seule** : Empêche la modification manuelle des données
- **Session sécurisée** : Utilise les sessions Django sécurisées
- **IP tracking** : Enregistre l'adresse IP pour la traçabilité

## 📊 Statistiques

Le système collecte automatiquement :
- Nombre de visiteurs
- Pays d'origine
- Villes de résidence
- Dates de visite
- Adresses IP (pour la traçabilité)

## 🐛 Dépannage

### Le modal ne s'ouvre pas
- Vérifier que Bootstrap est chargé
- Vérifier la console du navigateur pour les erreurs JavaScript
- S'assurer que les fichiers statiques sont bien servis

### Erreur lors de la soumission
- Vérifier que la migration est appliquée
- Vérifier les logs Django
- S'assurer que la base de données est accessible

### Problèmes de style
- Vérifier que le CSS est bien chargé
- Vérifier la compatibilité avec le thème existant
- Tester sur différents navigateurs

## 🔄 Mise à Jour

### Ajouter de nouveaux champs
1. Modifier le modèle `Visiteur`
2. Créer et appliquer une nouvelle migration
3. Mettre à jour le formulaire JavaScript
4. Mettre à jour la vue Django

### Modifier la logique
1. Éditer `visitor-modal.js` pour le frontend
2. Éditer `views.py` pour le backend
3. Tester les modifications

## 📞 Support

Pour toute question ou problème :
- Vérifier la documentation Django
- Consulter les logs du serveur
- Tester dans un environnement de développement

## 📝 Notes de Version

- **v1.0** : Implémentation initiale avec collecte des informations de base
- **Futur** : Possibilité d'ajouter des champs personnalisés et des validations avancées

---

**Développé pour AGUIPEX** - Système de Gestion des Entreprises Guinéennes
