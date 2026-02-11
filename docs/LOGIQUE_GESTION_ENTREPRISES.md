# Logique de Gestion des Entreprises - AGUIPEX

## 📋 Vue d'ensemble

Le système de gestion des entreprises permet aux entreprises de s'enregistrer via un formulaire front-office, avec validation par l'administration avant publication. Les entreprises peuvent être associées à des produits et des foires.

---

## 🏗️ Architecture

### 1. **Modèle Entreprise** (`core/models.py`)

```python
class Entreprise(models.Model):
    # Champs obligatoires
    nom = CharField(max_length=200)  # Nom de l'entreprise
    type_activite = CharField(max_length=200)  # Type d'activité
    ville = CharField(max_length=200)  # Ville
    
    # Champs optionnels
    slug = SlugField(null=True, blank=True)  # Généré automatiquement
    description = RichTextField(blank=True, null=True)  # CKEditor
    secteur_activite = CharField(blank=True, null=True)
    adresse = RichTextField(blank=True, null=True)  # CKEditor
    telephone = CharField(blank=True, null=True)
    email = EmailField(blank=True, null=True)
    site_web = CharField(max_length=500, blank=True, null=True)
    logo = ImageField(upload_to='LogoEntreprise', blank=True, null=True)
    image_couverture = ImageField(upload_to='ImageEntreprise', blank=True, null=True)
    date_creation = DateField(blank=True, null=True)
    nombre_employes = CharField(max_length=50, blank=True, null=True)
    certifications = RichTextField(blank=True, null=True)  # CKEditor
    
    # Relations
    foire = ForeignKey('Foires', blank=True, null=True)
    
    # Statut et métadonnées
    status = CharField(choices=STATUS, default='brouillon')  # 'brouillon' ou 'publier'
    is_deleted = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Génération automatique du slug si absent
        if not self.slug:
            self.slug = slugify(self.nom) + "-" + str(shortuuid.uuid().lower()[:2])
        super().save(*args, **kwargs)
```

**Points clés :**
- Slug généré automatiquement : `slugify(nom) + "-" + shortuuid[:2]`
- Statut par défaut : `'brouillon'` (nécessite validation admin)
- Champs RichTextField : `description`, `adresse`, `certifications` (CKEditor)
- Soft delete : `is_deleted` au lieu de suppression réelle

---

### 2. **Vue Front-Office : Enregistrement** (`core/views.py`)

#### Fonction : `enregistrer_entreprise(request)`

**Logique :**

1. **GET Request :**
   - Affiche le formulaire avec liste des produits disponibles
   - Produits filtrés : `status='publier'` et `is_deleted=False`

2. **POST Request :**
   - **Validation :** Vérifie que `nom`, `type_activite`, `ville` sont remplis
   - **Création :** Crée l'entreprise avec `status='brouillon'`
   - **Logo :** Gère l'upload du logo si fourni
   - **Produits :** Associe les produits sélectionnés à l'entreprise
   - **Message :** Affiche un message de succès avec mention de validation
   - **Redirection :** Vers la liste des entreprises

**Code clé :**
```python
# Validation
if not all([nom, type_activite, ville]):
    messages.error(...)
    return render(...)

# Création avec statut brouillon
entreprise = Entreprise.objects.create(
    nom=nom,
    type_activite=type_activite,
    ville=ville,
    # ... autres champs
    status='brouillon'  # IMPORTANT
)

# Association des produits
if produits_selectionnes:
    for produit_id in produits_selectionnes:
        produit = Produit.objects.get(id=produit_id)
        produit.entreprise = entreprise
        produit.save()
```

---

### 3. **Vue Front-Office : Liste** (`core/views.py`)

#### Fonction : `entreprises(request)`

**Logique :**

1. **Vérification session :** Redirige vers collecte d'infos visiteur si non soumis
2. **Filtrage :**
   - Uniquement `status='publier'` et `is_deleted=False`
   - Recherche par texte : `nom`, `type_activite`, `secteur_activite`, `ville`, `description`
   - Filtre par produit : `produits__title__icontains`
3. **Pagination :** 12 entreprises par page
4. **Tri :** Par date de création décroissante

**Code clé :**
```python
entreprises_list = Entreprise.objects.filter(
    status="publier", 
    is_deleted=False
)

# Recherche
if search_query:
    entreprises_list = entreprises_list.filter(
        Q(nom__icontains=search_query) |
        Q(type_activite__icontains=search_query) |
        # ...
    )

# Filtre produit
if produit_filter:
    entreprises_list = entreprises_list.filter(
        produits__title__icontains=produit_filter
    )
```

---

### 4. **Vue Front-Office : Détail** (`core/views.py`)

#### Fonction : `entreprise_detail(request, slug)`

**Logique :**

1. **Récupération :** Entreprise par slug avec filtres `status='publier'` et `is_deleted=False`
2. **Produits :** Récupère les produits associés (publiés et non supprimés)
3. **404 :** Si entreprise non trouvée ou non publiée

**Code clé :**
```python
entreprise = get_object_or_404(
    Entreprise, 
    slug=slug, 
    status="publier", 
    is_deleted=False
)

produits = Produit.objects.filter(
    entreprise=entreprise,
    status="publier",
    is_deleted=False
)
```

---

### 5. **Admin Django** (`core/admin.py`)

#### Formulaire personnalisé : `EntrepriseAdminForm`

- **CKEditor** pour `description` (config `default`)
- **CKEditor** pour `adresse` (config `simple`)
- **CKEditor** pour `certifications` (config `default`)

#### Admin : `EntrepriseAdmin`

**Configuration :**
- **Liste :** `nom`, `type_activite`, `ville`, `telephone`, `email`, `status`, `is_deleted`, `created_at`
- **Filtres :** `status`, `type_activite`, `ville`
- **Recherche :** `nom`, `type_activite`, `ville`, `email`
- **Readonly :** `created_at`, `updated_at`
- **Exclu :** `slug` (généré automatiquement)

**Fieldsets :**
1. Informations générales : `nom`, `description`, `type_activite`, `secteur_activite`
2. Contact : `adresse`, `ville`, `telephone`, `email`, `site_web`
3. Images : `logo`, `image_couverture`
4. Informations complémentaires : `date_creation`, `nombre_employes`, `certifications`
5. Foire (optionnel) : `foire`
6. Statut : `status`, `is_deleted`
7. Dates : `created_at`, `updated_at`

**Permissions :**
- Superuser : Accès complet
- Rôles `communication` ou `marketing` : Accès complet
- Autres : Pas d'accès

---

### 6. **URLs** (`core/urls.py`)

```python
path('entreprises/', views.entreprises, name='aguipex-entreprises'),
path('entreprises/<slug:slug>/', views.entreprise_detail, name='aguipex-entreprise-detail'),
path('enregistrer-entreprise/', views.enregistrer_entreprise, name='aguipex-enregistrer-entreprise'),
```

---

## 🔄 Workflow

### Enregistrement Front-Office

```
1. Utilisateur accède à /enregistrer-entreprise/
2. Remplit le formulaire (nom, type_activité, ville obligatoires)
3. Sélectionne des produits (optionnel)
4. Soumet le formulaire
5. Entreprise créée avec status='brouillon'
6. Message : "Votre entreprise a été enregistrée avec succès ! Elle sera publiée après validation par notre équipe."
7. Redirection vers /entreprises/
```

### Validation Admin

```
1. Admin accède à l'interface Django Admin
2. Voit l'entreprise avec status='brouillon'
3. Vérifie/modifie les informations
4. Change status de 'brouillon' à 'publier'
5. Entreprise devient visible sur le site
```

### Affichage Front-Office

```
1. Liste : /entreprises/
   - Affiche uniquement status='publier' et is_deleted=False
   - Recherche et filtres disponibles
   - Pagination (12 par page)

2. Détail : /entreprises/<slug>/
   - Affiche l'entreprise si status='publier' et is_deleted=False
   - Affiche les produits associés
   - 404 si non trouvé ou non publié
```

---

## 🎨 Templates

### 1. **Formulaire d'enregistrement** (`templates/aguipex/enregistrer_entreprise.html`)

- Formulaire multi-étapes (wizard)
- CKEditor pour `description`, `adresse`, `certifications`
- Sélection de produits (checkboxes)
- Upload de logo
- Validation JavaScript côté client

### 2. **Liste des entreprises** (`templates/aguipex/entreprises.html`)

- Grille responsive
- Barre de recherche
- Filtre par produit
- Pagination
- Cartes d'entreprises avec logo, nom, type, ville

### 3. **Détail entreprise** (`templates/aguipex/entreprise_detail.html`)

- Header avec logo, nom, type, description
- Statistiques (ville, employés, date création, produits)
- Informations de contact (adresse, téléphone, email, site web)
- Informations complémentaires (secteur, certifications)
- Liste des produits associés
- Police Century Gothic partout
- Design responsive avec cartes de contact

---

## 🔐 Sécurité et Validation

1. **Validation côté serveur :** Champs obligatoires vérifiés
2. **Statut brouillon :** Les entreprises non validées ne sont pas visibles
3. **Soft delete :** `is_deleted` au lieu de suppression réelle
4. **Permissions admin :** Seuls certains rôles peuvent modifier
5. **Filtrage strict :** Front-office ne montre que `status='publier'` et `is_deleted=False`

---

## 📦 Dépendances

- `django-ckeditor` : Pour les champs RichTextField
- `shortuuid` : Pour génération de slug unique
- `Pillow` : Pour gestion des images

---

## 🎯 Points importants

1. **Slug unique :** Généré automatiquement avec `slugify(nom) + "-" + shortuuid[:2]`
2. **Statut par défaut :** Toujours `'brouillon'` lors de la création front-office
3. **Validation admin :** Nécessaire pour passer à `'publier'`
4. **CKEditor :** Utilisé pour `description`, `adresse`, `certifications`
5. **Association produits :** Via ForeignKey dans Produit vers Entreprise
6. **Police :** Century Gothic partout (charte graphique)
7. **Responsive :** Design adaptatif pour mobile/tablette/desktop

