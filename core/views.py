from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from core import models as aguipex_models
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Q, Prefetch, Count
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from core.forms import CandidatureManifestationForm
from core.models import MAX_ORDRE_ETAPE_PAR_STATUT, CANDIDATURES_VISIBLES_FRONT_Q
# Create your views here.

def index(request):
    slides = aguipex_models.Slide.objects.filter(status="publier", is_deleted=False).order_by("-created_at")
    about = aguipex_models.QuiSommeNous.objects.filter(status="publier", is_deleted=False).order_by('-created_at').first()
    actualites = aguipex_models.Actualite.objects.filter(status="publier", is_deleted=False).order_by('-created_at')
    produits = aguipex_models.Produit.objects.filter(status="publier", pour_site=True, is_deleted=False).order_by('-created_at')
    programmes = aguipex_models.Programme.objects.filter(status="publier", is_deleted=False).order_by("-created_at")
    evenements = aguipex_models.Evenement.objects.filter(status="publier", is_deleted=False).order_by('-created_at')
    temoignages = aguipex_models.Temoignage.objects.filter(status="publier", is_deleted=False).order_by('-created_at')
    


    context = {
        'slides':slides,
        'about':about,
        'actualites':actualites,
        'produits':produits,
        'programmes':programmes,
        'evenements':evenements,
        'temoignages':temoignages,
    }
    return render(request, 'aguipex/index.html', context)

def about(request):
    mot_directeur = aguipex_models.MotDirecteur.objects.filter(status="publier", is_deleted=False).order_by('-created_at').first()
    vision_mission = aguipex_models.VisionMission.objects.filter(status="publier", is_deleted=False).order_by('-created_at').first()
    valeurs = aguipex_models.Valeur.objects.filter(status="publier", is_deleted=False).order_by('-created_at')
    gouvernances = aguipex_models.Gouvernance.objects.filter(status="publier", is_deleted=False)
    context = {
        "mot_directeur":mot_directeur,
        "vision_mission":vision_mission,
        "valeurs":valeurs,
        "gouvernances":gouvernances,
    }
    return render(request, "aguipex/about.html", context)

def equipe(request):
    equipes = aguipex_models.Equipe.objects.filter(status="publier")
    context = {
        "equipes":equipes
    }
    return render(request, "aguipex/equipe.html", context)


def actualite(request):
    actualites = aguipex_models.Actualite.objects.filter(status="publier").order_by('-created_at')
    context = {
        'actualites':actualites
    }
    return render(request, "aguipex/actualite.html", context)

def detail_actualite(request, slug):
    actualite = get_object_or_404(aguipex_models.Actualite, slug=slug, status="publier", is_deleted=False)
    autres_actualites = aguipex_models.Actualite.objects.filter(status="publier", is_deleted=False)
    context = {
        'actualite':actualite,
        'autres_actualites':autres_actualites
    }
    return render(request, 'aguipex/detail_actualite.html', context)



def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('object')  # Correspond à "Objet" dans le formulaire
        phone = request.POST.get('number', '')  # Optionnel
        message = request.POST.get('message')

        if name and email and message:
            # Enregistrement en base de données
            aguipex_models.Contact.objects.create(name=name, email=email, subject=subject, phone=phone, message=message)
            return JsonResponse({'success': True, 'message': 'Votre message a été envoyé avec succès !'})

        return JsonResponse({'success': False, 'message': 'Veuillez remplir tous les champs obligatoires.'})

    # Afficher la page HTML en cas de requête GET
    return render(request, "aguipex/contact.html")

def detail_programme(request, slug):
    programme = get_object_or_404(aguipex_models.Programme, slug=slug, status="publier", is_deleted=False)
    context = {
        'programme':programme,
        'request': request
    }
    return render(request, "aguipex/detail_programme.html", context)

def donnees_strategique(request):
    donnees_strategiques = aguipex_models.DonneeStrategique.objects.filter(status="publier", is_deleted=False).order_by('-created_at')
    context = {
        'donnees_strategiques':donnees_strategiques
    }
    return render(request, 'aguipex/donnees_strategique.html', context)


def detail_donnee_strategique(request, slug):
    donnee = get_object_or_404(aguipex_models.DonneeStrategique, slug=slug, status="publier", is_deleted=False)
    autres_donnees = aguipex_models.DonneeStrategique.objects.filter(status="publier", is_deleted=False)
    context = {
        'donnee':donnee,
        'autres_donnees':autres_donnees
    }
    return render(request, 'aguipex/detail_donnee_strategique.html', context)


def faq(request):
    faqs = aguipex_models.FAQ.objects.filter(status="publier", is_deleted=False).order_by("-created_at")
    context = {
        'faqs':faqs
    }
    return render(request, 'aguipex/faq.html', context)



def espace_media(request):
    espace_medias = aguipex_models.EspaceMedia.objects.filter(status="publier", is_deleted=False).order_by("-created_at")
    context = {
        'espace_medias':espace_medias
    }
    return render(request, 'aguipex/espace_media.html', context)

def detail_espace_media(request, slug):
    espace_media = get_object_or_404(aguipex_models.EspaceMedia, slug=slug, status="publier", is_deleted=False)
    context = {
        'espace_media':espace_media
    }
    return render(request, 'aguipex/detail_espace_media.html', context)



def offres_service(request):
    services = aguipex_models.Service.objects.filter(status="publier", is_deleted=False).order_by('-created_at')
    context = {
        'services':services
    }
    return render(request, 'aguipex/offres_de_service.html', context)


def potentiels_exportation(request):
    produits = aguipex_models.Produit.objects.filter(status="publier", pour_site=True, is_deleted=False).order_by("-created_at")
    procedure_globales = aguipex_models.ProcedureGlobale.objects.filter(status="publier", is_deleted=False).order_by("created_at")
    
    # Produits uniques à partir des procédures publiées
    procedures = aguipex_models.ProcedureProduct.objects.filter(status="publier", is_deleted=False)
    voie_exportations = aguipex_models.ProcedureProduct.objects.filter(status="publier", is_deleted=False)
    produits_ids = procedures.values_list('product_id', flat=True).distinct()
    produits_uniques = aguipex_models.Produit.objects.filter(id__in=produits_ids)

    context = {
        'products': produits_uniques,  # <== à utiliser dans le template
        'procedure_globales': procedure_globales,
        'procedure_products': procedures,  # pour gérer les voies d'exportation en JS par exemple
        'produits':produits,
        'voie_exportations':voie_exportations,
    }
    return render(request, 'aguipex/potentiels_exportation.html', context)



def get_exportation_details(request):
    """ Vue pour récupérer les détails en fonction du produit et de la voie d'exportation """
    procedure_id = request.GET.get('procedure_id')
    voie_exportation = request.GET.get('voie_exportation')

    if not procedure_id or not voie_exportation:
        return JsonResponse({"error": "Paramètres manquants"}, status=400)

    try:
        procedure = aguipex_models.ProcedureProduct.objects.get(
            id=procedure_id,
            voie_exportation=voie_exportation,
            status="publier",
            is_deleted=False
        )
        data = {
            "product": procedure.product.title,
            "image": procedure.product.image.url,
            "voie_exportation": procedure.voie_exportation,
            "formalisation": procedure.formalisation,
            "dde": procedure.dde,
            "certificat_technique": procedure.certificat_technique.titre,
            "certificat_conventionnel": procedure.certificat_conventionnel.titre,
            "autorisation": procedure.autorisation,
            "redevance": procedure.redevance,
            "formalite_douane": procedure.formalite_douane,
            "nb": procedure.nb,
        }
        return JsonResponse(data)
    except aguipex_models.ProcedureProduct.DoesNotExist:
        return JsonResponse({"error": "Données invalides"}, status=404)
    


def get_voies_by_produit(request):
    product_id = request.GET.get('product_id')

    if not product_id:
        return JsonResponse({'error': 'Produit non fourni'}, status=400)

    voies = aguipex_models.ProcedureProduct.objects.filter(
        product_id=product_id,
        status='publier',
        is_deleted=False
    ).values_list('voie_exportation', flat=True).distinct()

    return JsonResponse({'voies': list(voies)})


def get_procedure_details(request):
    product_id = request.GET.get('product_id')
    voie_exportation = request.GET.get('voie_exportation')

    try:
        procedure = aguipex_models.ProcedureProduct.objects.get(
            product_id=product_id,
            voie_exportation=voie_exportation,
            status='publier',
            is_deleted=False
        )

        data = {
            "product": procedure.product.title,
            "voie_exportation": procedure.voie_exportation,
            'formalisation': procedure.formalisation,
            'dde': procedure.dde,
            'certificat_technique': ", ".join([ct.titre for ct in procedure.certificat_technique.all()]),
            'certificat_conventionnel': procedure.certificat_conventionnel.titre,
            'autorisation': procedure.autorisation,
            'redevance': procedure.redevance,
            'formalite_douane': procedure.formalite_douane,
            'nb': procedure.nb,
            'image': procedure.product.image.url if procedure.product.image else ''

        }

        return JsonResponse(data)
    except aguipex_models.ProcedureProduct.DoesNotExist:
        return JsonResponse({'error': 'Aucune procédure trouvée'}, status=404)




def foires(request):
    foire_nationales_encours = aguipex_models.Foires.objects.filter(status="publier", is_deleted=False, type="FOIRE_NATIONALE", realisation="en_cours")
    foire_internationales_encours = aguipex_models.Foires.objects.filter(status="publier", is_deleted=False, type="FOIRE_INTERNATIONALE", realisation="en_cours")
    foire_nationales_terminer = aguipex_models.Foires.objects.filter(status="publier", is_deleted=False, type="FOIRE_NATIONALE", realisation="terminer")
    foire_internationales_terminer = aguipex_models.Foires.objects.filter(status="publier", is_deleted=False, type="FOIRE_INTERNATIONALE", realisation="terminer")

    # Calcul des statistiques
    total_foires_realisees = foire_nationales_terminer.count() + foire_internationales_terminer.count()
    total_foires_encours = foire_nationales_encours.count() + foire_internationales_encours.count()
    total_entreprises_accompagnees = aguipex_models.Foires.objects.aggregate(Sum('nbre_entreprise'))['nbre_entreprise__sum'] or 0
    total_produits_vendus = aguipex_models.Foires.objects.aggregate(Sum('nbre_produit_vendu'))['nbre_produit_vendu__sum'] or 0

    context = {
        'foire_nationales_encours': foire_nationales_encours,
        'foire_internationales_encours': foire_internationales_encours,
        'foire_nationales_terminer': foire_nationales_terminer,
        'foire_internationales_terminer': foire_internationales_terminer,
        'total_foires_realisees': total_foires_realisees,
        'total_foires_encours': total_foires_encours,
        'total_entreprises_accompagnees': total_entreprises_accompagnees,
        'total_produits_vendus': total_produits_vendus,
    }
    return render(request, 'aguipex/foire.html', context)

def foire_detail(request, slug):
    foire = get_object_or_404(aguipex_models.Foires, slug=slug, status="publier", is_deleted=False)
    entreprises = foire.entreprise_foire.filter(status="publier", is_deleted=False)
    f_images = foire.image_foire.filter(status="publier")

    paginator = Paginator(f_images, 3)
    page = request.GET.get('page', 1)

    try:
        f_images = paginator.page(page)
    except PageNotAnInteger:
        f_images = paginator.page(1)
    except EmptyPage:
        f_images = paginator.page(paginator.num_pages)
    except:
        f_images = paginator.page(1)


    context = {
        'foire': foire,
        'f_images':f_images,
        'entreprises':entreprises
    }
    return render(request, 'aguipex/foire_detail.html', context)

def mapping_product(request):
    villes_data = []
    produit_colors = {}

    villes = aguipex_models.Ville.objects.prefetch_related('produits').all()
    for ville in villes:
        produits_list = []
        for produit in ville.produits.all():
            produits_list.append(produit.title)
            produit_colors[produit.title] = produit.couleur  # couleur dynamique

        villes_data.append({
            'name': ville.name,
            'lat': ville.lat,
            'lng': ville.lng,
            'produits': produits_list
        })

    return render(request, 'aguipex/mapping_product.html', {
        'villes_data': json.dumps(villes_data),
        'produit_colors': json.dumps(produit_colors)
    })


def entreprises(request):
    """Vue pour lister toutes les entreprises publiées"""
    # Vérifier si l'utilisateur a déjà soumis ses informations via session
    visitor_submitted = request.session.get('visitor_info_submitted', False)
    
    # Si l'utilisateur n'a pas encore soumis ses informations, le rediriger
    if not visitor_submitted:
        return redirect('collecte-info-visiteur')
    
    # Récupérer les termes de recherche
    search_query = request.GET.get('q', '').strip()
    produit_filter = request.GET.get('produit', '').strip()
    
    # Récupérer les types de produits pour le filtre
    types_produits = aguipex_models.TypeProduit.objects.filter(
        status="publier",
        is_deleted=False
    ).order_by('ordre', 'nom')
    
    # Filtrer les entreprises
    entreprises_list = aguipex_models.Entreprise.objects.filter(
        status="publier", 
        is_deleted=False
    )
    
    # Appliquer la recherche par texte si un terme est fourni
    if search_query:
        entreprises_list = entreprises_list.filter(
            Q(nom__icontains=search_query) |
            Q(type_activite__icontains=search_query) |
            Q(secteur_activite__icontains=search_query) |
            Q(ville__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Appliquer le filtre par type_produit si sélectionné (nouveau système)
    type_produit_filter = request.GET.get('type_produit', '').strip()
    type_produit_filter_obj = None
    if type_produit_filter:
        try:
            type_produit_filter_obj = aguipex_models.TypeProduit.objects.get(
                slug=type_produit_filter,
                status="publier",
                is_deleted=False
            )
            entreprises_list = entreprises_list.filter(
                produits_entreprise__type_produit=type_produit_filter_obj,
                produits_entreprise__status="publier",
                produits_entreprise__is_deleted=False
            ).distinct()
        except aguipex_models.TypeProduit.DoesNotExist:
            type_produit_filter_obj = None
    
    # Appliquer distinct pour éviter les doublons
    entreprises_list = entreprises_list.distinct().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(entreprises_list, 12)  # 12 entreprises par page
    page = request.GET.get('page')
    
    try:
        entreprises = paginator.page(page)
    except PageNotAnInteger:
        entreprises = paginator.page(1)
    except EmptyPage:
        entreprises = paginator.page(paginator.num_pages)
    
    context = {
        'entreprises': entreprises,
        'total_entreprises': entreprises_list.count(),
        'search_query': search_query,
        'type_produit_filter': type_produit_filter,
        'type_produit_filter_obj': type_produit_filter_obj,
        'types_produits': types_produits,
        'mode': 'entreprises',  # Mode navigation par entreprise
    }
    return render(request, 'aguipex/entreprises.html', context)


def entreprise_detail(request, slug):
    """Vue pour afficher les détails d'une entreprise"""
    entreprise = get_object_or_404(
        aguipex_models.Entreprise, 
        slug=slug, 
        status="publier", 
        is_deleted=False
    )
    
    # Récupérer les produits_entreprise de cette entreprise (nouveau système)
    produits = aguipex_models.ProduitEntreprise.objects.filter(
        entreprise=entreprise,
        status="publier",
        is_deleted=False
    ).select_related('type_produit').order_by('-created_at')
    
    context = {
        'entreprise': entreprise,
        'produits': produits,
    }
    return render(request, 'aguipex/entreprise_detail.html', context)


def enregistrer_entreprise(request):
    """Vue pour l'enregistrement d'une nouvelle entreprise avec création de produits"""
    # Récupérer les types de produits disponibles
    types_produits = aguipex_models.TypeProduit.objects.filter(
        status="publier",
        is_deleted=False
    ).order_by('ordre', 'nom')
    
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            nom = request.POST.get('nom')
            description = request.POST.get('description')
            type_activite = request.POST.get('type_activite')
            secteur_activite = request.POST.get('secteur_activite')
            adresse = request.POST.get('adresse')
            ville = request.POST.get('ville')
            telephone = request.POST.get('telephone')
            email = request.POST.get('email')
            site_web = request.POST.get('site_web')
            date_creation = request.POST.get('date_creation')
            nombre_employes = request.POST.get('nombre_employes')
            certifications = request.POST.get('certifications')
            
            # Validation des champs obligatoires
            if not all([nom, type_activite, ville]):
                messages.error(request, 'Veuillez remplir tous les champs obligatoires (nom, type d\'activité, ville).')
                return render(request, 'aguipex/enregistrer_entreprise.html', {'types_produits': types_produits})
            
            # Site web : aucune restriction, on enregistre la saisie telle quelle
            site_web_clean = (site_web or '').strip() or None

            # Création de l'entreprise (par défaut en brouillon)
            entreprise = aguipex_models.Entreprise.objects.create(
                nom=nom,
                description=description,
                type_activite=type_activite,
                secteur_activite=secteur_activite if secteur_activite else None,
                adresse=adresse,
                ville=ville,
                telephone=telephone,
                email=email,
                site_web=site_web_clean,
                date_creation=date_creation if date_creation else None,
                nombre_employes=nombre_employes if nombre_employes else None,
                certifications=certifications if certifications else None,
                status='brouillon'  # Par défaut en brouillon pour validation
            )
            
            # Gestion du logo si fourni
            if 'logo' in request.FILES:
                entreprise.logo = request.FILES['logo']
            
            entreprise.save()
            
            # Création des produits_entreprise
            # Format attendu : produits_entreprise[0][nom], produits_entreprise[0][type_produit_id], produits_entreprise[0][description_courte], produits_entreprise[0][image]
            produits_data = {}
            for key, value in request.POST.items():
                if key.startswith('produits_entreprise['):
                    # Extraire l'index et le champ : produits_entreprise[0][nom] -> index=0, champ=nom
                    import re
                    match = re.match(r'produits_entreprise\[(\d+)\]\[(\w+)\]', key)
                    if match:
                        index = match.group(1)
                        field = match.group(2)
                        if index not in produits_data:
                            produits_data[index] = {}
                        produits_data[index][field] = value
            
            # Traiter les images des produits
            produits_images = {}
            for key, file in request.FILES.items():
                if key.startswith('produits_entreprise['):
                    match = re.match(r'produits_entreprise\[(\d+)\]\[image\]', key)
                    if match:
                        index = match.group(1)
                        produits_images[index] = file
            
            # Créer les produits_entreprise
            for index, produit_data in produits_data.items():
                nom_produit = produit_data.get('nom', '').strip()
                type_produit_id = produit_data.get('type_produit_id', '').strip()
                description_courte = produit_data.get('description_courte', '').strip()
                image_file = produits_images.get(index)
                
                # Validation : nom et image obligatoires
                if nom_produit and image_file:
                    # Récupérer ou créer le type_produit
                    type_produit = None
                    if type_produit_id:
                        try:
                            type_produit = aguipex_models.TypeProduit.objects.get(id=type_produit_id)
                        except aguipex_models.TypeProduit.DoesNotExist:
                            pass
                    
                    # Si type_produit_id est "new" ou vide, créer un nouveau type
                    if not type_produit and produit_data.get('type_produit_new', '').strip():
                        nouveau_type_nom = produit_data.get('type_produit_new', '').strip()
                        type_produit, created = aguipex_models.TypeProduit.objects.get_or_create(
                            nom=nouveau_type_nom,
                            defaults={'status': 'publier'}
                        )
                    
                    # Créer le produit_entreprise
                    if type_produit:
                        produit_entreprise = aguipex_models.ProduitEntreprise(
                            entreprise=entreprise,
                            type_produit=type_produit,
                            nom=nom_produit,
                            description_courte=description_courte[:500] if description_courte else '',
                            image=image_file,
                            status='brouillon'  # Par défaut en brouillon
                        )
                        produit_entreprise.save()  # Sauvegarder explicitement pour s'assurer que l'image est bien enregistrée
            
            messages.success(request, 'Votre entreprise a été enregistrée avec succès ! Elle sera publiée après validation par notre équipe.')
            return redirect('aguipex-entreprises')
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messages.error(request, f'Une erreur est survenue lors de l\'enregistrement : {str(e)}')
            return render(request, 'aguipex/enregistrer_entreprise.html', {'types_produits': types_produits})
    
    # GET Request : Afficher le formulaire
    context = {
        'types_produits': types_produits
    }
    return render(request, 'aguipex/enregistrer_entreprise.html', context)


def produits_par_type(request, slug_type=None):
    """Vue pour afficher les produits filtrés par type - Mode navigation par type_produit"""
    # Vérifier si l'utilisateur a déjà soumis ses informations via session
    visitor_submitted = request.session.get('visitor_info_submitted', False)
    
    if not visitor_submitted:
        return redirect('collecte-info-visiteur')
    
    # Récupérer tous les types de produits
    types_produits = aguipex_models.TypeProduit.objects.filter(
        status="publier",
        is_deleted=False
    ).order_by('ordre', 'nom')
    
    # Priorité au paramètre GET du formulaire, sinon utiliser slug_type de l'URL
    type_produit_slug = request.GET.get('type_produit', '').strip() or slug_type
    
    type_produit = None
    produits_list = aguipex_models.ProduitEntreprise.objects.none()
    
    if type_produit_slug:
        try:
            type_produit = aguipex_models.TypeProduit.objects.get(
                slug=type_produit_slug,
                status="publier",
                is_deleted=False
            )
            # Récupérer les produits de ce type (publiés uniquement)
            produits_list = aguipex_models.ProduitEntreprise.objects.filter(
                type_produit=type_produit,
                status="publier",
                is_deleted=False,
                entreprise__status="publier",
                entreprise__is_deleted=False
            ).select_related('entreprise', 'type_produit').order_by('-created_at')
        except aguipex_models.TypeProduit.DoesNotExist:
            type_produit = None
            produits_list = aguipex_models.ProduitEntreprise.objects.filter(
                status="publier",
                is_deleted=False,
                entreprise__status="publier",
                entreprise__is_deleted=False
            ).select_related('entreprise', 'type_produit').order_by('-created_at')
    else:
        # Afficher tous les produits publiés
        produits_list = aguipex_models.ProduitEntreprise.objects.filter(
            status="publier",
            is_deleted=False,
            entreprise__status="publier",
            entreprise__is_deleted=False
        ).select_related('entreprise', 'type_produit').order_by('-created_at')
    
    # Recherche par texte
    search_query = request.GET.get('q', '').strip()
    if search_query:
        produits_list = produits_list.filter(
            Q(nom__icontains=search_query) |
            Q(description_courte__icontains=search_query) |
            Q(entreprise__nom__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(produits_list, 12)
    page = request.GET.get('page')
    
    try:
        produits = paginator.page(page)
    except PageNotAnInteger:
        produits = paginator.page(1)
    except EmptyPage:
        produits = paginator.page(paginator.num_pages)
    
    context = {
        'types_produits': types_produits,
        'type_produit_selected': type_produit,
        'produits': produits,
        'total_produits': produits_list.count(),
        'search_query': search_query,
        'mode': 'produits',  # Mode navigation par type_produit
    }
    return render(request, 'aguipex/produits_par_type.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def create_type_produit_ajax(request):
    """API pour créer un type_produit à la volée depuis le formulaire"""
    try:
        data = json.loads(request.body)
        nom = data.get('nom', '').strip()
        
        if not nom:
            return JsonResponse({'success': False, 'error': 'Le nom est requis'}, status=400)
        
        # Créer le type_produit
        type_produit, created = aguipex_models.TypeProduit.objects.get_or_create(
            nom=nom,
            defaults={'status': 'publier'}
        )
        
        return JsonResponse({
            'success': True,
            'type_produit': {
                'id': type_produit.id,
                'nom': type_produit.nom,
                'slug': type_produit.slug,
            },
            'created': created
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def collecte_info_visiteur(request):
    """Vue pour afficher la page de collecte d'informations du visiteur"""
    return render(request, 'aguipex/collecte_info_visiteur.html')


def soumettre_info_visiteur(request):
    if request.method == 'POST':
        nom_complet = request.POST.get('nom_complet')
        email = request.POST.get('email')
        pays = request.POST.get('pays')
        ville_residence = request.POST.get('ville_residence')
        telephone = request.POST.get('telephone')
        
        # Récupérer l'adresse IP du visiteur
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Créer l'objet Visiteur
        visiteur = aguipex_models.Visiteur.objects.create(
            nom_complet=nom_complet,
            email=email,
            pays=pays,
            ville_residence=ville_residence,
            telephone=telephone,
            ip_address=ip
        )
        
        # Marquer dans la session que le visiteur a soumis ses informations
        request.session['visitor_info_submitted'] = True
        
        return JsonResponse({
            'success': True,
            'message': 'Informations enregistrées avec succès !'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée'
    })

# Nouvelles vues pour les pages du footer
def conditions_generales(request):
    """Page des conditions générales"""
    return render(request, 'aguipex/conditions_generales.html')

def carrieres(request):
    """Page des carrières"""
    return render(request, 'aguipex/carrieres.html')

def politique_confidentialite(request):
    """Page de la politique de confidentialité"""
    return render(request, 'aguipex/politique_confidentialite.html')

# Vues pour la Newsletter
def s_inscrire_newsletter(request):
    """Vue pour s'inscrire à la newsletter"""
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            nom = request.POST.get('nom', '')
            prenom = request.POST.get('prenom', '')
            pays = request.POST.get('pays', '')
            ville = request.POST.get('ville', '')
            secteur_activite = request.POST.get('secteur_activite', '')
            
            # Récupérer l'adresse IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # Vérifier si l'email existe déjà
            if aguipex_models.Newsletter.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Cette adresse e-mail est déjà inscrite à notre newsletter.'
                })
            
            # Créer l'abonné
            abonne = aguipex_models.Newsletter.objects.create(
                email=email,
                nom=nom,
                prenom=prenom,
                pays=pays,
                ville=ville,
                secteur_activite=secteur_activite,
                ip_inscription=ip,
                source_inscription='site_web'
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Inscription réussie ! Vous recevrez désormais nos newsletters.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors de l\'inscription : {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée'
    })


def se_desabonner_newsletter(request, token):
    """Vue pour se désabonner de la newsletter"""
    try:
        # En production, vous devriez utiliser un token sécurisé
        # Pour l'instant, on utilise l'email encodé en base64
        import base64
        email = base64.b64decode(token).decode('utf-8')
        
        abonne = aguipex_models.Newsletter.objects.get(email=email, est_actif=True)
        abonne.desabonner()
        
        return render(request, 'aguipex/desabonnement_newsletter.html', {
            'email': email,
            'success': True
        })
        
    except aguipex_models.Newsletter.DoesNotExist:
        return render(request, 'aguipex/desabonnement_newsletter.html', {
            'success': False,
            'message': 'Adresse e-mail non trouvée ou déjà désabonnée.'
        })
    except Exception as e:
        return render(request, 'aguipex/desabonnement_newsletter.html', {
            'success': False,
            'message': f'Erreur lors du désabonnement : {str(e)}'
        })


def envoyer_newsletter(request):
    """Vue pour envoyer une newsletter (réservée aux administrateurs)"""
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Accès non autorisé'
        })
    
    if request.method == 'POST':
        try:
            template_id = request.POST.get('template_id')
            sujet = request.POST.get('sujet')
            
            # Récupérer le template
            template = aguipex_models.NewsletterTemplate.objects.get(id=template_id, est_actif=True)
            
            # Récupérer tous les abonnés actifs
            abonnes = aguipex_models.Newsletter.objects.filter(est_actif=True)
            
            # Créer l'enregistrement d'envoi
            envoi = aguipex_models.NewsletterEnvoi.objects.create(
                template=template,
                sujet=sujet,
                nombre_destinataires=abonnes.count()
            )
            
            # En production, vous devriez utiliser Celery ou un autre système de tâches asynchrones
            # Pour l'instant, on simule l'envoi
            nombre_envoyes = 0
            nombre_erreurs = 0
            details_erreur = []
            
            for abonne in abonnes:
                try:
                    # Ici, vous devriez intégrer votre service d'envoi d'emails
                    # Par exemple, avec Django Email Backend, SendGrid, Mailgun, etc.
                    
                    # Simulation d'envoi réussi
                    nombre_envoyes += 1
                    
                except Exception as e:
                    nombre_erreurs += 1
                    details_erreur.append(f"Erreur pour {abonne.email}: {str(e)}")
            
            # Mettre à jour les statistiques
            envoi.nombre_envoyes = nombre_envoyes
            envoi.nombre_erreurs = nombre_erreurs
            envoi.statut = 'termine'
            if details_erreur:
                envoi.details_erreur = '\n'.join(details_erreur)
            envoi.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Newsletter envoyée avec succès à {nombre_envoyes} destinataires.',
                'statistiques': {
                    'envoyes': nombre_envoyes,
                    'erreurs': nombre_erreurs
                }
            })
            
        except aguipex_models.NewsletterTemplate.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Template de newsletter non trouvé.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors de l\'envoi : {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée'
    })


def interprofessions(request):
    """Liste des interprofessions (affichage public)."""
    interprofessions_list = aguipex_models.Interprofession.objects.filter(
        status="publier", is_deleted=False
    ).order_by('nom')
    context = {'interprofessions': interprofessions_list}
    return render(request, 'aguipex/interprofessions.html', context)


def interprofession_detail(request, slug):
    """Détail d'une interprofession avec la liste de ses personnels."""
    interprofession = get_object_or_404(
        aguipex_models.Interprofession,
        slug=slug,
        status="publier",
        is_deleted=False
    )
    personnels = interprofession.personnels.filter(status="publier", is_deleted=False).order_by('nom', 'prenom')
    context = {
        'interprofession': interprofession,
        'personnels': personnels,
    }
    return render(request, 'aguipex/interprofession_detail.html', context)


def projets(request):
    """Liste des projets (en cours et terminés) affichée sur le site."""
    etapes_ordre = aguipex_models.EtapeProjet.objects.filter(is_deleted=False).order_by('ordre', 'date_etape', 'created_at')
    projets_list = aguipex_models.Projet.objects.filter(
        status__in=('en_cours', 'termine'),
        is_deleted=False
    ).prefetch_related(
        Prefetch('etapes', queryset=etapes_ordre, to_attr='etapes_ordered')
    ).order_by('-start_date', '-created_at')
    for p in projets_list:
        etapes = getattr(p, 'etapes_ordered', [])
        p.last_etape_pourcentage = etapes[-1].pourcentage if etapes and etapes[-1].pourcentage is not None else None
    context = {'projets': projets_list}
    return render(request, 'aguipex/projets.html', context)


def projet_detail(request, slug):
    """Détail d'un projet avec évolution et étapes."""
    projet = get_object_or_404(
        aguipex_models.Projet,
        slug=slug,
        status__in=('en_cours', 'termine'),
        is_deleted=False
    )
    etapes = projet.etapes.filter(is_deleted=False).order_by('ordre', 'date_etape', 'created_at')
    context = {
        'projet': projet,
        'etapes': etapes,
    }
    return render(request, 'aguipex/projet_detail.html', context)


def statistiques(request):
    """Statistiques par année, mois et catégorie avec filtrage."""
    qs = aguipex_models.Statistique.objects.filter(is_deleted=False).select_related('categorie')
    annees_dispo = list(qs.values_list('annee', flat=True).distinct().order_by('-annee'))
    categories = aguipex_models.CategorieStatistique.objects.filter(is_deleted=False).order_by('ordre', 'nom')
    annee = request.GET.get('annee', '')
    mois = request.GET.get('mois', '')
    categorie_slug = request.GET.get('categorie', '')
    if annee:
        try:
            annee_int = int(annee)
            qs = qs.filter(annee=annee_int)
        except ValueError:
            pass
    if mois:
        try:
            mois_int = int(mois)
            qs = qs.filter(mois=mois_int)
        except ValueError:
            pass
    if categorie_slug:
        qs = qs.filter(categorie__slug=categorie_slug)
    statistiques_list = qs.order_by('-annee', 'mois', 'ordre', 'titre')
    context = {
        'statistiques': statistiques_list,
        'annees_dispo': annees_dispo,
        'categories': categories,
        'annee_choisie': annee,
        'mois_choisi': mois,
        'categorie_choisie': categorie_slug,
        'mois_choices': aguipex_models.Statistique.MOIS_CHOICES,
    }
    return render(request, 'aguipex/statistiques.html', context)


# --- Manifestations commerciales (Front Office) ---

def manifestations_list(request):
    """Liste des manifestations commerciales publiées (Front Office)."""
    manifestations = aguipex_models.ManifestationCommerciale.objects.filter(
        statut_publication='publier',
        is_deleted=False
    ).prefetch_related('etapes').order_by('-date_debut', '-created_at')
    context = {'manifestations': manifestations}
    return render(request, 'aguipex/manifestations_list.html', context)


def manifestation_detail(request, slug):
    """
    Détail d'une manifestation avec wizard des étapes (Front Office).
    Règle d'affichage : seules les étapes dont l'ordre <= statut global sont affichées.
    - BIENTOT_PREVU → étape 1 uniquement
    - A_POSTULER → étapes 1 et 2 (bouton Postuler affiché)
    - SELECTION_TERMINEE → étapes 1, 2 et 3
    - MANIFESTATION_TERMINEE → toutes les étapes
    """
    manifestation = get_object_or_404(
        aguipex_models.ManifestationCommerciale,
        slug=slug,
        statut_publication='publier',
        is_deleted=False
    )
    # Étapes visibles selon statut global
    max_ordre = MAX_ORDRE_ETAPE_PAR_STATUT.get(manifestation.statut_global, 1)
    etapes = manifestation.etapes.filter(
        is_deleted=False,
        ordre__lte=max_ordre
    ).order_by('ordre')
    
    # Pour chaque étape, récupérer toutes les candidatures qui sont passées par cette étape
    # (via l'historique), même si elles sont maintenant à une autre étape
    candidatures_par_etape = {}
    for e in etapes:
        candidatures_passees = e.get_candidatures_passees_par_etape().select_related('entreprise').order_by('-date_candidature')
        candidatures_par_etape[e.id] = list(candidatures_passees)
    
    # Annoter les étapes avec le nombre d'entreprises
    etapes_avec_candidatures = []
    for e in etapes:
        nb_candidatures = len(candidatures_par_etape.get(e.id, []))
        etapes_avec_candidatures.append({
            'etape': e,
            'candidatures': candidatures_par_etape.get(e.id, []),
            'nb_entreprises_selectionnees': nb_candidatures
        })
    peut_postuler = manifestation.statut_global == 'a_postuler'
    context = {
        'manifestation': manifestation,
        'etapes': etapes,
        'etapes_avec_candidatures': etapes_avec_candidatures,
        'peut_postuler': peut_postuler,
    }
    return render(request, 'aguipex/manifestation_detail.html', context)


@require_http_methods(['GET', 'POST'])
def manifestation_postuler(request, slug):
    """
    Formulaire de candidature (Front Office). Accessible uniquement si statut global = À postuler.
    À la création : candidature enregistrée à l'étape « À postuler » (ordre 2), statut métier A_POSTULER, statut back office BROUILLON.
    Premier enregistrement d'historique créé pour traçabilité.
    """
    manifestation = get_object_or_404(
        aguipex_models.ManifestationCommerciale,
        slug=slug,
        statut_publication='publier',
        is_deleted=False
    )
    if manifestation.statut_global != 'a_postuler':
        messages.warning(request, "Les candidatures ne sont pas ouvertes pour cette manifestation.")
        return redirect('aguipex-manifestation-detail', slug=slug)
    form = CandidatureManifestationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        candidature = form.save(commit=False)
        candidature.manifestation = manifestation
        candidature.statut_metier = 'refus'
        candidature.statut_back_office = 'brouillon'
        candidature.entreprise = None
        # Étape fixe à la création : « À postuler » (ordre 2)
        etape_postuler = manifestation.etapes.filter(is_deleted=False, ordre=2).first()
        if not etape_postuler:
            messages.error(request, "Configuration de la manifestation incomplète. Merci de réessayer plus tard.")
            return redirect('aguipex-manifestation-detail', slug=slug)
        candidature.etape_actuelle = etape_postuler
        if aguipex_models.CandidatureManifestation.objects.filter(
            manifestation=manifestation,
            email_contact=candidature.email_contact,
            is_deleted=False
        ).exists():
            messages.warning(request, "Une candidature avec cet email existe déjà pour cette manifestation.")
        else:
            candidature.save()
            aguipex_models.CandidatureEtapeHistorique.objects.create(
                candidature=candidature,
                etape=etape_postuler,
            )
            messages.success(request, "Votre candidature a bien été enregistrée. Vous serez recontacté par l'équipe AGUIPEX.")
            return redirect(reverse('aguipex-manifestation-detail', kwargs={'slug': slug}) + '?postule=1')
    context = {'manifestation': manifestation, 'form': form}
    return render(request, 'aguipex/manifestation_postuler.html', context)


def manifestation_etape_entreprises(request, slug, etape_id):
    """
    Liste des entreprises publiées qui sont passées par une étape donnée (Front Office).
    Utilise l'historique pour afficher toutes les candidatures qui sont passées par cette étape,
    même si elles sont maintenant à une autre étape.
    L'étape doit être visible selon le statut global (ordre <= max_ordre).
    """
    manifestation = get_object_or_404(
        aguipex_models.ManifestationCommerciale,
        slug=slug,
        statut_publication='publier',
        is_deleted=False
    )
    etape = get_object_or_404(
        aguipex_models.EtapeManifestation,
        pk=etape_id,
        manifestation=manifestation,
        is_deleted=False
    )
    max_ordre = MAX_ORDRE_ETAPE_PAR_STATUT.get(manifestation.statut_global, 1)
    if etape.ordre > max_ordre:
        messages.warning(request, "Cette étape n'est pas encore visible pour cette manifestation.")
        return redirect('aguipex-manifestation-detail', slug=slug)
    
    # Récupérer toutes les candidatures qui sont passées par cette étape (via l'historique)
    # Filtrées selon le statut back office 'publié' et statut métier 'accepte' ou 'refus'
    candidatures = etape.get_candidatures_passees_par_etape().select_related('entreprise').order_by('-date_candidature')
    
    context = {
        'manifestation': manifestation,
        'etape': etape,
        'candidatures': candidatures,
    }
    return render(request, 'aguipex/manifestation_etape_entreprises.html', context)


# ========== CHATBOT AGUIPEX ==========
from core.chatbot_services import (
    extract_keywords,
    detect_intent,
    search_site_content,
    get_cached_response,
    set_cached_response,
    build_response,
    generate_session_id,
)


def chatbot_api(request):
    """
    API du chatbot: POST { "session_id": "...", "message": "..." }
    Retourne { "reply", "understood_as", "keywords": [{"word", "weight"}], "session_id" }.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405, json_dumps_params={'ensure_ascii': False})
    try:
        data = json.loads(request.body)
        message = (data.get('message') or '').strip()
        session_id = (data.get('session_id') or '').strip()
        if not message:
            return JsonResponse({'error': 'Message vide'}, status=400, json_dumps_params={'ensure_ascii': False})
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Corps JSON invalide'}, status=400, json_dumps_params={'ensure_ascii': False})

    from core.models import ChatSession, ChatMessage, ExtractedKeyword
    import logging
    import html
    logger = logging.getLogger(__name__)

    session = None
    keywords = []
    try:
        if not session_id:
            session_id = generate_session_id()
            session = ChatSession.objects.create(session_id=session_id)
        else:
            session = ChatSession.objects.filter(session_id=session_id).first()
            if not session:
                session = ChatSession.objects.create(session_id=session_id)

        # Enregistrer le message utilisateur
        ChatMessage.objects.create(session=session, role=ChatMessage.ROLE_USER, content=message)

        # NLP: extraction mots-clés et intention
        keywords = extract_keywords(message)
        intent = detect_intent(message, keywords)

        # Cache (désactivé pour les procédures d'exportation pour toujours renvoyer la réponse dédiée)
        q_normalized = message.lower().strip()
        use_cache = intent not in (
            'procedure_export', 'contact', 'equipe', 'aguipex', 'foires', 'manifestations',
            'projets', 'statistiques', 'entreprises', 'produits', 'interprofessions', 'actualites', 'donnees_strategiques', 'faq',
        )
        cached = get_cached_response(q_normalized) if use_cache else None
        if cached:
            reply = cached
            understood_as = "Voici ce que j'ai compris : " + ", ".join([html.unescape(str(k[0])) for k in keywords[:8]]) if keywords else ""
        else:
            search_results = search_site_content(keywords, intent)
            reply, understood_as = build_response(message, intent, search_results, keywords)
            if use_cache:
                set_cached_response(q_normalized, reply)

        # Enregistrer les mots-clés pour le Word Cloud (navbar)
        msg_bot = ChatMessage.objects.create(
            session=session,
            role=ChatMessage.ROLE_BOT,
            content=reply,
            understood_as=understood_as or None,
        )
        for word, weight in keywords[:20]:
            ExtractedKeyword.objects.create(
                word=word,
                weight=weight,
                session=session,
                message=msg_bot,
            )

        return JsonResponse({
            'reply': reply,
            'understood_as': understood_as,
            'keywords': [{'word': w, 'weight': p} for w, p in keywords[:20]],
            'session_id': session_id,
        }, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        logger.exception("Chatbot API error: %s", e)
        fallback_reply = (
            "Désolé, une difficulté technique est survenue. Vous pouvez réessayer ou consulter "
            "directement les pages **À propos**, **Contact** et **Ressources** du site."
        )
        understood_as = "Voici ce que j'ai compris : " + ", ".join([html.unescape(str(k[0])) for k in keywords[:8]]) if keywords else "Une difficulté est survenue."
        if session:
            try:
                msg_bot = ChatMessage.objects.create(
                    session=session,
                    role=ChatMessage.ROLE_BOT,
                    content=fallback_reply,
                    understood_as=understood_as or None,
                )
                for word, weight in keywords[:20]:
                    ExtractedKeyword.objects.create(word=word, weight=weight, session=session, message=msg_bot)
            except Exception:
                pass
        return JsonResponse({
            'reply': fallback_reply,
            'understood_as': understood_as,
            'keywords': [{'word': w, 'weight': p} for w, p in keywords[:20]],
            'session_id': session_id,
        }, json_dumps_params={'ensure_ascii': False})


def word_cloud_data(request):
    """
    API Word Cloud: GET retourne les mots-clés agrégés (tous ou par session).
    Pour la page Word Cloud (navbar).
    """
    from core.models import ExtractedKeyword
    from django.db.models import Sum

    session_id = request.GET.get('session_id', '').strip()
    limit = min(int(request.GET.get('limit', 100)), 200)

    if session_id:
        qs = ExtractedKeyword.objects.filter(session__session_id=session_id)
    else:
        qs = ExtractedKeyword.objects.all()
    agg = qs.values('word').annotate(total_weight=Sum('weight')).order_by('-total_weight')[:limit]
    data = [{'word': x['word'], 'weight': x['total_weight']} for x in agg]
    return JsonResponse({'keywords': data})


def word_cloud_page(request):
    """Page Word Cloud (accès depuis la navbar, pas dans le chatbot)."""
    programmes = aguipex_models.Programme.objects.filter(status="publier", is_deleted=False).order_by("-created_at")
    context = {
        'programmes': programmes,
    }
    return render(request, 'aguipex/word_cloud.html', context)