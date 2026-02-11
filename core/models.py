from django.db import models
from django.db.models import Q
from django.conf import settings
from shortuuid.django_fields import ShortUUIDField
from django.utils import timezone
from django.utils.text import slugify
import shortuuid
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
import os
from ckeditor.fields import RichTextField

STATUS_PROJET = (
    ('brouillon', 'Brouillon'),
    ('en_cours', 'En cours'),
    ('termine', 'Terminé'),
)

STATUS = (
    ('brouillon', 'Brouillon'),
    ('publier', 'Publier')
)

RATING = (
    (1, '★✩✩✩'),
    (2, '★★✩✩✩'),
    (3, '★★★✩✩'),
    (4, '★★★★✩'),
    (5, '★★★★★'),
)

TYPE_FOIRE = (
    ('FOIRE_INTERNATIONALE', 'Foire Internationale'),
    ('FOIRE_NATIONALE', 'Foire Nationale')
)

VOIE_EXPOITATION = (
    ('transport_terrestre', 'Transport Terrestre'),
    ('transport_maritime', 'Transport Maritime'),
    ('transport_aerien', 'Transport Aérien'),
)


REALISATION = (
    ('en_cours', 'En cours'),
    ('terminer', 'Terminer')
)

def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg']
    if ext not in valid_extensions:
        raise ValidationError("Seuls les fichiers JPG, PNG, GIF et SVG sont autorisés.")


class Slide(models.Model):
    title = models.CharField(max_length=191)
    subtitle = models.CharField(max_length=191)
    description = models.TextField(null=True, blank=True)
    libelle = models.CharField(max_length=191)
    lien = models.CharField(max_length=191)
    lien_video = models.CharField(max_length=191, blank=True, null=True)
    image = models.ImageField(upload_to="slide_image")
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Slide'
        verbose_name_plural = 'Slides'

class QuiSommeNous(models.Model):
    titre = models.CharField(max_length=200)
    detail = RichTextField()
    contenu1 = models.CharField(max_length=100, blank=True, null=True)
    contenu2 = models.CharField(max_length=100, blank=True, null=True)
    contenu3 = models.CharField(max_length=100, blank=True, null=True)
    contenu4 = models.CharField(max_length=100, blank=True, null=True)
    contenu5 = models.CharField(max_length=100, blank=True, null=True)
    nombreAnnee = models.CharField(max_length=10, blank=True, null=True)
    texteAnne = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.titre
    
    class Meta:
        verbose_name = 'Qui sommes nous ?'

    class Meta:
        verbose_name_plural = 'Qui sommes nous ?'

class Ville(models.Model):
    name = models.CharField(max_length=191)
    lat = models.FloatField()
    lng = models.FloatField()

    def __str__(self):
        return self.name


class TypeProduit(models.Model):
    """Type de produit (ex: Agroalimentaire, Textile, Artisanat, etc.)"""
    nom = models.CharField(max_length=200, verbose_name="Nom du type de produit", unique=True)
    slug = models.SlugField(max_length=191, null=True, blank=True, unique=True)
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    icone = models.CharField(max_length=100, blank=True, null=True, verbose_name="Icône (classe FontAwesome)")
    ordre = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    status = models.CharField(max_length=10, choices=STATUS, default='publier')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Type de produit'
        verbose_name_plural = 'Types de produits'
        ordering = ['ordre', 'nom']


class Entreprise(models.Model):
    nom = models.CharField(max_length=200, verbose_name="Nom de l'entreprise")
    slug = models.SlugField(max_length=191, null=True, blank=True)
    description = RichTextField(verbose_name="Description de l'entreprise", blank=True, null=True)
    type_activite = models.CharField(max_length=200, verbose_name="Type d'activité")
    secteur_activite = models.CharField(max_length=150, verbose_name="Secteur d'activité", blank=True, null=True)
    adresse = RichTextField(verbose_name="Adresse complète", blank=True, null=True)
    ville = models.CharField(max_length=200, verbose_name="Ville")
    telephone = models.CharField(max_length=20, verbose_name="Téléphone", blank=True, null=True)
    email = models.EmailField(verbose_name="Adresse email", blank=True, null=True)
    site_web = models.CharField(max_length=500, blank=True, null=True, verbose_name="Site web")
    logo = models.ImageField(upload_to='LogoEntreprise', blank=True, null=True, verbose_name="Logo de l'entreprise")
    image_couverture = models.ImageField(upload_to='ImageEntreprise', blank=True, null=True, verbose_name="Image de couverture")
    date_creation = models.DateField(blank=True, null=True, verbose_name="Date de création de l'entreprise")
    nombre_employes = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nombre d'employés")
    certifications = RichTextField(blank=True, null=True, verbose_name="Certifications obtenues")
    foire = models.ForeignKey('Foires', on_delete=models.CASCADE, related_name='entreprise_foire', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom) + "-" + str(shortuuid.uuid().lower()[:2])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Entreprise'
        verbose_name_plural = 'Entreprises'


class ProduitEntreprise(models.Model):
    """Produit d'une entreprise - Nouveau modèle indépendant"""
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='produits_entreprise', verbose_name="Entreprise")
    type_produit = models.ForeignKey(TypeProduit, on_delete=models.SET_NULL, related_name='produits', null=True, verbose_name="Type de produit")
    nom = models.CharField(max_length=200, verbose_name="Nom du produit")
    description_courte = models.TextField(max_length=500, verbose_name="Description courte", help_text="Maximum 500 caractères")
    image = models.ImageField(upload_to='ProduitsEntreprise', verbose_name="Image du produit")
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.nom} - {self.entreprise.nom}"

    class Meta:
        verbose_name = 'Produit entreprise'
        verbose_name_plural = 'Produits entreprises'
        ordering = ['-created_at']


class Produit(models.Model):
    title = models.CharField(max_length=191)
    description = RichTextField(null=True, blank=True)
    image = models.ImageField(upload_to='ImageProduits', null=True, blank=True)
    couleur = models.CharField(max_length=20, default='blue')
    fiche_produit = models.ImageField(upload_to='FicheProduit', null=True, blank=True)
    featured = models.BooleanField(default=False)
    pour_site = models.BooleanField(default=True)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='produits', verbose_name="Entreprise productrice", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    villes = models.ManyToManyField(Ville, related_name='produits')  # <- liaison produit ↔ ville

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'


class Programme(models.Model):
    nom = models.CharField(max_length=191)
    slug = models.SlugField(max_length=191, null=True, blank=True)
    accronyme = models.CharField(max_length=191, blank=True, null=True)
    paragraphe1 = models.CharField(max_length=150)
    description1 = RichTextField(blank=True, null=True)
    paragraphe2 = models.CharField(max_length=150)
    description2 = RichTextField(blank=True, null=True)
    axe1 = models.CharField(max_length=100, blank=True, null=True)
    axe2 = models.CharField(max_length=100, blank=True, null=True)
    axe3 = models.CharField(max_length=100, blank=True, null=True)
    axe4 = models.CharField(max_length=100, blank=True, null=True)
    axe5 = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='ImageProgramme', null=True, blank=True)
    logo = models.ImageField(upload_to='Logo', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = 'Programme'
        verbose_name_plural = 'Programmes'

    def save(self, *args, **kwargs):
        if not self.slug :
            self.slug = slugify(self.nom) + "-" + str(shortuuid.uuid().lower()[:2])
        super().save(*args, **kwargs)


class Evenement(models.Model):
    title = models.CharField(max_length=191)
    slug = models.SlugField(max_length=191, null=True, blank=True)
    image = models.ImageField(upload_to="Image", null=True, blank=True)
    image_detail = models.ImageField(upload_to="ImageDetail", null=True, blank=True)
    date_evenement = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    featured = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug :
            self.slug = slugify(self.title) + "-" + str(shortuuid.uuid().lower()[:2])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Événement'
        verbose_name_plural = 'Événements'

class Partenaire(models.Model):
    logo = models.ImageField(upload_to='Logo', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = 'Partenaire'
        verbose_name_plural = 'Partenaires'

class Temoignage(models.Model):
    name = models.CharField(max_length=191)
    fonction = models.CharField(max_length=191)
    notation = models.IntegerField(choices=RATING, default=None)
    image = models.ImageField(upload_to="ImageTemoignage")  # Chemin ou nom de l'image
    contenu = RichTextField()
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Témoignage'
        verbose_name_plural = 'Témoignages'


class MotDirecteur(models.Model):
    titre = models.CharField(max_length=150)
    image = models.ImageField(upload_to="ImageDG")
    contenu  = RichTextField()
    nomDG = models.CharField(max_length=150)
    poste = models.CharField(max_length=150)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.titre

    class Meta:
        verbose_name = 'Mot du DG'
        verbose_name_plural = 'Mot du DG'
    
class VisionMission(models.Model):
    texte_mission = models.CharField(max_length=150)
    texte_vision = models.CharField(max_length=150)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.texte_mission

    class Meta:
        verbose_name = 'Vision et mission'
        verbose_name_plural = 'Vision et mission'

class Valeur(models.Model):
    image = models.ImageField(upload_to="IconeValeur", blank=True, null=True, verbose_name="Icone")
    titre = models.CharField(max_length=150)
    numero = models.CharField(max_length=150)
    contenu = RichTextField()
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.titre

    class Meta:
        verbose_name = 'Valeur'
        verbose_name_plural = 'Valeurs'

class Gouvernance(models.Model):
    nom = models.CharField(max_length=150)
    poste = models.CharField(max_length=150)
    contenu = RichTextField()
    image = models.ImageField(upload_to="GourvernanceImage", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    
    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = 'Gouvernance'
        verbose_name_plural = 'Gouvernances'


class ActivityFoire(models.Model):
    title = models.CharField(max_length=191)
    slug = models.SlugField(max_length=191, null=True, blank=True)
    description = RichTextField(null=True, blank=True)
    realisation = models.CharField(max_length=191, choices=REALISATION, default="en_cours")
    image = models.ImageField(upload_to="ImageActivities", null=True, blank=True)
    date_activitie = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    featured = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)
    
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug :
            self.slug = slugify(self.title) + "-" + str(shortuuid.uuid().lower()[:2])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Activité'
        verbose_name_plural = 'Activités'
        
        
class CategorieActuality(models.Model):
    name = models.CharField(max_length=191)
    slug = models.SlugField(max_length=191, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name='Est supprimé')  # Marquer comme supprimé
    featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + "-" + str(shortuuid.uuid().lower()[:2])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Catégorie d'actualité"
        verbose_name_plural = "Catégorie d'actualités"

    

class Contact(models.Model):
    name = models.CharField(max_length=191, verbose_name="Nom complet")
    phone = models.CharField(max_length=191, verbose_name="Numéro de téléphone", blank=True, null=True)
    email = models.EmailField(max_length=191)
    subject = models.CharField(max_length=191, verbose_name="Sujet")
    message = RichTextField()
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True ,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True ,null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
    
# class Departement(models.Model):
#     name = models.CharField(max_length=191)
#     slug = models.SlugField(max_length=191, null=True, blank=True)
#     status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
#     featured = models.BooleanField(default=True)
#     created_at = models.DateTimeField(null=True, blank=True)
#     updated_at = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return self.name
    
#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.name) + "-" + str(shortuuid.uuid().lower()[:2])
#         super().save(*args, **kwargs)
    
class Equipe(models.Model):
    name = models.CharField(max_length=191)
    slug = models.SlugField(max_length=191, null=True, blank=True)
    fonction = models.CharField(max_length=191)
    image = models.ImageField(upload_to="ImageEquipe", null=True, blank=True)
    lien1 = models.CharField(max_length=191, null=True, blank=True)
    lien2 = models.CharField(max_length=191, null=True, blank=True)
    # lien3 = models.CharField(max_length=191, null=True, blank=True)
    reseau1 = models.CharField(max_length=100, null=True, blank=True)
    reseau2 = models.CharField(max_length=100, null=True, blank=True)
    # reseau3 = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=191)
    contact = models.CharField(max_length=191)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    featured = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True ,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True ,null=True, blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + "-" + str(shortuuid.uuid().lower()[:2])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Equipe'
        verbose_name_plural = 'Equipes'


class Interprofession(models.Model):
    """Interprofession (organisation par filière)."""
    nom = models.CharField(max_length=200, verbose_name="Nom de l'interprofession")
    code = models.CharField(max_length=50, unique=True, verbose_name="Code (identifiant unique)")
    description = RichTextField(verbose_name="Description", blank=True, null=True, help_text="Description détaillée de l'interprofession")
    slug = models.SlugField(max_length=220, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.nom} ({self.code})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom) + "-" + str(shortuuid.uuid().lower()[:4])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Interprofession'
        verbose_name_plural = 'Interprofessions'


class PersonnelInterprofession(models.Model):
    """Personnel rattaché à une interprofession."""
    interprofession = models.ForeignKey(
        Interprofession,
        on_delete=models.CASCADE,
        related_name='personnels',
        verbose_name="Interprofession"
    )
    nom = models.CharField(max_length=150, verbose_name="Nom")
    prenom = models.CharField(max_length=150, verbose_name="Prénom")
    localisation = models.CharField(max_length=200, verbose_name="Localisation", blank=True, null=True)
    email = models.EmailField(verbose_name="Adresse email", blank=True, null=True)
    poste = models.CharField(max_length=200, verbose_name="Poste dans l'interprofession", blank=True, null=True)
    profession = models.CharField(max_length=200, verbose_name="Profession", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.prenom} {self.nom} — {self.interprofession.nom}"

    class Meta:
        verbose_name = 'Personnel interprofession'
        verbose_name_plural = 'Personnels des interprofessions'
        ordering = ['nom', 'prenom']


class Projet(models.Model):
    """Projet AGUIPEX ; responsable saisi manuellement (nom et poste)."""
    title = models.CharField(max_length=255, verbose_name="Titre du projet")
    slug = models.SlugField(max_length=280, null=True, blank=True)
    description = RichTextField(verbose_name="Description", blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_PROJET,
        default='brouillon',
        verbose_name="Statut"
    )
    start_date = models.DateField(verbose_name="Date de début", null=True, blank=True)
    end_date = models.DateField(verbose_name="Date de fin", null=True, blank=True)
    responsable_nom = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Nom du responsable du projet"
    )
    responsable_poste = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Poste du responsable"
    )
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) + "-" + str(shortuuid.uuid().lower()[:4])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Projet'
        verbose_name_plural = 'Projets'
        ordering = ['-created_at']


class EtapeProjet(models.Model):
    """Étape ou évolution liée à un projet (affichée sur le site)."""
    projet = models.ForeignKey(
        Projet,
        on_delete=models.CASCADE,
        related_name='etapes',
        verbose_name="Projet"
    )
    titre = models.CharField(max_length=200, verbose_name="Titre de l'étape")
    description = RichTextField(verbose_name="Description", blank=True, null=True)
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    date_etape = models.DateField(verbose_name="Date", null=True, blank=True)
    pourcentage = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Pourcentage d'avancement (%)",
        help_text="Valeur entre 0 et 100 (optionnel)",
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.projet.title} — {self.titre}"

    class Meta:
        verbose_name = 'Étape de projet'
        verbose_name_plural = 'Étapes de projet'
        ordering = ['ordre', 'date_etape', 'created_at']


# =============================================================================
# MANIFESTATIONS COMMERCIALES — Système complet (Back + Front)
# =============================================================================
# Règles : 4 étapes FIXES par manifestation (créées auto), pas d'ajout/suppression
# par l'admin. Chaque étape a date_debut et date_fin. Candidature initiale :
# étape A_POSTULER, statut_metier REFUS, statut_back_office BROUILLON.
# Transition uniquement via ACCEPTER (→ étape suivante + ACCEPTE + notification)
# ou REFUSER (→ reste + REFUS + notification).
# =============================================================================

# Statut global de la manifestation (pilote affichage Front et ouverture postulation)
STATUT_MANIFESTATION_GLOBAL = (
    ('bientot_prevu', 'Bientôt prévu'),           # BIENTOT_PREVU → étape 1 seule
    ('a_postuler', 'À postuler'),                 # A_POSTULER → étapes 1+2, bouton Postuler
    ('selection_terminee', 'Sélection terminée'),  # SELECTION_TERMINEE → 1+2+3
    ('manifestation_terminee', 'Manifestation terminée'),  # toutes les étapes
)

# Statut métier candidature : REFUS (initial ou après refus admin), ACCEPTE (après acceptation)
STATUT_METIER_CANDIDATURE = (
    ('refus', 'Refus'),
    ('accepte', 'Accepté'),
)

# Statut back office : visibilité / validation admin uniquement
STATUT_BACK_OFFICE_CANDIDATURE = (
    ('brouillon', 'Brouillon'),
    ('publie', 'Publié'),
)

# Décision admin (traçabilité)
DECISION_ADMIN_CANDIDATURE = (
    ('accepter', 'Accepter'),
    ('refuser', 'Refuser'),
)

# Libellés des 4 étapes FIXES (ordre 1 à 4), créées automatiquement
ETAPES_MANIFESTATION_FIXES = [
    (1, 'Bientôt prévu'),
    (2, 'À postuler'),
    (3, 'Sélection terminée'),
    (4, 'Manifestation terminée'),
]

# Ordre max affiché au Front selon statut global
MAX_ORDRE_ETAPE_PAR_STATUT = {
    'bientot_prevu': 1,
    'a_postuler': 2,
    'selection_terminee': 3,
    'manifestation_terminee': 4,
}

# Filtre commun : candidatures visibles sur le Front (publiées, acceptées ou refusées)
# Chaque manifestation affiche les entreprises selon ce statut : accepté et refus (après décision admin).
CANDIDATURES_VISIBLES_FRONT_Q = Q(
    statut_back_office='publie',
    statut_metier__in=['accepte', 'refus'],
    is_deleted=False,
)


class ManifestationCommerciale(models.Model):
    """
    Manifestation commerciale créée uniquement en Back Office.
    Les 4 étapes sont créées automatiquement (signal post_save) avec date_debut/date_fin.
    """
    titre = models.CharField(max_length=255, verbose_name="Titre")
    slug = models.SlugField(max_length=280, null=True, blank=True)
    description = RichTextField(verbose_name="Description", blank=True, null=True)
    conditions_de_participation = RichTextField(verbose_name="Conditions de participation", blank=True, null=True, help_text="Conditions et critères requis pour participer à cette manifestation")
    statut_global = models.CharField(
        max_length=30,
        choices=STATUT_MANIFESTATION_GLOBAL,
        default='bientot_prevu',
        verbose_name="Statut global"
    )
    statut_publication = models.CharField(
        max_length=10,
        choices=STATUS,
        default='brouillon',
        verbose_name="Publication (Front Office)"
    )
    date_debut = models.DateField(verbose_name="Date de début", null=True, blank=True)
    date_fin = models.DateField(verbose_name="Date de fin", null=True, blank=True)
    lieu = models.CharField(max_length=200, verbose_name="Lieu", blank=True, null=True)
    pays = models.CharField(max_length=100, verbose_name="Pays", blank=True, null=True)
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre) + "-" + str(shortuuid.uuid().lower()[:4])
        super().save(*args, **kwargs)

    def get_candidatures_visibles_front(self):
        """
        Retourne les candidatures de cette manifestation visibles sur le Front Office
        selon le statut : publiées, acceptées ou refusées (CANDIDATURES_VISIBLES_FRONT_Q).
        """
        return self.candidatures.filter(CANDIDATURES_VISIBLES_FRONT_Q)

    class Meta:
        verbose_name = 'Manifestation commerciale'
        verbose_name_plural = 'Manifestations commerciales'
        ordering = ['-date_debut', '-created_at']


class EtapeManifestation(models.Model):
    """
    Étape du wizard : exactement 4 étapes FIXES par manifestation (ordre 1 à 4).
    Créées automatiquement ; l'admin ne peut ni ajouter, ni supprimer, ni réordonner.
    Chaque étape possède date_debut et date_fin.
    """
    manifestation = models.ForeignKey(
        ManifestationCommerciale,
        on_delete=models.CASCADE,
        related_name='etapes',
        verbose_name="Manifestation"
    )
    ordre = models.PositiveIntegerField(verbose_name="Ordre (1 à 4)", validators=[MinValueValidator(1), MaxValueValidator(4)])
    titre = models.CharField(max_length=200, verbose_name="Titre de l'étape")
    description = RichTextField(verbose_name="Description", blank=True, null=True)
    date_debut = models.DateField(verbose_name="Date de début", null=True, blank=True)
    date_fin = models.DateField(verbose_name="Date de fin", null=True, blank=True)
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.manifestation.titre} — Étape {self.ordre}: {self.titre}"

    def get_candidatures_passees_par_etape(self):
        """
        Retourne toutes les candidatures qui sont passées par cette étape (via l'historique),
        filtrées selon le statut back office 'publié' et statut métier 'accepte' ou 'refus'.
        Utilise l'historique pour trouver toutes les candidatures, même si elles sont maintenant à une autre étape.
        """
        # Récupérer toutes les candidatures qui ont une entrée dans l'historique pour cette étape
        candidatures_ids = CandidatureEtapeHistorique.objects.filter(
            etape=self
        ).values_list('candidature_id', flat=True).distinct()
        
        # Filtrer selon les critères de visibilité : publiées, acceptées ou refusées
        return CandidatureManifestation.objects.filter(
            id__in=candidatures_ids,
            manifestation=self.manifestation,
            statut_back_office='publie',
            statut_metier__in=['accepte', 'refus'],
            is_deleted=False,
        ).distinct()

    class Meta:
        verbose_name = 'Étape de manifestation'
        verbose_name_plural = 'Étapes de manifestation'
        ordering = ['manifestation', 'ordre']
        unique_together = [['manifestation', 'ordre']]


class CandidatureManifestation(models.Model):
    """
    Candidature d'une entreprise à une manifestation.
    À la postulation : étape A_POSTULER (ordre 2), statut_metier REFUS, statut_back_office BROUILLON.
    Transition uniquement via décision admin (ACCEPTER → étape suivante + ACCEPTE + notification).
    """
    manifestation = models.ForeignKey(
        ManifestationCommerciale,
        on_delete=models.CASCADE,
        related_name='candidatures',
        verbose_name="Manifestation"
    )
    entreprise = models.ForeignKey(
        'Entreprise',
        on_delete=models.CASCADE,
        related_name='candidatures_manifestation',
        verbose_name="Entreprise",
        null=True,
        blank=True
    )
    nom_entreprise = models.CharField(max_length=200, verbose_name="Nom de l'entreprise", blank=True, null=True)
    email_contact = models.EmailField(verbose_name="Email du contact", blank=True, null=True)
    telephone_contact = models.CharField(max_length=30, verbose_name="Téléphone", blank=True, null=True)
    message = models.TextField(verbose_name="Message", blank=True, null=True)
    statut_metier = models.CharField(
        max_length=20,
        choices=STATUT_METIER_CANDIDATURE,
        default='refus',
        verbose_name="Statut métier"
    )
    statut_back_office = models.CharField(
        max_length=10,
        choices=STATUT_BACK_OFFICE_CANDIDATURE,
        default='brouillon',
        verbose_name="Statut back office"
    )
    etape_actuelle = models.ForeignKey(
        EtapeManifestation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='candidatures_etape',
        verbose_name="Étape actuelle"
    )
    date_candidature = models.DateTimeField(auto_now_add=True, verbose_name="Date de candidature")
    # Champs supplémentaires pour le formulaire de postulation (tous optionnels)
    nombre_personnes = models.PositiveIntegerField(verbose_name="Nombre de personnes dans l'entreprise", blank=True, null=True)
    produits_entreprise = models.TextField(verbose_name="Produits de l'entreprise", blank=True, null=True, help_text="Liste des produits proposés par l'entreprise")
    domaine_activite = models.CharField(max_length=200, verbose_name="Domaine d'activité", blank=True, null=True)
    a_rccm = models.BooleanField(verbose_name="Avez-vous un RCCM ?", default=False)
    a_code_nif = models.BooleanField(verbose_name="Avez-vous un code NIF à jour ?", default=False)
    type_entreprise = models.CharField(max_length=100, verbose_name="Type d'entreprise", blank=True, null=True, help_text="Ex: SARL, SA, EURL, etc.")
    responsable_entreprise = models.CharField(max_length=200, verbose_name="Responsable de l'entreprise", blank=True, null=True)
    date_creation_entreprise = models.DateField(verbose_name="Date de création de l'entreprise", blank=True, null=True)
    nombre_manifestations_participees = models.PositiveIntegerField(verbose_name="À combien de manifestations commerciales avez-vous déjà participé ?", blank=True, null=True, default=0)
    peut_se_financer = models.BooleanField(verbose_name="Pouvez-vous vous financer ?", default=False)
    siege_social = models.TextField(verbose_name="Siège social de l'entreprise", blank=True, null=True)
    certifications = models.TextField(verbose_name="Certifications de l'entreprise", blank=True, null=True, help_text="Liste des certifications obtenues par l'entreprise")
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        nom = self.entreprise.nom if self.entreprise else (self.nom_entreprise or "—")
        return f"{self.manifestation.titre} — {nom}"

    class Meta:
        verbose_name = 'Candidature à une manifestation'
        verbose_name_plural = 'Candidatures aux manifestations'
        ordering = ['manifestation', '-date_candidature']


class CandidatureEtapeHistorique(models.Model):
    """Historique complet des passages par étape (traçabilité)."""
    candidature = models.ForeignKey(
        CandidatureManifestation,
        on_delete=models.CASCADE,
        related_name='historique_etapes',
        verbose_name="Candidature"
    )
    etape = models.ForeignKey(
        EtapeManifestation,
        on_delete=models.CASCADE,
        related_name='historique_candidatures',
        verbose_name="Étape"
    )
    date_entree = models.DateTimeField(verbose_name="Date d'entrée à l'étape", auto_now_add=True)
    date_sortie = models.DateTimeField(verbose_name="Date de sortie de l'étape", null=True, blank=True)

    class Meta:
        verbose_name = 'Historique étape candidature'
        verbose_name_plural = 'Historiques étapes candidatures'
        ordering = ['candidature', 'date_entree']

    def __str__(self):
        return f"{self.candidature} — {self.etape} ({self.date_entree})"


class CandidatureDecision(models.Model):
    """
    Décision admin (ACCEPTER / REFUSER) : traçabilité decision_admin, date_transition, admin_responsable.
    """
    candidature = models.ForeignKey(
        CandidatureManifestation,
        on_delete=models.CASCADE,
        related_name='decisions',
        verbose_name="Candidature"
    )
    decision_admin = models.CharField(
        max_length=10,
        choices=DECISION_ADMIN_CANDIDATURE,
        verbose_name="Décision admin"
    )
    etape = models.ForeignKey(
        EtapeManifestation,
        on_delete=models.CASCADE,
        related_name='decisions_candidatures',
        verbose_name="Étape au moment de la décision"
    )
    date_transition = models.DateTimeField(verbose_name="Date de transition", auto_now_add=True)
    admin_responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='decisions_candidature',
        verbose_name="Admin responsable"
    )

    class Meta:
        verbose_name = 'Décision candidature'
        verbose_name_plural = 'Décisions candidatures'
        ordering = ['-date_transition']

    def __str__(self):
        return f"{self.candidature} — {self.get_decision_admin_display()} ({self.date_transition})"


class CategorieStatistique(models.Model):
    """Catégorie pour regrouper les statistiques (ex: Exportations, Certifications)."""
    nom = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    slug = models.SlugField(max_length=120, null=True, blank=True)
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom) + "-" + str(shortuuid.uuid().lower()[:3])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Catégorie de statistique'
        verbose_name_plural = 'Catégories de statistiques'
        ordering = ['ordre', 'nom']


class Statistique(models.Model):
    """Statistique par année et optionnellement par mois."""
    MOIS_CHOICES = [
        (1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'), (5, 'Mai'), (6, 'Juin'),
        (7, 'Juillet'), (8, 'Août'), (9, 'Septembre'), (10, 'Octobre'), (11, 'Novembre'), (12, 'Décembre'),
    ]
    annee = models.PositiveIntegerField(verbose_name="Année")
    mois = models.PositiveSmallIntegerField(
        choices=MOIS_CHOICES,
        null=True,
        blank=True,
        verbose_name="Mois (vide = statistique annuelle)"
    )
    categorie = models.ForeignKey(
        CategorieStatistique,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='statistiques',
        verbose_name="Catégorie"
    )
    titre = models.CharField(max_length=200, verbose_name="Titre / Libellé")
    valeur = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name="Valeur",
        help_text="Valeur numérique de la statistique"
    )
    unite = models.CharField(max_length=50, blank=True, null=True, verbose_name="Unité (ex: tonnes, GNF, %)")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        mois_str = f" / {self.mois:02d}" if self.mois else ""
        return f"{self.titre} — {self.annee}{mois_str} : {self.valeur}"

    class Meta:
        verbose_name = 'Statistique'
        verbose_name_plural = 'Statistiques'
        ordering = ['-annee', 'mois', 'ordre', 'titre']


class Actualite(models.Model):
    grand_titre = models.CharField(max_length=150)
    slug = models.SlugField(max_length=191, null=True, blank=True)
    date_actualite = models.DateField(null=True, blank=True)
    category = models.ForeignKey(CategorieActuality, on_delete=models.CASCADE, verbose_name="Catégorie de l'actualité")
    image_banner = models.ImageField(upload_to="ImageBanner")
    image_carre = models.ImageField(upload_to="ImageBanner")
    detail = RichTextField() 
    featured = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True ,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True ,null=True, blank=True)

    def __str__(self):
        return self.grand_titre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.grand_titre) + "-" + str(shortuuid.uuid().lower()[:2])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Actualité'
        verbose_name_plural = 'Actualités'
       


class ImageActualite(models.Model):
    images = models.ImageField(upload_to="actualites-images", default="actualite.jpg")
    actualite = models.ForeignKey(Actualite, on_delete=models.SET_NULL, null=True, related_name="a_images")
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé

    def __str__(self):
        return f"Image pour l'actualité {self.actualite.grand_titre}"
    
    
    class Meta:
        verbose_name_plural = "Images d'atualité"

    

class Foires(models.Model):
    titre = models.CharField(max_length=191)
    slug = models.SlugField(max_length=191, null=True, blank=True)
    description = RichTextField(null=True, blank=True)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    pays = models.CharField(max_length=191)
    lieu = models.CharField(max_length=191)
    type = models.CharField(max_length=20,choices=TYPE_FOIRE)
    realisation = models.CharField(max_length=191, choices=REALISATION, default="en_cours")
    montant_des_ventes = models.CharField(max_length=200, blank=True, null=True)
    nbre_entreprise = models.IntegerField(null=True, blank=True)
    nbre_produit_vendu = models.IntegerField(null=True, blank=True)
    nbre_personne = models.IntegerField(null=True, blank=True)
    superficie = models.IntegerField(null=True, blank=True)
    nbre_femme = models.IntegerField(null=True, blank=True)
    nbre_homme = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.titre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre) + "-" + str(shortuuid.uuid().lower()[:2])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Foire'
        verbose_name_plural = 'Foires'


    

class ImageFoire(models.Model):
    images = models.ImageField(upload_to="foire-images", default="foire.jpg")
    foire = models.ForeignKey(Foires, on_delete=models.CASCADE, related_name='image_foire')
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True ,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True ,null=True, blank=True)

    class Meta:
        verbose_name = "Image de la foire"

    def __str__(self):
        return f"Image pour la foire {self.foire.titre}"
    
class ImageActivities(models.Model):
    images = models.ImageField(upload_to="activities-images", default="activity.jpg")
    activity = models.ForeignKey(ActivityFoire, on_delete=models.CASCADE, related_name='image_activities', verbose_name="Activités")
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True ,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True ,null=True, blank=True)

    def __str__(self):
        return f"Image pour l'activité {self.activity.title}"
    
    class Meta:
        verbose_name = "Images d'activité"
    
class ImageSlide(models.Model):
    images = models.ImageField(upload_to="slide-images", default="slide.jpg")
    slide = models.ForeignKey(Slide, on_delete=models.CASCADE, related_name='image_slide')
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True ,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True ,null=True, blank=True)

    def __str__(self):
        return f"Image pour le slide {self.slide.title}"
    
    class Meta:
        verbose_name = "Images de slide"
    

class Presentation(models.Model):
    content = RichTextField()
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    featured = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.content[:50]  # Affiche les 50 premiers caractères du
    
    class Meta:
            verbose_name = 'Presentation'
            verbose_name_plural = 'Presentations'
    


class Service(models.Model):
    title = models.CharField(max_length=191)
    slug = models.SlugField(max_length=191, null=True, blank=True)
    image = models.FileField(upload_to="serviceImage", blank=True, null=True, validators=[validate_image_extension])
    axe1 = models.CharField(max_length=100, blank=True, null=True)
    axe2 = models.CharField(max_length=100, blank=True, null=True)
    axe3 = models.CharField(max_length=100, blank=True, null=True)
    axe4 = models.CharField(max_length=100, blank=True, null=True)
    axe5 = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    featured = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) + "-" + str(shortuuid.uuid().lower()[:2])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'



class DonneeStrategique(models.Model):
    titre = models.CharField(max_length=150)
    slug = models.SlugField(max_length=191, null=True, blank=True)
    detail = RichTextField()
    image = models.ImageField(upload_to="Image_Donnee")

    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    featured = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.titre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre) + "-" + str(shortuuid.uuid().lower()[:2])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Données Stratégique'
        verbose_name_plural = 'Données stratégiques'


class EspaceMedia(models.Model):
    titre = models.CharField(max_length=150)
    slug = models.SlugField(max_length=191, null=True, blank=True)
    image = models.ImageField(upload_to="Image_Donnee")

    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    featured = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.titre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre) + "-" + str(shortuuid.uuid().lower()[:2])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Espace Média'
        verbose_name_plural = 'Espace Médias'


    
class ImageMedia(models.Model):
    images = models.ImageField(upload_to="media-image", default="media.jpg")
    espace_media = models.ForeignKey(EspaceMedia, on_delete=models.CASCADE, related_name='image_media')
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Image pour {self.espace_media.titre}"
    

    class Meta:
        verbose_name = "Images de media"
    
class FAQ(models.Model):
    question = models.CharField(max_length=150)
    response = RichTextField()
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    featured = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.question
    
class CertificationTechnique(models.Model):
    titre = models.CharField(max_length=150)
    description = RichTextField(blank=True, null=True)
    prix = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.titre
    

    class Meta:
        verbose_name = "Certificat Technique"

class CertificationConventionnel(models.Model):
    titre = models.CharField(max_length=150)
    description = RichTextField(blank=True, null=True)
    prix = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.titre
    

    class Meta:
        verbose_name = "Certificat Conventionnel"

class ProcedureProduct(models.Model):
    product = models.ForeignKey(Produit, on_delete=models.CASCADE)
    voie_exportation = models.CharField(max_length=200, choices=VOIE_EXPOITATION, blank=True, null=True)
    formalisation = RichTextField()
    dde = RichTextField()
    certificat_technique = models.ManyToManyField(CertificationTechnique, blank=True, related_name="procedures")
    certificat_conventionnel = models.ForeignKey(CertificationConventionnel, on_delete=models.CASCADE)
    autorisation = RichTextField()
    redevance = RichTextField()
    formalite_douane = RichTextField()
    nb = RichTextField()
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.product.title
    

    class Meta:
        verbose_name = "Procédure d'exportation"

class ProcedureGlobale(models.Model):
    titre = models.CharField(max_length=150)
    description = RichTextField()
    status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
    is_deleted = models.BooleanField(default=False, verbose_name="Est supprimé")  # Marquer comme supprimé
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        verbose_name = "Procédure Global"



# class Statistique(models.Model):
#     title = models.CharField(max_length=191)
#     number = models.IntegerField()
#     status = models.CharField(max_length=10, choices=STATUS, default='brouillon')
#     created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
#     updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

#     def __str__(self):
#         return self.title

#     class Meta:
#         verbose_name = 'Statistique'
#         verbose_name_plural = 'Statistiques'









class Visiteur(models.Model):
    """Modèle pour stocker les informations des visiteurs qui accèdent aux entreprises"""
    nom_complet = models.CharField(max_length=200, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Adresse e-mail")
    pays = models.CharField(max_length=100, verbose_name="Pays")
    ville_residence = models.CharField(max_length=100, verbose_name="Ville de résidence")
    telephone = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    date_visite = models.DateTimeField(auto_now_add=True, verbose_name="Date de visite")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="Adresse IP")
    
    class Meta:
        verbose_name = 'Visiteur'
        verbose_name_plural = 'Visiteurs'
        ordering = ['-date_visite']
    
    def __str__(self):
        return f"{self.nom_complet} - {self.email}"


class Newsletter(models.Model):
    """Modèle pour gérer les abonnés à la newsletter"""
    email = models.EmailField(unique=True, verbose_name="Adresse e-mail")
    nom = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nom (optionnel)")
    prenom = models.CharField(max_length=100, blank=True, null=True, verbose_name="Prénom (optionnel)")
    pays = models.CharField(max_length=100, blank=True, null=True, verbose_name="Pays (optionnel)")
    ville = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ville (optionnel)")
    secteur_activite = models.CharField(max_length=200, blank=True, null=True, verbose_name="Secteur d'activité (optionnel)")
    est_actif = models.BooleanField(default=True, verbose_name="Abonnement actif")
    date_inscription = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    date_desinscription = models.DateTimeField(blank=True, null=True, verbose_name="Date de désinscription")
    ip_inscription = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP d'inscription")
    source_inscription = models.CharField(max_length=100, default='site_web', verbose_name="Source d'inscription")
    
    class Meta:
        verbose_name = 'Abonné Newsletter'
        verbose_name_plural = 'Abonnés Newsletter'
        ordering = ['-date_inscription']
    
    def __str__(self):
        return f"{self.email} - {self.date_inscription.strftime('%d/%m/%Y')}"
    
    def desabonner(self):
        """Méthode pour désabonner un utilisateur"""
        from django.utils import timezone
        self.est_actif = False
        self.date_desinscription = timezone.now()
        self.save()


class NewsletterTemplate(models.Model):
    """Modèle pour les templates de newsletter"""
    titre = models.CharField(max_length=200, verbose_name="Titre du template")
    sujet = models.CharField(max_length=200, verbose_name="Sujet de l'email")
    contenu_html = RichTextField(verbose_name="Contenu HTML")
    contenu_texte = models.TextField(verbose_name="Contenu texte brut")
    est_actif = models.BooleanField(default=True, verbose_name="Template actif")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = 'Template Newsletter'
        verbose_name_plural = 'Templates Newsletter'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.titre} - {self.date_creation.strftime('%d/%m/%Y')}"


class NewsletterEnvoi(models.Model):
    """Modèle pour tracer les envois de newsletter"""
    template = models.ForeignKey(NewsletterTemplate, on_delete=models.CASCADE, verbose_name="Template utilisé")
    sujet = models.CharField(max_length=200, verbose_name="Sujet envoyé")
    nombre_destinataires = models.IntegerField(verbose_name="Nombre de destinataires")
    nombre_envoyes = models.IntegerField(default=0, verbose_name="Nombre d'emails envoyés")
    nombre_erreurs = models.IntegerField(default=0, verbose_name="Nombre d'erreurs")
    date_envoi = models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")
    statut = models.CharField(max_length=20, choices=[
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('erreur', 'Erreur')
    ], default='en_cours', verbose_name="Statut de l'envoi")
    details_erreur = models.TextField(blank=True, null=True, verbose_name="Détails des erreurs")
    
    class Meta:
        verbose_name = 'Envoi Newsletter'
        verbose_name_plural = 'Envois Newsletter'
        ordering = ['-date_envoi']
    
    def __str__(self):
        return f"{self.template.titre} - {self.date_envoi.strftime('%d/%m/%Y %H:%M')}"


# ========== CHATBOT AGUIPEX ==========
# Sessions et messages pour traçabilité et historique.
# ExtractedKeyword alimente le Word Cloud (accessible depuis la navbar, pas dans le chat).


class ChatSession(models.Model):
    """Session de conversation avec le chatbot (anonyme ou identifiée)."""
    session_id = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Session chatbot'
        verbose_name_plural = 'Sessions chatbot'
        ordering = ['-updated_at']

    def __str__(self):
        return self.session_id[:16] + '...'


class ChatMessage(models.Model):
    """Un message (utilisateur ou bot) dans une session."""
    ROLE_USER = 'user'
    ROLE_BOT = 'bot'
    ROLE_CHOICES = [(ROLE_USER, 'Utilisateur'), (ROLE_BOT, 'Bot')]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    # Compréhension affichée côté UI ("Voici ce que j'ai compris...")
    understood_as = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Message chatbot'
        verbose_name_plural = 'Messages chatbot'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class ExtractedKeyword(models.Model):
    """Mots-clés extraits des questions (alimente le Word Cloud)."""
    word = models.CharField(max_length=100, db_index=True)
    weight = models.PositiveIntegerField(default=1)  # Fréquence / importance
    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name='keywords', null=True, blank=True
    )
    message = models.ForeignKey(
        ChatMessage, on_delete=models.CASCADE, related_name='keywords', null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mot-clé extrait (Word Cloud)'
        verbose_name_plural = 'Mots-clés extraits (Word Cloud)'
        ordering = ['-weight', '-created_at']

    def __str__(self):
        return f"{self.word} ({self.weight})"






