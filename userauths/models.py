from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from shortuuid.django_fields import ShortUUIDField
import shortuuid

OCCUPATION = (
    ("dg", "Directeur Général"),
    ("dga", "Directrice Générale Adjointe"),
    ("chef_departement", "Chef de département"),
    ("chef_cellule", "Chef de cellule"),
    ("charge_etude", "Charger d'étude"),
    ("communication", "Communication"),
    ("logistique", "Logistique"),
    ("comptabilite", "Comptabilité"),
    ("rh", "RH"),
    ("secretaire", "Secrétaire"),
    ("agoa", "Agoa"),
    ("conseiller", "Conseiller"),
    ("saf", "SAF"),
    ("visiteur", "Visiteur"),
    ("visil", "Visil"),
    ("autre", "Autre"),

)

GRADE = (
    ("chef_cellule", "Chef Cellule"),
    ("chef_service", "Chef Service"),
    ("autre", "Autre"),
)

ROLE = (
    ("marketing", "Marketing"),
    ("certification", "Certification"),
    ("communication", "Communication"),
    ("statistique", "Statistique"),
    ("logistique", "Logistique"),
    ("rh", "RH"),
    ("autre", "Autre"),
)

DEPARTEMENT = (
    ("certification_reglementation", "Certification et Reglementation"),
    ("marketing", "Marketing"),
    ("statistique_documentation", "Statistique et Documentation"),
    ("autre", "Autre"),
)

CELLULE = (
    ("cellule_partenariat", "Cellule Partenariat"),
    ("cellule_etude_marche", "Cellule Etude et Marché"),
    ("cellule_evenementiel", "Cellule Evenementiel"),
    ("cellule_etude_analyse_donnee", "Cellule Etudes et Analyses des Données"),
    ("cellule_documentation_archive", "Cellule Documentation et Archives"),
    ("cellule_certification", "Cellule Certification"),
    ("cellule_reglementation", "Cellule Reglementation"),
    ("agent_comptable", "Agent Comptable"),
    ("service_rh", "Service des ressources humaines"),
    ("service_logistique", "Service Logistique"),
    ("service_com_rp", "Service Communication et Relations Publiques"),
    ("secretariat_central", "Secrétariat Central"),
    ("controlleur_financier", "Contrôleur Financier"),
    ("autre", "Autre"),
)

GENRE = (
    ("masculin", "Masculin"),
    ("feminin", "Feminin"),
    ("other", "Autre"),
)

class User(AbstractUser):
    username = models.CharField(max_length=100, verbose_name="Nom d'utilisateur")
    email = models.EmailField(unique=True, verbose_name="Adresse E-mail", blank=True, null=True)
    full_name = models.CharField(max_length=100, verbose_name="Prénom et Nom")  # Suppression de l'unicité
    otp = models.CharField(max_length=100, null=True, blank=True)
    refresh_token = models.CharField(max_length=1000, null=True, blank=True)
    est_employer = models.BooleanField(default=False)
    entreprise = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(verbose_name="Téléphone", max_length=200, blank=True, null=True)
    occupation = models.CharField(max_length=150, choices=OCCUPATION, default="other", verbose_name="Occupation")  # Ajout du champ occupation
    grade = models.CharField(max_length=150, choices=GRADE, default="autre", verbose_name="Grade")  # Ajout du champ occupation
    role = models.CharField(max_length=150, choices=ROLE, default="autre", verbose_name="Rôle")
    cellule = models.CharField(max_length=150, choices=CELLULE, default="autre", verbose_name="Cellule")
    departement = models.CharField(max_length=150, choices=DEPARTEMENT, default="autre")
    profile_picture = models.ImageField(upload_to="profile_img", blank=True, null=True)
    profile_picture_url = models.URLField(blank=True, null=True)    
    status = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.full_name if self.full_name else self.email
    
    def save(self, *args, **kwargs):
        # Vérification et nettoyage de l'email
        if isinstance(self.email, tuple):  # Si l'email est un tuple, prendre le premier élément
            self.email = self.email[0] if self.email else None
        
        if self.email and isinstance(self.email, str):  # Nettoyer seulement si c'est une chaîne
            self.email = self.email.strip("(),''")
        
        if not self.email or self.email in ["", "()"]:
            self.email = None

        # Gestion du username
        if not self.username:
            if self.full_name:
                base_username = self.full_name.split(" ")[0].lower()
            elif self.email:
                base_username = self.email.split("@")[0].lower()
            else:
                base_username = f"user_{self.pk or 'temp'}"
            
            # Vérifier l'unicité du username
            unique_username = base_username
            counter = 1
            while User.objects.filter(username=unique_username).exists():
                unique_username = f"{base_username}{counter}"
                counter += 1
            
            self.username = unique_username

        # Gestion du full_name
        if not self.full_name and self.email:
            self.full_name = self.email.split("@")[0]

        if not self.full_name:
            self.full_name = self.username

        # Appeler la méthode save parent
        super().save(*args, **kwargs)






class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    full_name = models.CharField(max_length=150, verbose_name="Prénom et Nom")
    phone = models.CharField(verbose_name="Téléphone", max_length=200, default="Conakry")
    country = models.CharField(max_length=150, default="Guinée", verbose_name="Pays")
    city_of_origin = models.CharField(verbose_name="Ville", max_length=200, default="Conakry")
    genre = models.CharField(max_length=150, choices=GENRE, default="other")
    about = models.TextField(null=True, blank=True, verbose_name="Biographie")
    date = models.DateTimeField(auto_now_add=True)

    facebook = models.URLField(max_length=255, blank=True, null=True)
    youtube = models.URLField(max_length=255, blank=True, null=True)
    instagram = models.URLField(max_length=255, blank=True, null=True)
    twitter = models.URLField(max_length=255, blank=True, null=True)
    linkedin = models.URLField(max_length=255, blank=True, null=True)


    class Meta:
        verbose_name_plural = "Employés"

    def __str__(self) -> str:
        return str(self.full_name) if self.full_name else str(self.user.full_name)
    
    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.user.full_name
        super(Profile, self).save(*args, **kwargs)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
