from django.urls import path
from core import views

urlpatterns = [
    path('', views.index, name="aguipex-index"),
    path('a-propos/', views.about, name="aguipex-about"),
    path('equipe/', views.equipe, name="aguipex-equipe"),
    path('actualite/', views.actualite, name="aguipex-actualite"),
    path('contactez-nous/', views.contact, name="aguipex-contact"),
    path('detail-programme/<slug:slug>/', views.detail_programme, name="aguipex-detailProgramme"),
    path('donnees-strategique/', views.donnees_strategique, name="aguipex-donneeStrategique"),
    path('faq/', views.faq, name="aguipex-faq"),
    path('espace-media/', views.espace_media, name="aguipex-espaceMedia"),
    path('offre-de-service/', views.offres_service, name="aguipex-offreService"),
    path('exportations/', views.potentiels_exportation, name="aguipex-exportations"),
    path('get_exportation_details/', views.get_exportation_details, name="get-exportation-details"),
    path('get-voies-by-produit/', views.get_voies_by_produit, name='get_voies_by_produit'),
    path('get-procedure-details/', views.get_procedure_details, name='get_procedure_details'),
    path('catographie-produit/', views.mapping_product, name='mapping-produit'),

    # URLs pour les entreprises
    path('entreprises/', views.entreprises, name='aguipex-entreprises'),
    path('entreprises/<slug:slug>/', views.entreprise_detail, name='aguipex-entreprise-detail'),
    path('enregistrer-entreprise/', views.enregistrer_entreprise, name='aguipex-enregistrer-entreprise'),
    
    # URLs pour les produits par type
    path('produits/', views.produits_par_type, name='aguipex-produits'),
    path('produits/type/<slug:slug_type>/', views.produits_par_type, name='aguipex-produits-par-type'),
    
    # API pour créer type_produit à la volée
    path('api/create-type-produit/', views.create_type_produit_ajax, name='aguipex-create-type-produit'),

    # Interprofessions
    path('interprofessions/', views.interprofessions, name='aguipex-interprofessions'),
    path('interprofessions/<slug:slug>/', views.interprofession_detail, name='aguipex-interprofession-detail'),

    # Projets
    path('projets/', views.projets, name='aguipex-projets'),
    path('projets/<slug:slug>/', views.projet_detail, name='aguipex-projet-detail'),

    # Statistiques
    path('statistiques/', views.statistiques, name='aguipex-statistiques'),

    # Manifestations commerciales (Front Office)
    path('manifestations-commerciales/', views.manifestations_list, name='aguipex-manifestations'),
    path('manifestations-commerciales/<slug:slug>/', views.manifestation_detail, name='aguipex-manifestation-detail'),
    path('manifestations-commerciales/<slug:slug>/postuler/', views.manifestation_postuler, name='aguipex-manifestation-postuler'),
    path('manifestations-commerciales/<slug:slug>/etape/<int:etape_id>/entreprises/', views.manifestation_etape_entreprises, name='aguipex-manifestation-etape-entreprises'),

    path('foires/', views.foires, name="aguipex-foire"),
    path('foires/<slug:slug>/', views.foire_detail, name='aguipex-foire_detail'),
    path('actualites/<slug:slug>/', views.detail_actualite, name='aguipex-detail_actualite'),
    path('donnees/<slug:slug>/', views.detail_donnee_strategique, name='aguipex-detail_donnee'),
    path('galeries/<slug:slug>/', views.detail_espace_media, name='aguipex-detail_espace'),
    path('soumettre-info-visiteur/', views.soumettre_info_visiteur, name='soumettre-info-visiteur'),
    path('collecte-info-visiteur/', views.collecte_info_visiteur, name='collecte-info-visiteur'),

    # Nouvelles URLs pour les pages du footer
    path('conditions-generales/', views.conditions_generales, name='aguipex-conditions-generales'),
    path('carrieres/', views.carrieres, name='aguipex-carrieres'),
    path('politique-confidentialite/', views.politique_confidentialite, name='aguipex-politique-confidentialite'),

    # URLs pour la Newsletter
    path('newsletter/inscription/', views.s_inscrire_newsletter, name='aguipex-inscription-newsletter'),
    path('newsletter/desabonnement/<str:token>/', views.se_desabonner_newsletter, name='aguipex-desabonnement-newsletter'),
    path('newsletter/envoyer/', views.envoyer_newsletter, name='aguipex-envoyer-newsletter'),

    # Chatbot AGUIPEX
    path('api/chatbot/', views.chatbot_api, name='aguipex-chatbot-api'),
    path('api/chatbot/word-cloud/', views.word_cloud_data, name='aguipex-word-cloud-api'),
    path('word-cloud/', views.word_cloud_page, name='aguipex-word-cloud'),
]
