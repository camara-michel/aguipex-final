# Prompt Cursor pour Créer la Logique de Gestion des Entreprises

## 🎯 Prompt Complet

```
Crée un système complet de gestion des entreprises pour une application Django avec les fonctionnalités suivantes :

## 1. MODÈLE ENTREPRISE

Crée un modèle `Entreprise` dans `core/models.py` avec :

### Champs obligatoires :
- `nom` : CharField(max_length=200) - Nom de l'entreprise
- `type_activite` : CharField(max_length=200) - Type d'activité
- `ville` : CharField(max_length=200) - Ville

### Champs optionnels :
- `slug` : SlugField(null=True, blank=True) - Généré automatiquement
- `description` : RichTextField(blank=True, null=True) - Description avec CKEditor
- `secteur_activite` : CharField(blank=True, null=True)
- `adresse` : RichTextField(blank=True, null=True) - Adresse avec CKEditor
- `telephone` : CharField(blank=True, null=True)
- `email` : EmailField(blank=True, null=True)
- `site_web` : CharField(max_length=500, blank=True, null=True)
- `logo` : ImageField(upload_to='LogoEntreprise', blank=True, null=True)
- `image_couverture` : ImageField(upload_to='ImageEntreprise', blank=True, null=True)
- `date_creation` : DateField(blank=True, null=True)
- `nombre_employes` : CharField(max_length=50, blank=True, null=True)
- `certifications` : RichTextField(blank=True, null=True) - Certifications avec CKEditor

### Relations :
- `foire` : ForeignKey('Foires', blank=True, null=True)

### Statut et métadonnées :
- `status` : CharField avec choices STATUS (('brouillon', 'Brouillon'), ('publier', 'Publier')), default='brouillon'
- `is_deleted` : BooleanField(default=False) - Soft delete
- `created_at` : DateTimeField(auto_now_add=True)
- `updated_at` : DateTimeField(auto_now=True)

### Méthode save() :
- Génère automatiquement le slug si absent : `slugify(nom) + "-" + str(shortuuid.uuid().lower()[:2])`
- Utilise `from django.utils.text import slugify` et `import shortuuid`

## 2. VUE FRONT-OFFICE : ENREGISTREMENT

Crée une vue `enregistrer_entreprise(request)` dans `core/views.py` :

### GET Request :
- Récupère tous les produits avec `status='publier'` et `is_deleted=False`
- Affiche le formulaire `templates/aguipex/enregistrer_entreprise.html`

### POST Request :
- **Validation** : Vérifie que `nom`, `type_activite`, `ville` sont remplis
- Si validation échoue : message d'erreur et retour au formulaire
- **Création** : Crée l'entreprise avec `status='brouillon'` (IMPORTANT)
- **Logo** : Gère l'upload du logo si fourni dans `request.FILES['logo']`
- **Produits** : Associe les produits sélectionnés (via `request.POST.getlist('produits')`)
  - Pour chaque produit_id : `produit.entreprise = entreprise` puis `produit.save()`
- **Message** : `messages.success(request, 'Votre entreprise a été enregistrée avec succès ! Elle sera publiée après validation par notre équipe.')`
- **Redirection** : Vers `redirect('aguipex-entreprises')`

### Gestion d'erreurs :
- Try/except avec message d'erreur générique si exception

## 3. VUE FRONT-OFFICE : LISTE

Crée une vue `entreprises(request)` dans `core/views.py` :

### Vérification session :
- Vérifie `request.session.get('visitor_info_submitted', False)`
- Si False : `redirect('collecte-info-visiteur')`

### Filtrage :
- Base : `Entreprise.objects.filter(status="publier", is_deleted=False)`
- **Recherche texte** (si `request.GET.get('q')`) :
  - Filtre sur : `nom`, `type_activite`, `secteur_activite`, `ville`, `description`
  - Utilise `Q()` objects avec `icontains`
- **Filtre produit** (si `request.GET.get('produit')`) :
  - Filtre sur `produits__title__icontains`
- Applique `.distinct()` pour éviter doublons
- Tri : `.order_by('-created_at')`

### Pagination :
- `Paginator(entreprises_list, 12)` - 12 entreprises par page
- Gère `PageNotAnInteger` et `EmptyPage`

### Contexte :
- `entreprises` : Page paginée
- `total_entreprises` : Nombre total
- `search_query` : Terme de recherche
- `produit_filter` : Produit filtré
- `produits_disponibles` : Liste pour le select (status='publier', is_deleted=False)

## 4. VUE FRONT-OFFICE : DÉTAIL

Crée une vue `entreprise_detail(request, slug)` dans `core/views.py` :

- Récupère l'entreprise avec `get_object_or_404(Entreprise, slug=slug, status="publier", is_deleted=False)`
- Récupère les produits : `Produit.objects.filter(entreprise=entreprise, status="publier", is_deleted=False).order_by('-created_at')`
- Contexte : `{'entreprise': entreprise, 'produits': produits}`
- Template : `templates/aguipex/entreprise_detail.html`

## 5. ADMIN DJANGO

### Formulaire personnalisé `EntrepriseAdminForm` dans `core/admin.py` :

```python
from ckeditor.widgets import CKEditorWidget
from django import forms

class EntrepriseAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(config_name='default'), required=False)
    adresse = forms.CharField(widget=CKEditorWidget(config_name='simple'), required=False)
    certifications = forms.CharField(widget=CKEditorWidget(config_name='default'), required=False)
    
    class Meta:
        model = Entreprise
        fields = '__all__'
```

### Admin `EntrepriseAdmin` :

- `form = EntrepriseAdminForm`
- `list_display = ('nom', 'type_activite', 'ville', 'telephone', 'email', 'status', 'is_deleted', 'created_at')`
- `list_filter = ('status', 'type_activite', 'ville')`
- `search_fields = ('nom', 'type_activite', 'ville', 'email')`
- `readonly_fields = ('created_at', 'updated_at')`
- `exclude = ('slug',)` - Slug généré automatiquement

### Fieldsets :
1. Informations générales : `nom`, `description`, `type_activite`, `secteur_activite`
2. Contact : `adresse`, `ville`, `telephone`, `email`, `site_web`
3. Images : `logo`, `image_couverture`
4. Informations complémentaires : `date_creation`, `nombre_employes`, `certifications`
5. Foire (optionnel) : `foire` (collapse)
6. Statut : `status`, `is_deleted`
7. Dates : `created_at`, `updated_at` (collapse)

### Permissions :
- Superuser : Accès complet
- Rôles `communication` ou `marketing` : Accès complet
- Autres : Pas d'accès

## 6. URLs

Dans `core/urls.py`, ajoute :

```python
path('entreprises/', views.entreprises, name='aguipex-entreprises'),
path('entreprises/<slug:slug>/', views.entreprise_detail, name='aguipex-entreprise-detail'),
path('enregistrer-entreprise/', views.enregistrer_entreprise, name='aguipex-enregistrer-entreprise'),
```

## 7. TEMPLATES

### Formulaire d'enregistrement (`templates/aguipex/enregistrer_entreprise.html`) :
- Formulaire multi-étapes (wizard) avec 5 étapes
- CKEditor pour `description`, `adresse`, `certifications`
- Configuration CKEditor : police Century Gothic, config complète pour description/certifications, simple pour adresse
- Sélection produits avec checkboxes
- Upload logo
- Validation JavaScript

### Liste (`templates/aguipex/entreprises.html`) :
- Grille responsive
- Barre de recherche
- Filtre par produit (select)
- Pagination
- Cartes entreprises avec logo, nom, type, ville

### Détail (`templates/aguipex/entreprise_detail.html`) :
- Header avec logo, nom, type, description
- Statistiques (ville, employés, date création, produits)
- Section "Informations de contact" avec cartes :
  - Adresse, Téléphone, Email, Site web
  - Design : cartes blanches, icônes vertes circulaires, labels en gris, valeurs en vert
  - Responsive : 2 colonnes desktop, 1 colonne mobile
- Section "Informations complémentaires" : secteur, certifications
- Liste produits associés
- Police Century Gothic partout (`var(--title-font, "Century Gothic", sans-serif)`)
- Filtres `|safe|unescape_html` pour les champs RichTextField

## 8. STYLES CSS

### Cartes de contact :
- Fond blanc, bordure subtile, ombre légère
- Icône : 48px, gradient vert, ombre
- Label : 0.7rem, uppercase, gris, letter-spacing 0.8px, margin-bottom 6px
- Valeur : 1rem, vert (#008d3f), line-height 1.4
- Téléphone : font-weight 600, letter-spacing 0.2px, white-space nowrap
- Responsive : padding réduit sur mobile, icône 44px

### Grille :
- Desktop : 2 colonnes fixes
- Tablette : 2 colonnes
- Mobile : 1 colonne
- Gap : 24px desktop, 20px tablette, 18px mobile

## 9. IMPORTANT

1. **Statut par défaut** : Toujours `'brouillon'` lors de la création front-office
2. **Slug unique** : Généré automatiquement avec shortuuid
3. **Filtrage strict** : Front-office ne montre que `status='publier'` et `is_deleted=False`
4. **CKEditor** : Utilisé pour description, adresse, certifications
5. **Police** : Century Gothic partout (charte graphique)
6. **Soft delete** : Utilise `is_deleted` au lieu de suppression réelle
7. **Association produits** : Via ForeignKey dans Produit vers Entreprise

## 10. DÉPENDANCES

- `django-ckeditor` : Pour RichTextField
- `shortuuid` : Pour génération slug unique
- `Pillow` : Pour images

Crée tout le code nécessaire avec gestion d'erreurs, validation, et design responsive.
```

---

## 📝 Notes d'utilisation

Ce prompt peut être utilisé dans Cursor pour recréer entièrement la logique de gestion des entreprises. Il contient tous les détails nécessaires :

- Structure du modèle
- Logique des vues
- Configuration admin
- URLs
- Templates
- Styles CSS
- Points importants à respecter

Copiez-collez ce prompt dans Cursor et il générera tout le code nécessaire.

