from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.db.models import Count, Q, F
from django.utils.safestring import mark_safe
from django.urls import path
from django.template.response import TemplateResponse
from core import models as aguipex_models
from .models import (Slide, QuiSommeNous, Produit, Programme, Evenement, CertificationTechnique, CertificationConventionnel, ProcedureProduct, ProcedureGlobale, Partenaire, Equipe, Service, Foires,
                     Temoignage, MotDirecteur, VisionMission, Valeur, Gouvernance, ActivityFoire, EspaceMedia, Actualite, Contact, CategorieActuality, FAQ, DonneeStrategique,
                     Interprofession, PersonnelInterprofession, Projet, EtapeProjet, CategorieStatistique, Statistique,
                     ManifestationCommerciale, EtapeManifestation, CandidatureManifestation, CandidatureEtapeHistorique, CandidatureDecision,
                     ChatSession, ChatMessage, ExtractedKeyword, TypeProduit, ProduitEntreprise)
from .manifestation_services import transition_candidature, TransitionCandidatureError
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from datetime import datetime, timedelta
import csv
import openpyxl
import re
import html
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

def _strip_html(html_content: str) -> str:
    """Retire les balises HTML et décode les entités HTML."""
    if not html_content:
        return ""
    text = str(html_content)
    text = re.sub(r'<[^>]+>', ' ', text)
    try:
        text = html.unescape(text)
    except Exception:
        pass
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Formulaires personnalisés avec CKEditor
class ActualiteAdminForm(forms.ModelForm):
    detail = forms.CharField(widget=CKEditorWidget(config_name='default'))
    
    class Meta:
        model = Actualite
        fields = '__all__'

class ProgrammeAdminForm(forms.ModelForm):
    description1 = forms.CharField(widget=CKEditorWidget(config_name='default'), required=False)
    description2 = forms.CharField(widget=CKEditorWidget(config_name='default'), required=False)
    
    class Meta:
        model = Programme
        fields = '__all__'

class MotDirecteurAdminForm(forms.ModelForm):
    contenu = forms.CharField(widget=CKEditorWidget(config_name='default'))
    
    class Meta:
        model = MotDirecteur
        fields = '__all__'

class TemoignageAdminForm(forms.ModelForm):
    contenu = forms.CharField(widget=CKEditorWidget(config_name='default'))
    
    class Meta:
        model = Temoignage
        fields = '__all__'

class ValeurAdminForm(forms.ModelForm):
    contenu = forms.CharField(widget=CKEditorWidget(config_name='default'))
    
    class Meta:
        model = Valeur
        fields = '__all__'

class GouvernanceAdminForm(forms.ModelForm):
    contenu = forms.CharField(widget=CKEditorWidget(config_name='default'))
    
    class Meta:
        model = Gouvernance
        fields = '__all__'

class FAQAdminForm(forms.ModelForm):
    response = forms.CharField(widget=CKEditorWidget(config_name='default'))
    
    class Meta:
        model = FAQ
        fields = '__all__'

class ContactAdminForm(forms.ModelForm):
    message = forms.CharField(widget=CKEditorWidget(config_name='simple'))
    
    class Meta:
        model = Contact
        fields = '__all__'


def image_preview(obj):
    if obj.image:
        return format_html('<img src="{}" width="50" height="50" style="border-radius:5px;"/>'.format(obj.image.url))
    return "(Aucune image)"

class ImageActivitiesInline(admin.TabularInline):
    model = aguipex_models.ImageActivities

class ImageSlideInline(admin.TabularInline):
    model = aguipex_models.ImageSlide

class ImageMediaInline(admin.TabularInline):
    model = aguipex_models.ImageMedia

class ImageActualiteInline(admin.TabularInline):
    model = aguipex_models.ImageActualite

class ImageFoireInline(admin.TabularInline):
    model = aguipex_models.ImageFoire



class CustomAdmin(admin.ModelAdmin):
    actions = ["soft_delete_selected"]

    def delete_model(self, request, obj):
        obj.is_deleted = True
        obj.save()
        messages.success(request, f"L'élément {obj} a été marqué comme supprimé.")

    def delete_queryset(self, request, queryset):
        count = queryset.update(is_deleted=True)
        messages.success(request, f"{count} élément(s) ont été marqués comme supprimés.")

    @admin.action(description="Marquer comme supprimé")
    def soft_delete_selected(self, request, queryset):
        count = queryset.update(is_deleted=True)
        messages.success(request, f"{count} élément(s) ont été marqués comme supprimés.")


    def get_queryset(self, request):
        """ Filtre les objets supprimés pour tous sauf le superadmin """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_deleted=False)
    
    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     return queryset.filter(is_deleted=False)


    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if request.user.is_superuser or getattr(request.user, "role", None) == "communication":
            return list_display
        return tuple(field for field in list_display if field != "status")
    
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser or getattr(request.user, "role", None) == "communication":
            return fields
        return tuple(field for field in fields if field != "status")

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if request.user.is_superuser or getattr(request.user, "role", None) == "communication":
            return readonly_fields
        return readonly_fields + ("status",)  # Rendre le champ status en lecture seule pour les autres
    
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        return tuple(field for field in fields if field != "is_deleted")
    
    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if request.user.is_superuser:
            return list_display
        return tuple(field for field in list_display if field != "is_deleted")

    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated

    def has_change_permission(self, request, obj=None):
        return request.user.is_authenticated

    def has_add_permission(self, request):
        return request.user.is_authenticated

    def has_delete_permission(self, request, obj=None):
        return request.user.is_authenticated


@admin.register(Slide)
class SlideAdmin(CustomAdmin):
    list_display = ('title', 'subtitle', 'status', 'is_deleted', 'created_at', 'updated_at', 'image_preview')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'subtitle', 'description')
    readonly_fields = ('image_preview',)
    exclude = ('slug',)
    inlines = [ImageSlideInline]
    def image_preview(self, obj):
        return image_preview(obj)
    
    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication"]:
            return True
        return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)
    
# Qui somme nous
@admin.register(QuiSommeNous)
class QuiSommeNousAdmin(CustomAdmin):
    list_display = ('titre', 'nombreAnnee', 'texteAnne', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('titre', 'detail')

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication"]:
            return True
        return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)

# Produit
@admin.register(Produit)
class ProduitAdmin(CustomAdmin):
    list_display = ('title', 'status', 'featured','pour_site', 'is_deleted', 'created_at', 'updated_at', 'image_preview')
    list_filter = ('status', 'featured', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('image_preview',)
    def image_preview(self, obj):
        return image_preview(obj)
    
    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication", "marketing"]:
            return True
        return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)

# Programme
@admin.register(Programme)
class ProgrammeAdmin(CustomAdmin):
    form = ProgrammeAdminForm
    list_display = ('nom', 'accronyme', 'status', 'is_deleted', 'created_at', 'updated_at', 'image_preview', 'logo_preview')
    list_filter = ('status', 'created_at')
    search_fields = ('nom', 'accronyme')
    readonly_fields = ('image_preview', 'logo_preview')
    exclude = ('slug',)
    
    def image_preview(self, obj):
        return image_preview(obj)
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="80"/>'.format(obj.logo.url))
        return "(Aucun logo)"
    
    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication"]:
            return True
        return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)

# Événement
@admin.register(Evenement)
class EvenementAdmin(CustomAdmin):
    list_display = ('title', 'date_evenement', 'date_fin', 'status', 'featured', 'is_deleted', 'created_at', 'updated_at', 'image_preview')
    list_filter = ('status', 'featured', 'date_evenement')
    search_fields = ('title',)
    readonly_fields = ('image_preview',)
    exclude = ('slug',)
    def image_preview(self, obj):
        return image_preview(obj)
    

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication"]:
            return True
        return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)
    

# Partenaire
@admin.register(Partenaire)
class PartenaireAdmin(CustomAdmin):
    list_display = ('status', 'is_deleted', 'created_at', 'updated_at', 'logo_preview')
    list_filter = ('status',)
    readonly_fields = ('logo_preview',)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="100"/>'.format(obj.logo.url))
        return "(Aucun logo)"
    
    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication"]:
            return True
        return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)

# Témoignage
@admin.register(Temoignage)
class TemoignageAdmin(CustomAdmin):
    form = TemoignageAdminForm
    list_display = ('name', 'fonction', 'notation', 'status', 'is_deleted', 'created_at', 'updated_at', 'image_preview')
    list_filter = ('status', 'notation')
    search_fields = ('name', 'fonction', 'contenu')
    readonly_fields = ('image_preview',)
    def image_preview(self, obj):
        return image_preview(obj)
    

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication"]:
            return True
        return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)


# Equipe
@admin.register(Equipe)
class EquipeAdmin(CustomAdmin):
    list_display = ('name', 'fonction', 'email', 'contact', 'is_deleted', 'created_at', 'updated_at', 'image_preview')
    list_filter = ('status', 'contact')
    search_fields = ('name', 'fonction', 'email')
    readonly_fields = ('image_preview',)
    exclude = ('slug',)
    def image_preview(self, obj):
        return image_preview(obj)
    
    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication"]:
            return True
        return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)


# Interprofessions
class InterprofessionAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(config_name='default'), required=False)
    
    class Meta:
        model = Interprofession
        fields = '__all__'


class PersonnelInterprofessionInline(admin.TabularInline):
    model = PersonnelInterprofession
    extra = 0
    fields = ('nom', 'prenom', 'localisation', 'email', 'poste', 'profession', 'status')
    show_change_link = True


@admin.register(Interprofession)
class InterprofessionAdmin(CustomAdmin):
    form = InterprofessionAdminForm
    list_display = ('nom', 'code', 'status', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('nom', 'code', 'description')
    inlines = [PersonnelInterprofessionInline]
    ordering = ('nom',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'code', 'description')
        }),
        ('Statut', {
            'fields': ('status', 'is_deleted')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PersonnelInterprofession)
class PersonnelInterprofessionAdmin(CustomAdmin):
    list_display = ('nom', 'prenom', 'interprofession', 'poste', 'profession', 'localisation', 'email', 'status', 'is_deleted', 'created_at')
    list_filter = ('status', 'interprofession')
    search_fields = ('nom', 'prenom', 'email', 'poste', 'profession')
    list_select_related = ('interprofession',)
    autocomplete_fields = ('interprofession',)
    ordering = ('interprofession__nom', 'nom', 'prenom')


# Gestion des projets
class ProjetAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(config_name='default'), required=False)

    class Meta:
        model = Projet
        fields = '__all__'


class EtapeProjetInline(admin.TabularInline):
    model = EtapeProjet
    extra = 0
    fields = ('titre', 'description', 'ordre', 'date_etape', 'pourcentage')
    ordering = ('ordre',)


@admin.register(Projet)
class ProjetAdmin(CustomAdmin):
    form = ProjetAdminForm
    list_display = ('title', 'status', 'responsable_nom', 'responsable_poste', 'start_date', 'end_date', 'is_deleted', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'description', 'responsable_nom')
    inlines = [EtapeProjetInline]
    date_hierarchy = 'start_date'
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'status')
        }),
        ('Période', {
            'fields': ('start_date', 'end_date')
        }),
        ('Responsable du projet', {
            'fields': ('responsable_nom', 'responsable_poste'),
            'description': 'Saisir le nom et le poste du responsable (affichés sur le site).'
        }),
    )


class EtapeProjetAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(config_name='simple'), required=False)

    class Meta:
        model = EtapeProjet
        fields = '__all__'


@admin.register(EtapeProjet)
class EtapeProjetAdmin(CustomAdmin):
    form = EtapeProjetAdminForm
    list_display = ('titre', 'projet', 'ordre', 'date_etape', 'pourcentage', 'is_deleted', 'created_at')
    list_filter = ('projet',)
    search_fields = ('titre', 'projet__title')
    list_select_related = ('projet',)
    autocomplete_fields = ('projet',)
    ordering = ('projet', 'ordre')


# --- Manifestations commerciales (Back Office) ---
# Les 4 étapes sont créées automatiquement à la création de la manifestation.
# L'admin ne peut ni les créer, ni les supprimer, ni modifier leur ordre ; seul le contenu est éditable.
class EtapeManifestationInlineForm(forms.ModelForm):
    """Ordre et titre en lecture seule ; description et dates éditables."""
    ordre = forms.IntegerField(disabled=True, required=False)
    titre = forms.CharField(disabled=True, required=False)

    class Meta:
        model = EtapeManifestation
        fields = ('ordre', 'titre', 'date_debut', 'date_fin', 'description')


class EtapeManifestationInline(admin.TabularInline):
    model = EtapeManifestation
    form = EtapeManifestationInlineForm
    extra = 0
    max_num = 4
    can_delete = False
    ordering = ('ordre',)
    verbose_name = 'Étape (contenu)'
    verbose_name_plural = 'Étapes (ordre et titre fixes ; seule la description est modifiable)'


class ManifestationCommercialeAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(config_name='default'), required=False)
    conditions_de_participation = forms.CharField(widget=CKEditorWidget(config_name='default'), required=False)

    class Meta:
        model = ManifestationCommerciale
        fields = '__all__'


@admin.register(EtapeManifestation)
class EtapeManifestationAdmin(CustomAdmin):
    """Consultation uniquement. Les étapes sont créées automatiquement avec la manifestation ; pas d'ajout/suppression."""
    list_display = ('titre', 'manifestation', 'ordre', 'is_deleted', 'created_at')
    list_filter = ('manifestation',)
    search_fields = ('titre', 'manifestation__titre')
    list_select_related = ('manifestation',)
    autocomplete_fields = ('manifestation',)
    ordering = ('manifestation', 'ordre')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ManifestationCommerciale)
class ManifestationCommercialeAdmin(CustomAdmin):
    form = ManifestationCommercialeAdminForm
    list_display = ('titre', 'statut_global', 'statut_publication', 'date_debut', 'date_fin', 'lieu', 'is_deleted', 'created_at')
    list_filter = ('statut_global', 'statut_publication')
    search_fields = ('titre', 'lieu', 'pays')
    prepopulated_fields = {'slug': ('titre',)}
    inlines = [EtapeManifestationInline]
    date_hierarchy = 'date_debut'
    ordering = ('-date_debut', '-created_at')
    fieldsets = (
        (None, {
            'fields': ('titre', 'slug', 'description')
        }),
        ('Conditions de participation', {
            'fields': ('conditions_de_participation',),
            'description': 'Conditions et critères requis pour participer à cette manifestation. Sera affiché sur la page de détail et dans le formulaire de postulation.'
        }),
        ('Statuts', {
            'fields': ('statut_global', 'statut_publication'),
            'description': 'Statut global = processus. Publication = visible sur le site (Front Office).'
        }),
        ('Dates et lieu', {
            'fields': ('date_debut', 'date_fin', 'lieu', 'pays')
        }),
    )

    def get_inline_instances(self, request, obj=None):
        """Afficher les étapes uniquement en édition : elles sont créées automatiquement au premier enregistrement."""
        inlines = super().get_inline_instances(request, obj)
        if obj is None:
            inlines = [i for i in inlines if not isinstance(i, EtapeManifestationInline)]
        return inlines


class CandidatureManifestationAdminForm(forms.ModelForm):
    class Meta:
        model = CandidatureManifestation
        fields = '__all__'


# Filtres personnalisés pour CandidatureManifestation
class ManifestationFilter(admin.SimpleListFilter):
    title = 'Manifestation'
    parameter_name = 'manifestation_filter'

    def lookups(self, request, model_admin):
        manifestations = aguipex_models.ManifestationCommerciale.objects.values_list('id', 'titre').order_by('titre')
        return [(str(id), titre) for id, titre in manifestations]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(manifestation_id=self.value())
        return queryset

class StatutMetierFilter(admin.SimpleListFilter):
    title = 'Statut métier'
    parameter_name = 'statut_metier_filter'

    def lookups(self, request, model_admin):
        return (
            ('accepte', 'Acceptées'),
            ('refus', 'Refusées'),
            ('en_attente', 'En attente'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'accepte':
            return queryset.filter(statut_metier='accepte')
        elif self.value() == 'refus':
            return queryset.filter(statut_metier='refus')
        elif self.value() == 'en_attente':
            return queryset.filter(statut_metier='en_attente')
        return queryset

class StatutBackOfficeFilter(admin.SimpleListFilter):
    title = 'Statut back office'
    parameter_name = 'statut_back_office_filter'

    def lookups(self, request, model_admin):
        return (
            ('publie', 'Publiées'),
            ('brouillon', 'Brouillons'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'publie':
            return queryset.filter(statut_back_office='publie')
        elif self.value() == 'brouillon':
            return queryset.filter(statut_back_office='brouillon')
        return queryset

class EtapeFilter(admin.SimpleListFilter):
    title = 'Étape actuelle'
    parameter_name = 'etape_filter'

    def lookups(self, request, model_admin):
        etapes = aguipex_models.EtapeManifestation.objects.select_related('manifestation').values_list('id', 'titre', 'manifestation__titre').order_by('manifestation__titre', 'ordre')
        return [(str(id), f"{manifestation} - {titre}") for id, titre, manifestation in etapes]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(etape_actuelle_id=self.value())
        return queryset

class DateCandidatureFilter(admin.SimpleListFilter):
    title = 'Date de candidature'
    parameter_name = 'date_candidature_filter'

    def lookups(self, request, model_admin):
        return (
            ('today', "Aujourd'hui"),
            ('week', 'Cette semaine'),
            ('month', 'Ce mois'),
            ('year', 'Cette année'),
        )

    def queryset(self, request, queryset):
        today = datetime.now().date()
        if self.value() == 'today':
            return queryset.filter(date_candidature__date=today)
        elif self.value() == 'week':
            week_ago = today - timedelta(days=7)
            return queryset.filter(date_candidature__date__gte=week_ago)
        elif self.value() == 'month':
            month_ago = today - timedelta(days=30)
            return queryset.filter(date_candidature__date__gte=month_ago)
        elif self.value() == 'year':
            year_ago = today - timedelta(days=365)
            return queryset.filter(date_candidature__date__gte=year_ago)
        return queryset

@admin.register(CandidatureManifestation)
class CandidatureManifestationAdmin(CustomAdmin):
    form = CandidatureManifestationAdminForm
    change_form_template = 'admin/core/candidaturemanifestation/change_form.html'
    change_list_template = 'admin/core/candidaturemanifestation/change_list.html'
    list_display = (
        'manifestation', 'get_entreprise_display', 'get_responsable_display', 'statut_metier', 'statut_back_office',
        'etape_actuelle', 'date_candidature', 'is_deleted', 'created_at'
    )
    list_filter = (ManifestationFilter, StatutMetierFilter, StatutBackOfficeFilter, EtapeFilter, DateCandidatureFilter, 'is_deleted', 'created_at')
    search_fields = ('nom_entreprise', 'email_contact', 'telephone_contact', 'responsable_entreprise', 'manifestation__titre', 'entreprise__nom', 'domaine_activite', 'type_entreprise', 'siege_social')
    list_select_related = ('manifestation', 'entreprise', 'etape_actuelle')
    autocomplete_fields = ('manifestation', 'entreprise')
    readonly_fields = ('date_candidature', 'etape_actuelle', 'statut_metier')
    ordering = ('manifestation', '-date_candidature')
    list_per_page = 50
    list_max_show_all = 200
    actions = ['accepter_candidature', 'refuser_candidature', 'publier_selected', 'mettre_en_brouillon_selected']
    fieldsets = (
        (None, {
            'fields': ('manifestation', 'entreprise')
        }),
        ('Contact (si pas d\'entreprise liée)', {
            'fields': ('nom_entreprise', 'email_contact', 'telephone_contact', 'message'),
            'classes': ('collapse',)
        }),
        ('Informations complémentaires', {
            'fields': ('responsable_entreprise', 'nombre_personnes', 'produits_entreprise', 'domaine_activite', 'type_entreprise', 'date_creation_entreprise', 'nombre_manifestations_participees', 'peut_se_financer', 'a_rccm', 'a_code_nif', 'siege_social', 'certifications'),
            'classes': ('collapse',),
            'description': 'Informations supplémentaires sur l\'entreprise et sa candidature.'
        }),
        ('Statuts', {
            'fields': ('statut_metier', 'statut_back_office'),
            'description': "Statut métier : lecture seule (modifié par Accepter / Refuser). Statut back office : vous pouvez passer de Brouillon à Publié pour chaque candidature."
        }),
        ('Avancement', {
            'fields': ('etape_actuelle',),
            'description': "L'étape et le statut ne se modifient pas à la main. Seuls les avancements possibles : Accepter (passage au statut/étape suivant) ou Refuser (reste au même statut/étape). Utilisez les actions en liste."
        }),
        ('Dates', {
            'fields': ('date_candidature',)
        }),
    )

    def get_entreprise_display(self, obj):
        return obj.entreprise.nom if obj.entreprise else (obj.nom_entreprise or "—")
    get_entreprise_display.short_description = 'Entreprise'

    def get_responsable_display(self, obj):
        return obj.responsable_entreprise or "—"
    get_responsable_display.short_description = 'Responsable'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Intercepter les boutons Accepter / Refuser sur la fiche candidature pour appliquer la transition (avancement)."""
        if request.method == 'POST':
            if '_accepter' in request.POST or '_refuser' in request.POST:
                candidature = get_object_or_404(CandidatureManifestation, pk=object_id)
                decision = 'accepter' if '_accepter' in request.POST else 'refuser'
                try:
                    transition_candidature(candidature, decision, user=request.user)
                    msg = "Candidature acceptée : passage à l'étape suivante." if decision == 'accepter' else "Candidature refusée : elle reste à l'étape actuelle."
                    self.message_user(request, msg, messages.SUCCESS)
                except TransitionCandidatureError as e:
                    self.message_user(request, str(e), messages.ERROR)
                return redirect('admin:core_candidaturemanifestation_change', object_id)
        return super().change_view(request, object_id, form_url, extra_context)

    def _appliquer_decision(self, request, queryset, decision):
        nb_ok, nb_err = 0, 0
        for candidature in queryset:
            if not candidature.etape_actuelle:
                self.message_user(request, f"Candidature « {candidature} » sans étape actuelle : ignorée.", messages.WARNING)
                nb_err += 1
                continue
            try:
                transition_candidature(candidature, decision, user=request.user)
                nb_ok += 1
            except TransitionCandidatureError as e:
                self.message_user(request, f"{candidature} : {e}", messages.ERROR)
                nb_err += 1
        if nb_ok:
            self.message_user(request, f"{nb_ok} candidature(s) traitée(s).", messages.SUCCESS)
        if nb_err:
            self.message_user(request, f"{nb_err} erreur(s).", messages.WARNING)

    @admin.action(description="Accepter la candidature (passage à l'étape suivante)")
    def accepter_candidature(self, request, queryset):
        self._appliquer_decision(request, queryset, 'accepter')

    @admin.action(description="Refuser (reste à l'étape actuelle)")
    def refuser_candidature(self, request, queryset):
        self._appliquer_decision(request, queryset, 'refuser')

    @admin.action(description="Publier les candidatures sélectionnées")
    def publier_selected(self, request, queryset):
        count = queryset.update(statut_back_office='publie')
        self.message_user(request, f"{count} candidature(s) ont été publiée(s).", messages.SUCCESS)

    @admin.action(description="Mettre en brouillon les candidatures sélectionnées")
    def mettre_en_brouillon_selected(self, request, queryset):
        count = queryset.update(statut_back_office='brouillon')
        self.message_user(request, f"{count} candidature(s) ont été mise(s) en brouillon.", messages.SUCCESS)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('kpi-stats/', self.admin_site.admin_view(self.kpi_stats_view), name='candidature_kpi_stats'),
            path('export-excel/', self.admin_site.admin_view(self.export_excel), name='candidature_export_excel'),
            path('export-csv/', self.admin_site.admin_view(self.export_csv), name='candidature_export_csv'),
        ]
        return custom_urls + urls
    
    def export_excel(self, request):
        """Export Excel des candidatures"""
        queryset = self.get_queryset(request)
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Candidatures"
        
        headers = [
            'Manifestation', 'Entreprise', 'Responsable', 'Email', 'Téléphone',
            'Statut Métier', 'Statut Back Office', 'Étape Actuelle', 'Date Candidature',
            'Nombre Personnes', 'Produits', 'Domaine Activité', 'Type Entreprise',
            'RCCM', 'NIF', 'Date Création Entreprise', 'Nombre Manifestations',
            'Peut Se Financer', 'Siège Social', 'Certifications'
        ]
        
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        for row_num, obj in enumerate(queryset, 2):
            ws.cell(row=row_num, column=1, value=str(obj.manifestation.titre) if obj.manifestation else '')
            ws.cell(row=row_num, column=2, value=obj.entreprise.nom if obj.entreprise else (obj.nom_entreprise or ''))
            ws.cell(row=row_num, column=3, value=obj.responsable_entreprise or '')
            ws.cell(row=row_num, column=4, value=obj.email_contact or '')
            ws.cell(row=row_num, column=5, value=obj.telephone_contact or '')
            ws.cell(row=row_num, column=6, value=obj.get_statut_metier_display())
            ws.cell(row=row_num, column=7, value=obj.get_statut_back_office_display())
            ws.cell(row=row_num, column=8, value=obj.etape_actuelle.titre if obj.etape_actuelle else '')
            ws.cell(row=row_num, column=9, value=obj.date_candidature.strftime('%d/%m/%Y %H:%M') if obj.date_candidature else '')
            ws.cell(row=row_num, column=10, value=obj.nombre_personnes or '')
            ws.cell(row=row_num, column=11, value=obj.produits_entreprise or '')
            ws.cell(row=row_num, column=12, value=obj.domaine_activite or '')
            ws.cell(row=row_num, column=13, value=obj.type_entreprise or '')
            ws.cell(row=row_num, column=14, value='Oui' if obj.a_rccm else 'Non')
            ws.cell(row=row_num, column=15, value='Oui' if obj.a_code_nif else 'Non')
            ws.cell(row=row_num, column=16, value=obj.date_creation_entreprise.strftime('%d/%m/%Y') if obj.date_creation_entreprise else '')
            ws.cell(row=row_num, column=17, value=obj.nombre_manifestations_participees or '')
            ws.cell(row=row_num, column=18, value='Oui' if obj.peut_se_financer else 'Non')
            ws.cell(row=row_num, column=19, value=obj.siege_social or '')
            ws.cell(row=row_num, column=20, value=obj.certifications or '')
        
        for col_num in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col_num)].width = 20
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="candidatures_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        wb.save(response)
        return response
    
    def export_csv(self, request):
        """Export CSV des candidatures"""
        queryset = self.get_queryset(request)
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="candidatures_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Manifestation', 'Entreprise', 'Responsable', 'Email', 'Téléphone',
            'Statut Métier', 'Statut Back Office', 'Étape Actuelle', 'Date Candidature',
            'Nombre Personnes', 'Produits', 'Domaine Activité', 'Type Entreprise',
            'RCCM', 'NIF', 'Date Création Entreprise', 'Nombre Manifestations',
            'Peut Se Financer', 'Siège Social', 'Certifications'
        ])
        
        for obj in queryset:
            writer.writerow([
                str(obj.manifestation.titre) if obj.manifestation else '',
                obj.entreprise.nom if obj.entreprise else (obj.nom_entreprise or ''),
                obj.responsable_entreprise or '',
                obj.email_contact or '',
                obj.telephone_contact or '',
                obj.get_statut_metier_display(),
                obj.get_statut_back_office_display(),
                obj.etape_actuelle.titre if obj.etape_actuelle else '',
                obj.date_candidature.strftime('%d/%m/%Y %H:%M') if obj.date_candidature else '',
                obj.nombre_personnes or '',
                obj.produits_entreprise or '',
                obj.domaine_activite or '',
                obj.type_entreprise or '',
                'Oui' if obj.a_rccm else 'Non',
                'Oui' if obj.a_code_nif else 'Non',
                obj.date_creation_entreprise.strftime('%d/%m/%Y') if obj.date_creation_entreprise else '',
                obj.nombre_manifestations_participees or '',
                'Oui' if obj.peut_se_financer else 'Non',
                obj.siege_social or '',
                obj.certifications or '',
            ])
        
        return response

    def kpi_stats_view(self, request):
        """Vue pour afficher les KPI des candidatures"""
        queryset = self.get_queryset(request)
        
        # Calcul des KPI
        total = queryset.count()
        acceptees = queryset.filter(statut_metier='accepte', is_deleted=False).count()
        refusees = queryset.filter(statut_metier='refus', is_deleted=False).count()
        en_attente = queryset.filter(statut_metier='en_attente', is_deleted=False).count()
        publiees = queryset.filter(statut_back_office='publie', is_deleted=False).count()
        brouillons = queryset.filter(statut_back_office='brouillon', is_deleted=False).count()
        supprimees = queryset.filter(is_deleted=True).count()
        
        # Par manifestation (top 5)
        top_manifestations = queryset.values('manifestation__titre').annotate(count=Count('id')).order_by('-count')[:5]
        
        # Par étape
        par_etape = queryset.values('etape_actuelle__titre', 'etape_actuelle__manifestation__titre').annotate(count=Count('id')).order_by('-count')[:10]
        
        # Évolution (7 derniers jours)
        evolution = []
        for i in range(6, -1, -1):
            date = datetime.now().date() - timedelta(days=i)
            count = queryset.filter(date_candidature__date=date).count()
            evolution.append({'date': date.strftime('%d/%m'), 'count': count})
        
        # Taux d'acceptation par manifestation
        taux_acceptation = []
        for manif in aguipex_models.ManifestationCommerciale.objects.all()[:5]:
            total_manif = queryset.filter(manifestation=manif, is_deleted=False).count()
            acceptees_manif = queryset.filter(manifestation=manif, statut_metier='accepte', is_deleted=False).count()
            taux = (acceptees_manif / total_manif * 100) if total_manif > 0 else 0
            taux_acceptation.append({
                'manifestation': manif.titre,
                'total': total_manif,
                'acceptees': acceptees_manif,
                'taux': round(taux, 1)
            })
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Statistiques des Candidatures',
            'kpi': {
                'total': total,
                'acceptees': acceptees,
                'refusees': refusees,
                'en_attente': en_attente,
                'publiees': publiees,
                'brouillons': brouillons,
                'supprimees': supprimees,
                'top_manifestations': top_manifestations,
                'par_etape': par_etape,
                'evolution': evolution,
                'taux_acceptation': taux_acceptation,
            }
        }
        return TemplateResponse(request, 'admin/candidature_kpi_stats.html', context)

    def get_queryset(self, request):
        """Optimise la requête"""
        qs = super().get_queryset(request)
        return qs.select_related('manifestation', 'entreprise', 'etape_actuelle').prefetch_related('manifestation__etapes')

    def changelist_view(self, request, extra_context=None):
        """Ajoute les KPI dans la vue de liste"""
        response = super().changelist_view(request, extra_context=extra_context)
        
        if hasattr(response, 'context_data'):
            queryset = self.get_queryset(request)
            
            # KPI rapides
            kpi = {
                'total': queryset.count(),
                'acceptees': queryset.filter(statut_metier='accepte', is_deleted=False).count(),
                'refusees': queryset.filter(statut_metier='refus', is_deleted=False).count(),
                'en_attente': queryset.filter(statut_metier='en_attente', is_deleted=False).count(),
                'publiees': queryset.filter(statut_back_office='publie', is_deleted=False).count(),
                'brouillons': queryset.filter(statut_back_office='brouillon', is_deleted=False).count(),
            }
            
            response.context_data['kpi'] = kpi
        
        return response


@admin.register(CandidatureEtapeHistorique)
class CandidatureEtapeHistoriqueAdmin(admin.ModelAdmin):
    """Historique des passages par étape (traçabilité). Lecture seule."""
    list_display = ('candidature', 'etape', 'date_entree', 'date_sortie')
    list_filter = ('etape__manifestation',)
    search_fields = ('candidature__nom_entreprise', 'candidature__email_contact')
    list_select_related = ('candidature', 'etape')
    ordering = ('-date_entree',)
    readonly_fields = ('candidature', 'etape', 'date_entree', 'date_sortie')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CandidatureDecision)
class CandidatureDecisionAdmin(admin.ModelAdmin):
    """Décisions admin (Accepter / Refuser). Lecture seule. Traçabilité : decision_admin, date_transition, admin_responsable."""
    list_display = ('candidature', 'decision_admin', 'etape', 'admin_responsable', 'date_transition')
    list_filter = ('decision_admin', 'etape__manifestation')
    search_fields = ('candidature__nom_entreprise', 'candidature__email_contact')
    list_select_related = ('candidature', 'etape', 'admin_responsable')
    ordering = ('-date_transition',)
    readonly_fields = ('candidature', 'decision_admin', 'etape', 'admin_responsable', 'date_transition')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Chatbot AGUIPEX (sessions, messages, mots-clés Word Cloud)
@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'created_at', 'updated_at')
    search_fields = ('session_id',)
    readonly_fields = ('session_id', 'created_at', 'updated_at')
    ordering = ('-updated_at',)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'content_preview', 'created_at')
    list_filter = ('role',)
    search_fields = ('content', 'understood_as')
    list_select_related = ('session',)
    ordering = ('-created_at',)
    readonly_fields = ('session', 'role', 'content', 'understood_as', 'created_at')

    def content_preview(self, obj):
        return (obj.content or '')[:60] + ('...' if len(obj.content or '') > 60 else '')
    content_preview.short_description = 'Contenu'


@admin.register(ExtractedKeyword)
class ExtractedKeywordAdmin(admin.ModelAdmin):
    list_display = ('word', 'weight', 'session', 'created_at')
    list_filter = ('session',)
    search_fields = ('word',)
    ordering = ('-weight', '-created_at')


# Module Statistiques
@admin.register(CategorieStatistique)
class CategorieStatistiqueAdmin(CustomAdmin):
    list_display = ('nom', 'slug', 'ordre', 'is_deleted', 'created_at')
    search_fields = ('nom',)
    ordering = ('ordre', 'nom')

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication", "statistique"]:
            return True
        return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)


@admin.register(Statistique)
class StatistiqueAdmin(CustomAdmin):
    list_display = ('titre', 'annee', 'mois', 'categorie', 'valeur', 'unite', 'ordre', 'is_deleted', 'created_at')
    list_filter = ('annee', 'mois', 'categorie')
    search_fields = ('titre', 'annee')
    list_select_related = ('categorie',)
    autocomplete_fields = ('categorie',)
    ordering = ('-annee', 'mois', 'ordre')
    list_per_page = 25
    fieldsets = (
        ('Période', {
            'fields': ('annee', 'mois')
        }),
        ('Contenu', {
            'fields': ('categorie', 'titre', 'valeur', 'unite', 'ordre')
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-excel/', self.admin_site.admin_view(self.export_excel), name='statistique_export_excel'),
            path('export-csv/', self.admin_site.admin_view(self.export_csv), name='statistique_export_csv'),
        ]
        return custom_urls + urls
    
    def export_excel(self, request):
        """Export Excel des statistiques"""
        queryset = self.get_queryset(request)
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Statistiques"
        
        headers = ['Titre', 'Année', 'Mois', 'Catégorie', 'Valeur', 'Unité', 'Ordre', 'Date Création']
        
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        for row_num, obj in enumerate(queryset, 2):
            ws.cell(row=row_num, column=1, value=obj.titre or '')
            ws.cell(row=row_num, column=2, value=obj.annee or '')
            ws.cell(row=row_num, column=3, value=obj.get_mois_display() if hasattr(obj, 'get_mois_display') else obj.mois or '')
            ws.cell(row=row_num, column=4, value=obj.categorie.nom if obj.categorie else '')
            ws.cell(row=row_num, column=5, value=obj.valeur or '')
            ws.cell(row=row_num, column=6, value=obj.unite or '')
            ws.cell(row=row_num, column=7, value=obj.ordre or '')
            ws.cell(row=row_num, column=8, value=obj.created_at.strftime('%d/%m/%Y %H:%M') if obj.created_at else '')
        
        for col_num in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col_num)].width = 20
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="statistiques_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        wb.save(response)
        return response
    
    def export_csv(self, request):
        """Export CSV des statistiques"""
        queryset = self.get_queryset(request)
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="statistiques_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Titre', 'Année', 'Mois', 'Catégorie', 'Valeur', 'Unité', 'Ordre', 'Date Création'])
        
        for obj in queryset:
            writer.writerow([
                obj.titre or '',
                obj.annee or '',
                obj.get_mois_display() if hasattr(obj, 'get_mois_display') else obj.mois or '',
                obj.categorie.nom if obj.categorie else '',
                obj.valeur or '',
                obj.unite or '',
                obj.ordre or '',
                obj.created_at.strftime('%d/%m/%Y %H:%M') if obj.created_at else '',
            ])
        
        return response

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication", "statistique"]:
            return True
        return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)


# Mot du Directeur
@admin.register(MotDirecteur)
class MotDirecteurAdmin(CustomAdmin):
    form = MotDirecteurAdminForm
    list_display = ('titre', 'nomDG', 'poste', 'status', 'is_deleted', 'created_at', 'updated_at', 'image_preview')
    list_filter = ('status',)
    search_fields = ('titre', 'nomDG', 'poste')
    readonly_fields = ('image_preview',)
    def image_preview(self, obj):
        return image_preview(obj)
    
    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication"]:
            return True
        return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)
    

# Mot du Directeur
@admin.register(Service)
class ServiceAdmin(CustomAdmin):
    list_display = ('title', 'axe1', 'axe2', 'axe3', 'axe4', 'status', 'is_deleted', 'created_at', 'updated_at', 'image_preview')
    list_filter = ('status',)
    search_fields = ('title',)
    readonly_fields = ('image_preview',)
    exclude = ('slug',)
    def image_preview(self, obj):
        return image_preview(obj)
    
    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication"]:
            return True
        return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)
    

# Vision et Mission
@admin.register(VisionMission)
class VisionMissionAdmin(CustomAdmin):
    list_display = ('texte_mission', 'texte_vision', 'status', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('texte_mission', 'texte_vision')

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication"]:
            return True
        return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)

# Formulaire personnalisé pour Entreprise avec CKEditor
class EntrepriseAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(config_name='default'), required=False)
    adresse = forms.CharField(widget=CKEditorWidget(config_name='simple'), required=False)
    certifications = forms.CharField(widget=CKEditorWidget(config_name='default'), required=False)
    
    class Meta:
        model = aguipex_models.Entreprise
        fields = '__all__'

# Filtres personnalisés pour Entreprise
class StatusFilter(admin.SimpleListFilter):
    title = 'Statut'
    parameter_name = 'status_filter'

    def lookups(self, request, model_admin):
        return (
            ('publier', 'Publiées'),
            ('brouillon', 'Brouillons'),
            ('toutes', 'Toutes'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'publier':
            return queryset.filter(status='publier')
        elif self.value() == 'brouillon':
            return queryset.filter(status='brouillon')
        return queryset

class VilleFilter(admin.SimpleListFilter):
    title = 'Ville'
    parameter_name = 'ville_filter'

    def lookups(self, request, model_admin):
        villes = aguipex_models.Entreprise.objects.values_list('ville', flat=True).distinct().order_by('ville')
        return [(ville, ville) for ville in villes if ville]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(ville=self.value())
        return queryset

class DateCreationFilter(admin.SimpleListFilter):
    title = 'Date de création'
    parameter_name = 'date_creation_filter'

    def lookups(self, request, model_admin):
        return (
            ('today', "Aujourd'hui"),
            ('week', 'Cette semaine'),
            ('month', 'Ce mois'),
            ('year', 'Cette année'),
            ('older', 'Plus ancien'),
        )

    def queryset(self, request, queryset):
        today = datetime.now().date()
        if self.value() == 'today':
            return queryset.filter(created_at__date=today)
        elif self.value() == 'week':
            week_ago = today - timedelta(days=7)
            return queryset.filter(created_at__date__gte=week_ago)
        elif self.value() == 'month':
            month_ago = today - timedelta(days=30)
            return queryset.filter(created_at__date__gte=month_ago)
        elif self.value() == 'year':
            year_ago = today - timedelta(days=365)
            return queryset.filter(created_at__date__gte=year_ago)
        elif self.value() == 'older':
            year_ago = today - timedelta(days=365)
            return queryset.filter(created_at__date__lt=year_ago)
        return queryset

class ProduitsCountFilter(admin.SimpleListFilter):
    title = 'Nombre de produits'
    parameter_name = 'produits_count_filter'

    def lookups(self, request, model_admin):
        return (
            ('0', 'Aucun produit'),
            ('1-5', '1 à 5 produits'),
            ('6-10', '6 à 10 produits'),
            ('10+', 'Plus de 10 produits'),
        )

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.annotate(prod_count=Count('produits_entreprise')).filter(prod_count=0)
        elif self.value() == '1-5':
            return queryset.annotate(prod_count=Count('produits_entreprise')).filter(prod_count__gte=1, prod_count__lte=5)
        elif self.value() == '6-10':
            return queryset.annotate(prod_count=Count('produits_entreprise')).filter(prod_count__gte=6, prod_count__lte=10)
        elif self.value() == '10+':
            return queryset.annotate(prod_count=Count('produits_entreprise')).filter(prod_count__gt=10)
        return queryset

# entreprise
@admin.register(aguipex_models.Entreprise)
class EntrepriseAdmin(CustomAdmin):
    form = EntrepriseAdminForm
    list_display = ('nom', 'type_activite', 'ville', 'get_produits_count', 'telephone', 'email', 'status', 'is_deleted', 'created_at')
    list_filter = (StatusFilter, VilleFilter, 'type_activite', DateCreationFilter, ProduitsCountFilter, 'is_deleted', 'created_at')
    search_fields = ('nom', 'type_activite', 'secteur_activite', 'ville', 'email', 'telephone', 'description')
    readonly_fields = ('created_at', 'updated_at', 'get_produits_count_display')
    exclude = ('slug',)
    list_per_page = 50
    list_max_show_all = 200
    
    # Actions en masse
    actions = ['publier_selected', 'mettre_en_brouillon_selected', 'soft_delete_selected']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'description', 'type_activite', 'secteur_activite')
        }),
        ('Contact', {
            'fields': ('adresse', 'ville', 'telephone', 'email', 'site_web')
        }),
        ('Images', {
            'fields': ('logo', 'image_couverture')
        }),
        ('Informations complémentaires', {
            'fields': ('date_creation', 'nombre_employes', 'certifications')
        }),
        ('Statistiques', {
            'fields': ('get_produits_count_display',),
            'classes': ('collapse',)
        }),
        ('Foire (optionnel)', {
            'fields': ('foire',),
            'classes': ('collapse',)
        }),
        ('Statut', {
            'fields': ('status', 'is_deleted')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('kpi-stats/', self.admin_site.admin_view(self.kpi_stats_view), name='entreprise_kpi_stats'),
            path('export-excel/', self.admin_site.admin_view(self.export_excel), name='entreprise_export_excel'),
            path('export-csv/', self.admin_site.admin_view(self.export_csv), name='entreprise_export_csv'),
        ]
        return custom_urls + urls
    
    def export_excel(self, request):
        """Export Excel des entreprises"""
        queryset = self.get_queryset(request)
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Entreprises"
        
        headers = [
            'Nom', 'Type Activité', 'Secteur Activité', 'Ville', 'Adresse',
            'Téléphone', 'Email', 'Site Web', 'Date Création', 'Nombre Employés',
            'Status', 'Date Enregistrement'
        ]
        
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        for row_num, obj in enumerate(queryset, 2):
            ws.cell(row=row_num, column=1, value=obj.nom or '')
            ws.cell(row=row_num, column=2, value=obj.type_activite or '')
            ws.cell(row=row_num, column=3, value=obj.secteur_activite or '')
            ws.cell(row=row_num, column=4, value=obj.ville or '')
            ws.cell(row=row_num, column=5, value=_strip_html(obj.adresse or ''))
            ws.cell(row=row_num, column=6, value=obj.telephone or '')
            ws.cell(row=row_num, column=7, value=obj.email or '')
            ws.cell(row=row_num, column=8, value=obj.site_web or '')
            ws.cell(row=row_num, column=9, value=obj.date_creation.strftime('%d/%m/%Y') if obj.date_creation else '')
            ws.cell(row=row_num, column=10, value=obj.nombre_employes or '')
            ws.cell(row=row_num, column=11, value=obj.get_status_display())
            ws.cell(row=row_num, column=12, value=obj.created_at.strftime('%d/%m/%Y %H:%M') if obj.created_at else '')
        
        for col_num in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col_num)].width = 20
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="entreprises_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        wb.save(response)
        return response
    
    def export_csv(self, request):
        """Export CSV des entreprises"""
        queryset = self.get_queryset(request)
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="entreprises_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Nom', 'Type Activité', 'Secteur Activité', 'Ville', 'Adresse',
            'Téléphone', 'Email', 'Site Web', 'Date Création', 'Nombre Employés',
            'Status', 'Date Enregistrement'
        ])
        
        for obj in queryset:
            writer.writerow([
                obj.nom or '',
                obj.type_activite or '',
                obj.secteur_activite or '',
                obj.ville or '',
                _strip_html(obj.adresse or ''),
                obj.telephone or '',
                obj.email or '',
                obj.site_web or '',
                obj.date_creation.strftime('%d/%m/%Y') if obj.date_creation else '',
                obj.nombre_employes or '',
                obj.get_status_display(),
                obj.created_at.strftime('%d/%m/%Y %H:%M') if obj.created_at else '',
            ])
        
        return response

    def kpi_stats_view(self, request):
        """Vue pour afficher les KPI des entreprises"""
        queryset = self.get_queryset(request)
        
        # Calcul des KPI
        total = queryset.count()
        publiees = queryset.filter(status='publier', is_deleted=False).count()
        brouillons = queryset.filter(status='brouillon', is_deleted=False).count()
        supprimees = queryset.filter(is_deleted=True).count()
        
        # Entreprises avec produits
        avec_produits = queryset.annotate(prod_count=Count('produits_entreprise')).filter(prod_count__gt=0).count()
        sans_produits = total - avec_produits
        
        # Par ville (top 5)
        top_villes = queryset.values('ville').annotate(count=Count('id')).order_by('-count')[:5]
        
        # Par type d'activité (top 5)
        top_types = queryset.values('type_activite').annotate(count=Count('id')).order_by('-count')[:5]
        
        # Évolution (7 derniers jours)
        evolution = []
        for i in range(6, -1, -1):
            date = datetime.now().date() - timedelta(days=i)
            count = queryset.filter(created_at__date=date).count()
            evolution.append({'date': date.strftime('%d/%m'), 'count': count})
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Statistiques des Entreprises',
            'kpi': {
                'total': total,
                'publiees': publiees,
                'brouillons': brouillons,
                'supprimees': supprimees,
                'avec_produits': avec_produits,
                'sans_produits': sans_produits,
                'top_villes': top_villes,
                'top_types': top_types,
                'evolution': evolution,
            }
        }
        return TemplateResponse(request, 'admin/entreprise_kpi_stats.html', context)

    def get_produits_count(self, obj):
        """Affiche le nombre de produits avec un badge coloré"""
        count = obj.produits_entreprise.filter(is_deleted=False).count()
        if count == 0:
            color = '#dc3545'  # Rouge
        elif count < 5:
            color = '#ffc107'  # Jaune
        else:
            color = '#28a745'  # Vert
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-weight: bold; font-size: 0.85rem;">{}</span>',
            color, count
        )
    get_produits_count.short_description = 'Produits'
    get_produits_count.admin_order_field = 'produits_entreprise__count'

    def get_produits_count_display(self, obj):
        """Affiche le nombre de produits dans le formulaire"""
        if obj.pk:
            count = obj.produits_entreprise.filter(is_deleted=False).count()
            return format_html(
                '<div style="padding: 10px; background: #f8f9fa; border-radius: 5px;"><strong>Nombre de produits :</strong> {}</div>',
                count
            )
        return "Enregistrez d'abord l'entreprise pour voir le nombre de produits"
    get_produits_count_display.short_description = 'Nombre de produits'

    @admin.action(description="Publier les entreprises sélectionnées")
    def publier_selected(self, request, queryset):
        count = queryset.update(status='publier')
        self.message_user(request, f"{count} entreprise(s) ont été publiée(s).", messages.SUCCESS)

    @admin.action(description="Mettre en brouillon les entreprises sélectionnées")
    def mettre_en_brouillon_selected(self, request, queryset):
        count = queryset.update(status='brouillon')
        self.message_user(request, f"{count} entreprise(s) ont été mise(s) en brouillon.", messages.SUCCESS)

    def get_queryset(self, request):
        """Optimise la requête avec select_related et prefetch_related"""
        qs = super().get_queryset(request)
        return qs.select_related('foire').prefetch_related('produits_entreprise')

    def changelist_view(self, request, extra_context=None):
        """Ajoute les KPI dans la vue de liste"""
        response = super().changelist_view(request, extra_context=extra_context)
        
        if hasattr(response, 'context_data'):
            queryset = self.get_queryset(request)
            
            # KPI rapides
            kpi = {
                'total': queryset.count(),
                'publiees': queryset.filter(status='publier', is_deleted=False).count(),
                'brouillons': queryset.filter(status='brouillon', is_deleted=False).count(),
                'avec_produits': queryset.annotate(prod_count=Count('produits_entreprise')).filter(prod_count__gt=0).count(),
            }
            
            response.context_data['kpi'] = kpi
        
        return response

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication", "marketing"]:
            return True
        return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)


# TypeProduit
@admin.register(aguipex_models.TypeProduit)
class TypeProduitAdmin(CustomAdmin):
    list_display = ('nom', 'ordre', 'status', 'is_deleted', 'created_at')
    list_filter = ('status',)
    search_fields = ('nom', 'description')
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('slug',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'description', 'icone', 'ordre')
        }),
        ('Statut', {
            'fields': ('status', 'is_deleted')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication", "marketing"]:
            return True
        return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)


# ProduitEntreprise
@admin.register(aguipex_models.ProduitEntreprise)
class ProduitEntrepriseAdmin(CustomAdmin):
    list_display = ('nom', 'get_entreprise_display', 'get_type_produit_display', 'status', 'is_deleted', 'created_at')
    list_filter = ('status', 'type_produit', 'is_deleted')
    search_fields = ('nom', 'description_courte', 'entreprise__nom', 'type_produit__nom')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    exclude = ()
    
    fieldsets = (
        ('Informations du produit', {
            'fields': ('entreprise', 'type_produit', 'nom', 'description_courte', 'image')
        }),
        ('Aperçu', {
            'fields': ('image_preview',)
        }),
        ('Statut', {
            'fields': ('status', 'is_deleted')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 200px;" />', obj.image.url)
        return "Aucune image"
    image_preview.short_description = 'Aperçu'
    
    def get_entreprise_display(self, obj):
        return obj.entreprise.nom if obj.entreprise else "—"
    get_entreprise_display.short_description = 'Entreprise'
    
    def get_type_produit_display(self, obj):
        return obj.type_produit.nom if obj.type_produit else "—"
    get_type_produit_display.short_description = 'Type de produit'

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication", "marketing"]:
            return True
        return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)


# Foire
@admin.register(Foires)
class FoireAdmin(CustomAdmin):
    list_display = ('titre', 'date_debut', 'date_fin', 'pays', 'lieu', 'type', 'realisation', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('status', 'type', 'realisation',)
    search_fields = ('titre', 'description',)
    exclude = ('slug',)
    readonly_fields = ('image_preview',)
    inlines = [ImageFoireInline]
    def image_preview(self, obj):
        return image_preview(obj)
    
    def has_view_permission(self, request, obj=None):
        # Le superadmin voit tout
        if request.user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur est authentifié avant d'accéder à son role
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication", "marketing"]:
            return True
        return False

    def has_module_permission(self, request):
        """Empêche complètement l'accès au module si l'utilisateur n'a pas la permission."""
        return self.has_view_permission(request)



# Categorie d'actualité
@admin.register(CategorieActuality)
class CategorieActualityAdmin(CustomAdmin):
    list_display = ('name', 'status', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('name',)
    exclude = ('slug',)

    def has_view_permission(self, request, obj=None):
        # Le superadmin voit tout
        if request.user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur est authentifié avant d'accéder à son role
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication"]:
            return True
        return False

    def has_module_permission(self, request):
        """Empêche complètement l'accès au module si l'utilisateur n'a pas la permission."""
        return self.has_view_permission(request)

# Valeur
@admin.register(Valeur)
class ValeurAdmin(CustomAdmin):
    form = ValeurAdminForm
    list_display = ('titre', 'numero', 'status', 'is_deleted', 'created_at', 'updated_at', 'icone')
    list_filter = ('status',)
    search_fields = ('titre', 'contenu')
    readonly_fields = ('icone',)
    def icone(self, obj):
        return image_preview(obj)
    
    def has_view_permission(self, request, obj=None):
        # Le superadmin voit tout
        if request.user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur est authentifié avant d'accéder à son role
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication"]:
            return True
        return False

    def has_module_permission(self, request):
        """Empêche complètement l'accès au module si l'utilisateur n'a pas la permission."""
        return self.has_view_permission(request)

# Actualité
@admin.register(Actualite)
class ActualiteAdmin(CustomAdmin):
    form = ActualiteAdminForm
    list_display = ('grand_titre', 'date_actualite', 'category', 'status', 'featured', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('grand_titre', )
    exclude = ('slug',)
    # inlines = [ImageActualiteInline]

    def has_view_permission(self, request, obj=None):
        # Le superadmin voit tout
        if request.user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur est authentifié avant d'accéder à son role
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication"]:
            return True
        return False

    def has_module_permission(self, request):
        """Empêche complètement l'accès au module si l'utilisateur n'a pas la permission."""
        return self.has_view_permission(request)


# Gouvernance
@admin.register(Gouvernance)
class GouvernanceAdmin(CustomAdmin):
    form = GouvernanceAdminForm
    list_display = ('nom', 'poste', 'status', 'is_deleted', 'created_at', 'updated_at', 'image_preview')
    list_filter = ('status',)
    search_fields = ('nom', 'poste', 'contenu')
    readonly_fields = ('image_preview',)
    def image_preview(self, obj):
        return image_preview(obj)
    
    def has_view_permission(self, request, obj=None):
        # Le superadmin voit tout
        if request.user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur est authentifié avant d'accéder à son role
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication"]:
            return True
        return False

    def has_module_permission(self, request):
        """Empêche complètement l'accès au module si l'utilisateur n'a pas la permission."""
        return self.has_view_permission(request)
    
# ActivityFoire
@admin.register(ActivityFoire)
class ActivityFoireAdmin(CustomAdmin):
    list_display = ('title', 'status', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('title', 'description')
    inlines = [ImageActivitiesInline]
    exclude = ('slug',)


    def has_view_permission(self, request, obj=None):
        # Le superadmin voit tout
        if request.user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur est authentifié avant d'accéder à son role
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication", "marketing"]:
            return True
        return False

    def has_module_permission(self, request):
        """Empêche complètement l'accès au module si l'utilisateur n'a pas la permission."""
        return self.has_view_permission(request)


# Espace Média
@admin.register(EspaceMedia)
class EspaceMediaAdmin(CustomAdmin):
    list_display = ('titre', 'status', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('titre', )
    inlines = [ImageMediaInline]
    exclude = ('slug',)

    def has_view_permission(self, request, obj=None):
        # Le superadmin voit tout
        if request.user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur est authentifié avant d'accéder à son role
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication"]:
            return True
        return False

    def has_module_permission(self, request):
        """Empêche complètement l'accès au module si l'utilisateur n'a pas la permission."""
        return self.has_view_permission(request)


# contact
@admin.register(Contact)
class ContactAdmin(CustomAdmin):
    form = ContactAdminForm
    list_display = ('name', 'phone', 'email', 'subject', 'message', 'is_deleted', 'created_at', 'updated_at',)
    list_filter = ('email',)
    search_fields = ('name', 'email')

    def has_view_permission(self, request, obj=None):
        # Le superadmin voit tout
        if request.user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur est authentifié avant d'accéder à son role
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication"]:
            return True
        return False

    def has_module_permission(self, request):
        """Empêche complètement l'accès au module si l'utilisateur n'a pas la permission."""
        return self.has_view_permission(request)

@admin.register(FAQ)
class FaqAdmin(CustomAdmin):
    form = FAQAdminForm
    list_display = ('question', 'response', 'status', 'featured', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('question', )

    def has_view_permission(self, request, obj=None):
        # Le superadmin voit tout
        if request.user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur est authentifié avant d'accéder à son role
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication"]:
            return True
        return False

    def has_module_permission(self, request):
        """Empêche complètement l'accès au module si l'utilisateur n'a pas la permission."""
        return self.has_view_permission(request)
    
@admin.register(DonneeStrategique)
class DonneeStrategiqueAdmin(CustomAdmin):
    list_display = ('titre', 'detail', 'status', 'featured', 'is_deleted', 'created_at', 'updated_at', 'image_preview')
    list_filter = ('status',)
    search_fields = ('titre', 'detail')
    readonly_fields = ('image_preview',)
    exclude = ('slug',)
    def image_preview(self, obj):
        return image_preview(obj)

    def has_view_permission(self, request, obj=None):
        # Le superadmin voit tout
        if request.user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur est authentifié avant d'accéder à son role
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication", "statistique"]:
            return True
        return False

    def has_module_permission(self, request):
        """Empêche complètement l'accès au module si l'utilisateur n'a pas la permission."""
        return self.has_view_permission(request)
    


@admin.register(CertificationTechnique)
class CertificationTechniqueAdmin(CustomAdmin):
    list_display = ('titre', 'description', 'status', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('titre', 'description')

    def has_view_permission(self, request, obj=None):
        # Le superadmin voit tout
        if request.user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur est authentifié avant d'accéder à son role
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication", "certification"]:
            return True
        return False

    def has_module_permission(self, request):
        """Empêche complètement l'accès au module si l'utilisateur n'a pas la permission."""
        return self.has_view_permission(request)
    

@admin.register(CertificationConventionnel)
class CertificationConventionnelAdmin(CustomAdmin):
    list_display = ('titre', 'description', 'status', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('titre', 'description')

    def has_view_permission(self, request, obj=None):
        # Le superadmin voit tout
        if request.user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur est authentifié avant d'accéder à son role
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication", "certification"]:
            return True
        return False

    def has_module_permission(self, request):
        """Empêche complètement l'accès au module si l'utilisateur n'a pas la permission."""
        return self.has_view_permission(request)
    

@admin.register(ProcedureProduct)
class ProcedureProductAdmin(CustomAdmin):
    list_display = ('product', 'voie_exportation','get_certificat_technique', 'certificat_conventionnel', 'status', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('product',)
    search_fields = ('product',)

    def has_view_permission(self, request, obj=None):
        # Le superadmin voit tout
        if request.user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur est authentifié avant d'accéder à son role
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication", "certification"]:
            return True
        return False

    def has_module_permission(self, request):
        """Empêche complètement l'accès au module si l'utilisateur n'a pas la permission."""
        return self.has_view_permission(request)
    
    def get_certificat_technique(self, obj):
        return ", ".join([c.titre for c in obj.certificat_technique.all()])
    get_certificat_technique.short_description = "Certificats Techniques"
    
@admin.register(ProcedureGlobale)
class ProcedureGlobaleAdmin(CustomAdmin):
    list_display = ('titre', 'status', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('titre',)

    def has_view_permission(self, request, obj=None):
        # Le superadmin voit tout
        if request.user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur est authentifié avant d'accéder à son role
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication", "certification"]:
            return True
        return False

    def has_module_permission(self, request):
        """Empêche complètement l'accès au module si l'utilisateur n'a pas la permission."""
        return self.has_view_permission(request)


@admin.register(aguipex_models.InfrastructureExportation)
class InfrastructureExportationAdmin(CustomAdmin):
    list_display = ('titre', 'ordre', 'status', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('titre', 'description', 'icone')
    ordering = ('ordre', 'created_at')

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated and getattr(request.user, "role", None) in ["communication", "certification"]:
            return True
        return False

    def has_module_permission(self, request):
        return self.has_view_permission(request)







admin.site.register(aguipex_models.Ville)

@admin.register(aguipex_models.Visiteur)
class VisiteurAdmin(admin.ModelAdmin):
    list_display = ('nom_complet', 'email', 'pays', 'ville_residence', 'telephone', 'date_visite', 'ip_address')
    list_filter = ('pays', 'ville_residence', 'date_visite')
    search_fields = ('nom_complet', 'email', 'pays', 'ville_residence')
    readonly_fields = ('date_visite', 'ip_address')
    ordering = ('-date_visite',)
    
    def has_add_permission(self, request):
        return False  # Empêcher l'ajout manuel
    
    def has_change_permission(self, request, obj=None):
        return False  # Empêcher la modification


@admin.register(aguipex_models.Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'nom', 'prenom', 'pays', 'ville', 'secteur_activite', 'est_actif', 'date_inscription', 'source_inscription')
    list_filter = ('est_actif', 'pays', 'ville', 'secteur_activite', 'source_inscription', 'date_inscription')
    search_fields = ('email', 'nom', 'prenom', 'pays', 'ville')
    readonly_fields = ('date_inscription', 'ip_inscription')
    list_editable = ('est_actif',)
    actions = ['activer_abonnements', 'desactiver_abonnements', 'exporter_emails']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('email', 'nom', 'prenom')
        }),
        ('Localisation', {
            'fields': ('pays', 'ville')
        }),
        ('Activité', {
            'fields': ('secteur_activite',)
        }),
        ('Statut', {
            'fields': ('est_actif', 'source_inscription')
        }),
        ('Informations techniques', {
            'fields': ('date_inscription', 'ip_inscription'),
            'classes': ('collapse',)
        })
    )
    
    def activer_abonnements(self, request, queryset):
        updated = queryset.update(est_actif=True)
        self.message_user(request, f'{updated} abonnement(s) activé(s) avec succès.')
    activer_abonnements.short_description = "Activer les abonnements sélectionnés"
    
    def desactiver_abonnements(self, request, queryset):
        updated = queryset.update(est_actif=False)
        self.message_user(request, f'{updated} abonnement(s) désactivé(s) avec succès.')
    desactiver_abonnements.short_description = "Désactiver les abonnements sélectionnés"
    
    def exporter_emails(self, request, queryset):
        emails = queryset.filter(est_actif=True).values_list('email', flat=True)
        response = HttpResponse('\n'.join(emails), content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="emails_newsletter.txt"'
        return response
    exporter_emails.short_description = "Exporter les emails actifs"


@admin.register(aguipex_models.NewsletterTemplate)
class NewsletterTemplateAdmin(admin.ModelAdmin):
    list_display = ('titre', 'sujet', 'est_actif', 'date_creation', 'date_modification')
    list_filter = ('est_actif', 'date_creation')
    search_fields = ('titre', 'sujet')
    list_editable = ('est_actif',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'sujet', 'est_actif')
        }),
        ('Contenu', {
            'fields': ('contenu_html', 'contenu_texte')
        })
    )
    
    def save_model(self, request, obj, form, change):
        # Si c'est un nouveau template, le rendre actif et désactiver les autres
        if not change and obj.est_actif:
            aguipex_models.NewsletterTemplate.objects.filter(est_actif=True).update(est_actif=False)
        super().save_model(request, obj, form, change)


@admin.register(aguipex_models.NewsletterEnvoi)
class NewsletterEnvoiAdmin(admin.ModelAdmin):
    list_display = ('template', 'sujet', 'nombre_destinataires', 'nombre_envoyes', 'nombre_erreurs', 'statut', 'date_envoi')
    list_filter = ('statut', 'template', 'date_envoi')
    search_fields = ('sujet', 'template__titre')
    readonly_fields = ('date_envoi', 'nombre_destinataires', 'nombre_envoyes', 'nombre_erreurs')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('template', 'sujet', 'statut')
        }),
        ('Statistiques', {
            'fields': ('nombre_destinataires', 'nombre_envoyes', 'nombre_erreurs', 'date_envoi')
        }),
        ('Détails des erreurs', {
            'fields': ('details_erreur',),
            'classes': ('collapse',)
        })
    )
    
    def has_add_permission(self, request):
        return False  # Empêcher l'ajout manuel
    
    def has_change_permission(self, request, obj=None):
        return False  # Empêcher la modification

