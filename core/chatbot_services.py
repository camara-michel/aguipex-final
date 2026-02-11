# -*- coding: utf-8 -*-
"""
Chatbot AGUIPEX - Intelligence hybride.

Architecture:
- Extraction de mots-clés (NLP léger, stopwords FR)
- Détection d'intention (règles + mots-clés)
- Recherche sémantique sur le contenu du site (Statistiques, Projets, Entreprises,
  Manifestations, Foires, Produits, Actualités, Données stratégiques, etc.)
- Cache Django pour réponses fréquentes
- Réponses progressives, ton professionnel et pédagogique.

Règle d'or: ne jamais inventer de services; priorité aux données du site.
"""
import re
import uuid
import html
from typing import List, Tuple, Dict, Optional
from django.db.models import Q
from django.core.cache import cache
from django.conf import settings

def _strip_html(html_content: str) -> str:
    """Retire les balises HTML, décode les entités HTML et normalise les espaces pour un texte lisible."""
    if not html_content:
        return ""
    # Convertir en string si nécessaire
    text = str(html_content)
    # Retirer les balises HTML
    text = re.sub(r'<[^>]+>', ' ', text)
    # Décoder les entités HTML (comme &eacute;, &agrave;, etc.)
    try:
        text = html.unescape(text)
    except Exception:
        pass
    # Normaliser les espaces
    text = re.sub(r'\s+', ' ', text).strip()
    # Limiter la longueur
    return text[:2000]  # limite raisonnable pour le chat


def get_procedure_export_full_answer(question: str) -> str:
    """
    Récupère le contenu réel des procédures d'exportation (ProcédureGlobale + éventuellement
    procédure par produit si la question mentionne un produit) et retourne une réponse complète.
    """
    from core import models as aguipex_models

    parts = []

    # 1. Procédures globales (étapes générales)
    procedures_globales = aguipex_models.ProcedureGlobale.objects.filter(
        status='publier', is_deleted=False
    ).order_by('created_at')
    if procedures_globales.exists():
        parts.append("**Procédure d'exportation — étapes générales :**\n")
        for i, proc in enumerate(procedures_globales, 1):
            titre = (proc.titre or '').strip()
            desc = _strip_html(proc.description or '')
            if titre or desc:
                parts.append(f"{i}. **{titre}** : {desc}")
        parts.append("")

    # 2. Détail par produit si la question mentionne un produit (ex. café)
    q_lower = question.lower()
    product_keywords = ['cafe', 'café', 'cacao', 'fonio', 'mangue', 'ananas', 'banane', 'riz', 'minerai', 'bauxite']
    product_match = next((kw for kw in product_keywords if kw in q_lower), None)
    if product_match:
        proc_product = aguipex_models.ProcedureProduct.objects.filter(
            status='publier', is_deleted=False,
            product__title__icontains=product_match
        ).select_related('product').first()
        if proc_product:
            parts.append(f"**Processus pour l'export de « {proc_product.product.title } » :**\n")
            if proc_product.formalisation:
                parts.append("• Formalisation : " + _strip_html(proc_product.formalisation))
            if proc_product.dde:
                parts.append("• DDE : " + _strip_html(proc_product.dde))
            if proc_product.autorisation:
                parts.append("• Autorisation : " + _strip_html(proc_product.autorisation))
            if proc_product.formalite_douane:
                parts.append("• Formalités douane : " + _strip_html(proc_product.formalite_douane))
            if proc_product.redevance:
                parts.append("• Redevance : " + _strip_html(proc_product.redevance))
            parts.append("\nPour les détails complets (certificats, voies d'exportation), consultez la page **Exportations** sur notre site.")

    if not parts:
        return (
            "Les procédures d'exportation sont en cours de mise à jour sur notre site. "
            "Veuillez consulter la page **Exportations** (menu principal) ou nous contacter pour obtenir les informations à jour."
        )

    return "\n\n".join(parts).strip()


def get_contact_siege_full_answer() -> str:
    """
    Réponse exacte pour siège, adresse et coordonnées d'AGUIPEX (données publiées sur le site).
    """
    return (
        "**Siège d'AGUIPEX**\n\n"
        "• **Adresse** : Immeuble Horizon, 3ème étage, 5ème Avenue Sandervalia, Commune de Kaloum.\n\n"
        "• **Téléphone** : (+224) 611 75 65 52\n\n"
        "• **Email** : contact@aguipex.gov.gn\n\n"
        "• **Horaires** : Du lundi au vendredi, 8h – 17h.\n\n"
        "Pour nous écrire ou voir le plan, consultez la page **Contactez-nous** dans le menu."
    )


def get_foires_full_answer() -> str:
    """
    Réponse sur les foires à partir de la base (Foires publiées).
    """
    from core import models as aguipex_models

    foires = aguipex_models.Foires.objects.filter(
        status='publier', is_deleted=False
    ).order_by('-date_debut', '-created_at')[:15]
    if not foires:
        return get_no_answer_contact_message()
    parts = ["**Nos foires**\n"]
    for f in foires:
        titre = (getattr(f, 'titre', '') or '').strip()
        lieu = (getattr(f, 'lieu', '') or '').strip()
        pays = (getattr(f, 'pays', '') or '').strip()
        desc = _strip_html(getattr(f, 'description', '') or '')[:200]
        date_d = getattr(f, 'date_debut', None)
        date_f = getattr(f, 'date_fin', None)
        line = f"• **{titre}**"
        if lieu or pays:
            line += f" — {lieu or ''}{', ' if lieu and pays else ''}{pays or ''}"
        if date_d:
            line += f" ({date_d})"
        parts.append(line)
        if desc:
            parts.append(f"  {desc}{'...' if len(getattr(f, 'description', '') or '') > 200 else ''}")
    parts.append("\nDétails : menu **Ressources** > Foires.")
    return "\n\n".join(parts)


def get_manifestations_full_answer() -> str:
    """
    Réponse sur les manifestations commerciales à partir de la base.
    """
    from core import models as aguipex_models

    manifs = aguipex_models.ManifestationCommerciale.objects.filter(
        is_deleted=False, statut_publication='publier'
    ).order_by('-date_debut', '-created_at')[:15]
    if not manifs:
        return get_no_answer_contact_message()
    parts = ["**Manifestations commerciales**\n"]
    for m in manifs:
        titre = (getattr(m, 'titre', '') or '').strip()
        lieu = (getattr(m, 'lieu', '') or '').strip()
        pays = (getattr(m, 'pays', '') or '').strip()
        desc = _strip_html(getattr(m, 'description', '') or '')[:200]
        date_d = getattr(m, 'date_debut', None)
        line = f"• **{titre}**"
        if lieu or pays:
            line += f" — {lieu or ''}{', ' if lieu and pays else ''}{pays or ''}"
        if date_d:
            line += f" ({date_d})"
        parts.append(line)
        if desc:
            parts.append(f"  {desc}{'...' if len(getattr(m, 'description', '') or '') > 200 else ''}")
    parts.append("\nDétails et candidature : menu **Ressources** > Manifestations commerciales.")
    return "\n\n".join(parts)


def get_projets_full_answer() -> str:
    """Réponse sur les projets à partir de la base."""
    from core import models as aguipex_models

    projets = aguipex_models.Projet.objects.filter(
        is_deleted=False
    ).exclude(status='brouillon').order_by('-start_date', '-created_at')[:15]
    if not projets:
        return get_no_answer_contact_message()
    parts = ["**Projets AGUIPEX**\n"]
    for p in projets:
        titre = (getattr(p, 'title', '') or '').strip()
        desc = _strip_html(getattr(p, 'description', '') or '')[:180]
        statut = getattr(p, 'status', '') or ''
        line = f"• **{titre}**"
        if statut and statut != 'brouillon':
            line += f" ({statut.replace('_', ' ')})"
        parts.append(line)
        if desc:
            parts.append(f"  {desc}{'...' if len(getattr(p, 'description', '') or '') > 180 else ''}")
    parts.append("\nDétails : menu **Ressources** > Projets.")
    return "\n\n".join(parts)


def get_statistiques_full_answer() -> str:
    """Réponse sur les statistiques à partir de la base."""
    from core import models as aguipex_models

    stats = aguipex_models.Statistique.objects.filter(
        is_deleted=False
    ).select_related('categorie').order_by('-annee', 'ordre', 'titre')[:20]
    if not stats:
        return get_no_answer_contact_message()
    parts = ["**Statistiques**\n"]
    for s in stats:
        titre = (getattr(s, 'titre', '') or '').strip()
        val = getattr(s, 'valeur', None)
        unite = (getattr(s, 'unite', '') or '').strip()
        annee = getattr(s, 'annee', None)
        line = f"• **{titre}**"
        if val is not None:
            line += f" : {val}"
            if unite:
                line += f" {unite}"
        if annee:
            line += f" ({annee})"
        parts.append(line)
    parts.append("\nDétails : menu **Ressources** > Statistiques.")
    return "\n\n".join(parts)


def get_entreprises_full_answer() -> str:
    """Réponse sur les entreprises à partir de la base."""
    from core import models as aguipex_models

    entreprises = aguipex_models.Entreprise.objects.filter(
        status='publier', is_deleted=False
    ).order_by('nom')[:15]
    if not entreprises:
        return get_no_answer_contact_message()
    parts = ["**Entreprises**\n"]
    for e in entreprises:
        nom = (getattr(e, 'nom', '') or '').strip()
        type_act = (getattr(e, 'type_activite', '') or '').strip()
        ville = (getattr(e, 'ville', '') or '').strip()
        desc = _strip_html(getattr(e, 'description', '') or '')[:150]
        line = f"• **{nom}**"
        if type_act:
            line += f" — {type_act}"
        if ville:
            line += f" ({ville})"
        parts.append(line)
        if desc:
            parts.append(f"  {desc}{'...' if len(getattr(e, 'description', '') or '') > 150 else ''}")
    parts.append("\nDétails : menu **Ressources** > Entreprises.")
    return "\n\n".join(parts)


def get_produits_full_answer() -> str:
    """Réponse sur les produits à partir de la base."""
    from core import models as aguipex_models

    produits = aguipex_models.Produit.objects.filter(
        status='publier', is_deleted=False, pour_site=True
    ).order_by('title')[:20]
    if not produits:
        return get_no_answer_contact_message()
    parts = ["**Produits**\n"]
    for p in produits:
        titre = (getattr(p, 'title', '') or '').strip()
        desc = _strip_html(getattr(p, 'description', '') or '')[:150]
        parts.append(f"• **{titre}**")
        if desc:
            parts.append(f"  {desc}{'...' if len(getattr(p, 'description', '') or '') > 150 else ''}")
    parts.append("\nCartographie et détails : page **Exportations** et menu **Ressources**.")
    return "\n\n".join(parts)


def get_interprofessions_full_answer() -> str:
    """Réponse sur les interprofessions à partir de la base."""
    from core import models as aguipex_models

    interpros = aguipex_models.Interprofession.objects.filter(
        status='publier', is_deleted=False
    ).order_by('nom')[:15]
    if not interpros:
        return get_no_answer_contact_message()
    parts = ["**Interprofessions**\n"]
    for i in interpros:
        nom = (getattr(i, 'nom', '') or '').strip()
        code = (getattr(i, 'code', '') or '').strip()
        parts.append(f"• **{nom}** ({code})")
    parts.append("\nDétails : menu **Ressources** > Interprofessions.")
    return "\n\n".join(parts)


def get_actualites_full_answer() -> str:
    """Réponse sur les actualités à partir de la base."""
    from core import models as aguipex_models

    actualites = aguipex_models.Actualite.objects.filter(
        status='publier', is_deleted=False
    ).order_by('-date_actualite', '-created_at')[:10]
    if not actualites:
        return get_no_answer_contact_message()
    parts = ["**Actualités**\n"]
    for a in actualites:
        titre = (getattr(a, 'grand_titre', '') or '').strip()
        date_a = getattr(a, 'date_actualite', None)
        detail = _strip_html(getattr(a, 'detail', '') or '')[:180]
        line = f"• **{titre}**"
        if date_a:
            line += f" ({date_a})"
        parts.append(line)
        if detail:
            parts.append(f"  {detail}{'...' if len(getattr(a, 'detail', '') or '') > 180 else ''}")
    parts.append("\nDétails : menu **Ressources** > Actualités.")
    return "\n\n".join(parts)


def get_donnees_strategiques_full_answer() -> str:
    """Réponse sur les données stratégiques à partir de la base."""
    from core import models as aguipex_models

    donnees = aguipex_models.DonneeStrategique.objects.filter(
        status='publier', is_deleted=False
    ).order_by('-created_at')[:12]
    if not donnees:
        return get_no_answer_contact_message()
    parts = ["**Données stratégiques**\n"]
    for d in donnees:
        titre = (getattr(d, 'titre', '') or '').strip()
        detail = _strip_html(getattr(d, 'detail', '') or '')[:200]
        parts.append(f"• **{titre}**")
        if detail:
            parts.append(f"  {detail}{'...' if len(getattr(d, 'detail', '') or '') > 200 else ''}")
    parts.append("\nDétails : menu **Ressources** > Données stratégiques.")
    return "\n\n".join(parts)


def get_faq_full_answer() -> str:
    """Réponse FAQ à partir de la base (questions / réponses publiées)."""
    from core import models as aguipex_models

    faqs = aguipex_models.FAQ.objects.filter(
        status='publier'
    ).order_by('id')[:15]
    if not faqs:
        return get_no_answer_contact_message()
    parts = ["**Questions fréquentes**\n"]
    for f in faqs:
        q = (getattr(f, 'question', '') or '').strip()
        r = _strip_html(getattr(f, 'response', '') or '')[:250]
        parts.append(f"• **{q}**")
        parts.append(f"  {r}{'...' if len(getattr(f, 'response', '') or '') > 250 else ''}")
    parts.append("\nDétails : menu **Ressources** > FAQ.")
    return "\n\n".join(parts)


def get_no_answer_contact_message() -> str:
    """
    Message affiché quand le chatbot n'a pas été entraîné pour la question :
    inviter à contacter le service de communication avec les coordonnées.
    """
    return (
        "Je n'ai pas encore été entraîné pour cette question.\n\n"
        "Veuillez contacter le **service de communication** de l'Agence Guinéenne de Promotion des Exportations (AGUIPEX) pour plus d'informations :\n\n"
        "• **Numéro de téléphone** : (+224) 611 75 65 52\n\n"
        "• **Adresse email** : contact@aguipex.gov.gn\n\n"
        "• **Emplacement du bureau** : Immeuble Horizon, 3ème étage, 5ème Avenue Sandervalia, Commune de Kaloum."
    )


def search_person_by_name(name: str) -> Optional[Dict]:
    """
    Recherche très précise d'une personne par son nom dans Equipe, Gouvernance et MotDirecteur.
    Recherche flexible : cherche le nom complet ou chaque partie du nom.
    Exclut TOUJOURS les statuts 'brouillon' et is_deleted=True.
    Retourne None si pas trouvé.
    """
    try:
        from core import models as aguipex_models
        
        name_original = (name or '').strip()
        name_normalized = _normalize(name_original)
        
        if not name_normalized or len(name_normalized) < 2:
            return None
        
        # Extraire les parties du nom (ex: "Kaba" ou "Amadou Daff BALDE")
        name_parts = [part.strip() for part in name_original.split() if len(part.strip()) >= 2]
        name_parts_normalized = [part.strip() for part in name_normalized.split() if len(part.strip()) >= 2]
        
        # Construire une recherche Q flexible
        q_equipe = Q()
        q_gouv = Q()
        q_dg = Q()
        q_personnel = Q()
        q_responsable = Q()
        
        # Recherche avec le nom complet
        q_equipe |= Q(name__icontains=name_original) | Q(name__icontains=name_normalized)
        q_gouv |= Q(nom__icontains=name_original) | Q(nom__icontains=name_normalized)
        q_dg |= Q(nomDG__icontains=name_original) | Q(nomDG__icontains=name_normalized)
        q_personnel |= Q(nom__icontains=name_original) | Q(nom__icontains=name_normalized) | Q(prenom__icontains=name_original) | Q(prenom__icontains=name_normalized)
        q_responsable |= Q(responsable_entreprise__icontains=name_original) | Q(responsable_entreprise__icontains=name_normalized)
        
        # Recherche avec chaque partie du nom (pour trouver "Kaba" dans "Kaba Diallo")
        for part in name_parts:
            if len(part) >= 2:
                q_equipe |= Q(name__icontains=part)
                q_gouv |= Q(nom__icontains=part)
                q_dg |= Q(nomDG__icontains=part)
                q_personnel |= Q(nom__icontains=part) | Q(prenom__icontains=part)
                q_responsable |= Q(responsable_entreprise__icontains=part)
        
        for part in name_parts_normalized:
            if len(part) >= 2:
                q_equipe |= Q(name__icontains=part)
                q_gouv |= Q(nom__icontains=part)
                q_dg |= Q(nomDG__icontains=part)
                q_personnel |= Q(nom__icontains=part) | Q(prenom__icontains=part)
                q_responsable |= Q(responsable_entreprise__icontains=part)
        
        # Recherche dans Equipe (priorité)
        equipe_result = aguipex_models.Equipe.objects.filter(
            status='publier',
            is_deleted=False
        ).filter(q_equipe).order_by('-created_at').first()
        
        if equipe_result:
            return {
                'type': 'equipe',
                'nom': html.unescape(str(equipe_result.name or '').strip()),
                'poste': html.unescape(str(equipe_result.fonction or '').strip()),
                'email': str(equipe_result.email or '').strip(),
                'contact': str(equipe_result.contact or '').strip(),
            }
        
        # Recherche dans Gouvernance
        gouv_result = aguipex_models.Gouvernance.objects.filter(
            status='publier',
            is_deleted=False
        ).filter(q_gouv).order_by('id').first()
        
        if gouv_result:
            contenu = _strip_html(gouv_result.contenu or '')
            return {
                'type': 'gouvernance',
                'nom': html.unescape(str(gouv_result.nom or '').strip()),
                'poste': html.unescape(str(gouv_result.poste or '').strip()),
                'contenu': contenu[:300] if contenu else '',
            }
        
        # Recherche dans MotDirecteur (DG)
        mot_dg = aguipex_models.MotDirecteur.objects.filter(
            status='publier',
            is_deleted=False
        ).filter(q_dg).order_by('-created_at').first()
        
        if mot_dg:
            contenu = _strip_html(mot_dg.contenu or '')
            return {
                'type': 'dg',
                'nom': html.unescape(str(mot_dg.nomDG or '').strip()),
                'poste': html.unescape(str(mot_dg.poste or '').strip()),
                'contenu': contenu[:300] if contenu else '',
            }
        
        # Recherche dans PersonnelInterprofession
        personnel_result = aguipex_models.PersonnelInterprofession.objects.filter(
            status='publier',
            is_deleted=False
        ).filter(q_personnel).order_by('-created_at').first()
        
        if personnel_result:
            nom_complet = f"{personnel_result.prenom} {personnel_result.nom}".strip()
            return {
                'type': 'personnel_interprofession',
                'nom': html.unescape(nom_complet),
                'poste': html.unescape(str(personnel_result.poste or '').strip()),
                'email': str(personnel_result.email or '').strip(),
                'interprofession': html.unescape(str(personnel_result.interprofession.nom or '').strip()),
            }
        
        # Recherche dans responsables d'entreprises (CandidatureManifestation)
        responsable_result = aguipex_models.CandidatureManifestation.objects.filter(
            is_deleted=False
        ).filter(q_responsable).exclude(responsable_entreprise__isnull=True).exclude(responsable_entreprise='').order_by('-date_candidature').first()
        
        if responsable_result:
            entreprise_nom = responsable_result.entreprise.nom if responsable_result.entreprise else responsable_result.nom_entreprise or 'Entreprise'
            return {
                'type': 'responsable_entreprise',
                'nom': html.unescape(str(responsable_result.responsable_entreprise or '').strip()),
                'poste': 'Responsable',
                'entreprise': html.unescape(str(entreprise_nom)),
                'email': str(responsable_result.email_contact or '').strip(),
                'telephone': str(responsable_result.telephone_contact or '').strip(),
            }
        
        return None
    except Exception:
        return None


def search_specific_person_by_keywords(question: str) -> Optional[Dict]:
    """
    Recherche EXPERT DATA : recherche exhaustive et précise d'une personne par mots-clés.
    Explore TOUS les champs pertinents avec plusieurs stratégies de recherche.
    Scoring intelligent pour trouver le meilleur résultat.
    Exclut TOUJOURS les statuts 'brouillon' et is_deleted=True.
    Retourne None si pas trouvé.
    """
    try:
        from core import models as aguipex_models
        
        q_lower = _normalize(question or '')
        q_original = (question or '').strip()
        
        if not q_lower:
            return None
        
        # PRIORITÉ ABSOLUE : Détecter si on cherche une personne par son nom
        name_patterns = [
            r'qui est\s+(?:m\.|mr|madame|mme|monsieur|m\.|mme\.)?\s*([a-zéèêëàâäùûüôöîïç]+(?:\s+[a-zéèêëàâäùûüôöîïç]+)*)',
            r'qui est\s+([a-zéèêëàâäùûüôöîïç]+(?:\s+[a-zéèêëàâäùûüôöîïç]+)*)\s+(?:a|à|chez|de)\s+aguipex',
            r'([A-ZÉÈÊËÀÂÄÙÛÜÔÖÎÏÇ][a-zéèêëàâäùûüôöîïç]+(?:\s+[A-ZÉÈÊËÀÂÄÙÛÜÔÖÎÏÇ][a-zéèêëàâäùûüôöîïç]+)*)\s+(?:a|à|chez|de)\s+aguipex',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, q_original, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) >= 2:
                    person_result = search_person_by_name(name)
                    if person_result:
                        return person_result
        
        # Extraire les mots-clés significatifs avec préservation de l'ordre
        keywords = []
        for w in q_lower.split():
            if (len(w) >= 2 and w not in STOPWORDS_FR) or w in ['rh', 'dg', 'dga', 'ceo']:
                keywords.append(w)
        
        if not keywords:
            return None
        
        # STRATÉGIE EXPERT DATA : Recherche exhaustive avec plusieurs niveaux de précision
        
        # Niveau 1 : Recherche AND stricte (tous les mots-clés doivent être présents)
        # Niveau 2 : Recherche AND flexible (mots-clés importants doivent être présents)
        # Niveau 3 : Recherche OR avec scoring élevé
        
        # Catégoriser les mots-clés
        poste_keywords = [kw for kw in keywords if kw in ['chef', 'responsable', 'directeur', 'directrice', 'adjoint', 'adjointe', 'dga', 'dg']]
        dept_keywords = [kw for kw in keywords if kw in ['statistique', 'statistiques', 'commercial', 'finance', 'communication', 'technique', 'juridique', 'rh', 'departement', 'département']]
        all_important_keywords = poste_keywords + dept_keywords
        other_keywords = [kw for kw in keywords if kw not in all_important_keywords]
        
        # STRATÉGIE 1 : Recherche AND stricte dans fonction/poste uniquement
        if len(keywords) >= 2:
            q_equipe_and = Q()
            q_gouv_and = Q()
            
            # Construire AND pour tous les mots-clés dans fonction
            for kw in keywords:
                if len(kw) >= 2:
                    q_equipe_and &= Q(fonction__icontains=kw)
                    q_gouv_and &= Q(poste__icontains=kw)
            
            equipe_and = aguipex_models.Equipe.objects.filter(
                status='publier', is_deleted=False
            ).filter(q_equipe_and)
            
            if equipe_and.exists():
                # Scoring : compter combien de mots-clés matchent exactement
                best_match = None
                best_score = 0
                for eq in equipe_and:
                    fonction_text = _normalize(str(eq.fonction or ''))
                    score = sum(2 if kw in fonction_text else 0 for kw in keywords)  # Score 2 par mot-clé exact
                    if score > best_score:
                        best_score = score
                        best_match = eq
                
                if best_match and best_score >= len(keywords) * 2:  # Tous les mots-clés doivent matcher
                    return {
                        'type': 'equipe',
                        'nom': str(best_match.name or '').strip(),
                        'poste': str(best_match.fonction or '').strip(),
                        'email': str(best_match.email or '').strip(),
                        'contact': str(best_match.contact or '').strip(),
                    }
        
        # STRATÉGIE 2 : Recherche AND pour poste + département (plus flexible)
        if poste_keywords and dept_keywords:
            q_equipe_poste_dept = Q()
            q_gouv_poste_dept = Q()
            
            # Poste ET Département dans fonction
            q_equipe_poste = Q()
            q_equipe_dept = Q()
            for pk in poste_keywords:
                q_equipe_poste |= Q(fonction__icontains=pk)
            for dk in dept_keywords:
                q_equipe_dept |= Q(fonction__icontains=dk)
            q_equipe_poste_dept = q_equipe_poste & q_equipe_dept
            
            q_gouv_poste = Q()
            q_gouv_dept = Q()
            for pk in poste_keywords:
                q_gouv_poste |= Q(poste__icontains=pk)
            for dk in dept_keywords:
                q_gouv_dept |= Q(poste__icontains=dk)
            q_gouv_poste_dept = q_gouv_poste & q_gouv_dept
            
            equipe_poste_dept = aguipex_models.Equipe.objects.filter(
                status='publier', is_deleted=False
            ).filter(q_equipe_poste_dept)
            
            if equipe_poste_dept.exists():
                best_match = None
                best_score = 0
                for eq in equipe_poste_dept:
                    fonction_text = _normalize(str(eq.fonction or ''))
                    # Score élevé si contient poste ET département
                    score = (sum(3 if pk in fonction_text else 0 for pk in poste_keywords) +
                            sum(3 if dk in fonction_text else 0 for dk in dept_keywords))
                    if score > best_score:
                        best_score = score
                        best_match = eq
                
                if best_match and best_score >= 3:  # Au moins un poste ET un département
                    return {
                        'type': 'equipe',
                        'nom': str(best_match.name or '').strip(),
                        'poste': str(best_match.fonction or '').strip(),
                        'email': str(best_match.email or '').strip(),
                        'contact': str(best_match.contact or '').strip(),
                    }
            
            # Même chose pour Gouvernance
            gouv_poste_dept = aguipex_models.Gouvernance.objects.filter(
                status='publier', is_deleted=False
            ).filter(q_gouv_poste_dept)
            
            if gouv_poste_dept.exists():
                best_match = None
                best_score = 0
                for gv in gouv_poste_dept:
                    poste_text = _normalize(str(gv.poste or ''))
                    score = (sum(3 if pk in poste_text else 0 for pk in poste_keywords) +
                            sum(3 if dk in poste_text else 0 for dk in dept_keywords))
                    if score > best_score:
                        best_score = score
                        best_match = gv
                
                if best_match and best_score >= 3:
                    contenu = _strip_html(best_match.contenu or '')
                    return {
                        'type': 'gouvernance',
                        'nom': str(best_match.nom or '').strip(),
                        'poste': str(best_match.poste or '').strip(),
                        'contenu': contenu[:300] if contenu else '',
                    }
        
        # STRATÉGIE 3 : Recherche OR avec scoring intelligent (exploration exhaustive)
        q_equipe_or = Q()
        q_gouv_or = Q()
        
        for kw in keywords:
            if len(kw) >= 2:
                # Recherche dans TOUS les champs pertinents
                q_equipe_or |= Q(fonction__icontains=kw) | Q(name__icontains=kw)
                q_gouv_or |= Q(poste__icontains=kw) | Q(nom__icontains=kw)
        
        # Recherche exhaustive dans Equipe
        equipe_all = aguipex_models.Equipe.objects.filter(
            status='publier', is_deleted=False
        ).filter(q_equipe_or)
        
        if equipe_all.exists():
            best_match = None
            best_score = 0
            for eq in equipe_all:
                fonction_text = _normalize(str(eq.fonction or ''))
                name_text = _normalize(str(eq.name or ''))
                
                # Scoring expert : fonction compte plus que nom
                score = 0
                for kw in keywords:
                    if kw in fonction_text:
                        score += 5  # Fonction = score élevé
                    elif kw in name_text:
                        score += 1  # Nom = score faible
                
                # Bonus si tous les mots-clés importants sont présents
                if all_important_keywords:
                    if all(kw in fonction_text for kw in all_important_keywords):
                        score += 10  # Bonus majeur
                
                if score > best_score:
                    best_score = score
                    best_match = eq
            
            # Seuil minimum : au moins 50% des mots-clés doivent matcher dans fonction
            if best_match and best_score >= len(keywords) * 2:
                return {
                    'type': 'equipe',
                    'nom': str(best_match.name or '').strip(),
                    'poste': str(best_match.fonction or '').strip(),
                    'email': str(best_match.email or '').strip(),
                    'contact': str(best_match.contact or '').strip(),
                }
        
        # Recherche exhaustive dans Gouvernance
        gouv_all = aguipex_models.Gouvernance.objects.filter(
            status='publier', is_deleted=False
        ).filter(q_gouv_or)
        
        if gouv_all.exists():
            best_match = None
            best_score = 0
            for gv in gouv_all:
                poste_text = _normalize(str(gv.poste or ''))
                nom_text = _normalize(str(gv.nom or ''))
                
                score = 0
                for kw in keywords:
                    if kw in poste_text:
                        score += 5
                    elif kw in nom_text:
                        score += 1
                
                if all_important_keywords:
                    if all(kw in poste_text for kw in all_important_keywords):
                        score += 10
                
                if score > best_score:
                    best_score = score
                    best_match = gv
            
            if best_match and best_score >= len(keywords) * 2:
                contenu = _strip_html(best_match.contenu or '')
                return {
                    'type': 'gouvernance',
                    'nom': str(best_match.nom or '').strip(),
                    'poste': str(best_match.poste or '').strip(),
                    'contenu': contenu[:300] if contenu else '',
                }
        
        return None
    except Exception as e:
        return None


def get_dg_equipe_full_answer(question: str) -> str:
    """
    Réponse sur le DG et l'équipe à partir de la base : MotDirecteur, Equipe, Gouvernance.
    Recherche précise pour "dga", "directeur général adjoint", "chef de département", etc.
    Ne lève jamais d'exception : retourne un message de repli en cas d'erreur.
    """
    fallback = (
        "Les informations sur la direction et l'équipe sont en cours de mise à jour. "
        "Consultez les pages **À propos** et **Équipes** dans le menu pour les détails."
    )
    try:
        from core import models as aguipex_models

        parts = []
        q_lower = _normalize(question or '')
        
        # PRIORITÉ ABSOLUE : Si la question demande explicitement l'équipe, afficher DG + DGA + TOUS les membres
        demande_equipe = any(k in q_lower for k in ['equipe', 'équipe', 'équipes', 'equipes', 'qui sont', 'membres', 'membre', 'personnel', 'employes', 'employés', 'liste', 'tous'])
        
        if demande_equipe:
            # 1. Directeur Général (DG)
            mot_dg = aguipex_models.MotDirecteur.objects.filter(
                status='publier', is_deleted=False
            ).order_by('-created_at').first()
            if mot_dg:
                nom = str(mot_dg.nomDG or '').strip()
                poste = str(mot_dg.poste or '').strip()
                titre_msg = str(mot_dg.titre or '').strip()
                if nom or poste:
                    parts.append(f"**Directeur Général d'AGUIPEX**\n\n• **{nom}** — {poste}.")
                if titre_msg:
                    parts.append(f"• *{titre_msg}*")
                contenu = _strip_html(mot_dg.contenu or '')
                if contenu and len(contenu) > 20:
                    parts.append(contenu[:350] + ('...' if len(contenu) > 350 else ''))
            
            # 2. Directeur Général Adjoint (DGA)
            gouv_dga = aguipex_models.Gouvernance.objects.filter(
                status='publier', is_deleted=False
            ).filter(
                Q(poste__icontains='adjoint') | Q(poste__icontains='adjointe') | 
                Q(poste__icontains='dga') | Q(poste__icontains='vice')
            ).order_by('id').first()
            
            if gouv_dga:
                nom_dga = str(gouv_dga.nom or '').strip()
                poste_dga = str(gouv_dga.poste or '').strip()
                if nom_dga:
                    if parts:
                        parts.append("")
                    parts.append(f"**Directeur Général Adjoint**\n\n• **{nom_dga}** — {poste_dga}.")
            else:
                # Chercher dans Equipe si pas trouvé dans Gouvernance
                equipe_dga = aguipex_models.Equipe.objects.filter(
                    status='publier', is_deleted=False
                ).filter(
                    Q(fonction__icontains='adjoint') | Q(fonction__icontains='adjointe') | 
                    Q(fonction__icontains='dga') | Q(fonction__icontains='vice')
                ).order_by('-created_at').first()
                
                if equipe_dga:
                    nom_dga = str(equipe_dga.name or '').strip()
                    fonction_dga = str(equipe_dga.fonction or '').strip()
                    if nom_dga:
                        if parts:
                            parts.append("")
                        parts.append(f"**Directeur Général Adjoint**\n\n• **{nom_dga}** — {fonction_dga}.")
            
            # 3. Tous les membres de l'équipe
            equipes = aguipex_models.Equipe.objects.filter(
                status='publier', is_deleted=False
            ).order_by('fonction', 'name')
            
            if equipes.exists():
                if parts:
                    parts.append("")
                parts.append("**Équipe AGUIPEX - Tous les membres** :\n")
                
                for e in equipes:
                    name = html.unescape(str(getattr(e, 'name', '') or '').strip())
                    fonction = html.unescape(str(getattr(e, 'fonction', '') or '').strip())
                    
                    if name:
                        # Ajouter email et contact si disponibles
                        email = str(getattr(e, 'email', '') or '').strip()
                        contact = str(getattr(e, 'contact', '') or '').strip()
                        contact_info = []
                        if email:
                            contact_info.append(f"Email : {email}")
                        if contact:
                            contact_info.append(f"Contact : {contact}")
                        
                        if contact_info:
                            parts.append(f"• **{name}** — {fonction} ({' | '.join(contact_info)})")
                        else:
                            parts.append(f"• **{name}** — {fonction}")
            
            # Retourner la réponse complète (DG + DGA + Équipe)
            if parts:
                return "\n\n".join(parts).strip()
            else:
                # Si rien n'est trouvé, afficher un message explicite
                return "**Équipe AGUIPEX**\n\nAucune information sur la direction et l'équipe n'est disponible pour le moment. Veuillez consulter la page **Équipes** dans le menu pour plus d'informations."
        
        # PRIORITÉ 1 : Recherche par nom de personne (ex: "qui est kaba", "kaba a aguipex")
        # Détecter les patterns de recherche par nom
        name_search_patterns = [
            r'qui est\s+(?:m\.|mr|madame|mme|monsieur|m\.|mme\.)?\s*([A-ZÉÈÊËÀÂÄÙÛÜÔÖÎÏÇ][a-zéèêëàâäùûüôöîïç]+(?:\s+[A-ZÉÈÊËÀÂÄÙÛÜÔÖÎÏÇ][a-zéèêëàâäùûüôöîïç]+)*)',
            r'qui est\s+([a-zéèêëàâäùûüôöîïç]+(?:\s+[a-zéèêëàâäùûüôöîïç]+)*)\s+(?:a|à|chez|de)\s+aguipex',
            r'([A-ZÉÈÊËÀÂÄÙÛÜÔÖÎÏÇ][a-zéèêëàâäùûüôöîïç]+(?:\s+[A-ZÉÈÊËÀÂÄÙÛÜÔÖÎÏÇ][a-zéèêëàâäùûüôöîïç]+)*)\s+(?:a|à|chez|de)\s+aguipex',
            r'([A-ZÉÈÊËÀÂÄÙÛÜÔÖÎÏÇ][a-zéèêëàâäùûüôöîïç]+)\s+(?:a|à|chez|de)\s+aguipex',
        ]
        
        for pattern in name_search_patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) >= 2:
                    person_result = search_person_by_name(name)
                    if person_result:
                        nom = person_result.get('nom', '').strip()
                        poste = person_result.get('poste', '').strip()
                        if nom:
                            # Titre selon le type
                            if person_result.get('type') == 'dg':
                                parts.append(f"**Directeur Général d'AGUIPEX**\n\n• **{nom}** — {poste}.")
                            else:
                                parts.append(f"**{nom}**\n\n• **{nom}** — {poste}.")
                            
                            # Ajouter email et contact si disponibles (Equipe uniquement)
                            email = person_result.get('email', '').strip()
                            contact = person_result.get('contact', '').strip()
                            if email or contact:
                                contact_info = []
                                if email:
                                    contact_info.append(f"Email : {email}")
                                if contact:
                                    contact_info.append(f"Contact : {contact}")
                                if contact_info:
                                    parts.append("• " + " | ".join(contact_info))
                            
                            # Ajouter contenu si disponible (Gouvernance ou DG)
                            contenu = person_result.get('contenu', '').strip()
                            if contenu and len(contenu) > 20:
                                parts.append("\n" + contenu[:300] + ('...' if len(contenu) > 300 else ''))
                            
                            if parts:
                                return "\n\n".join(parts).strip()
        
        # PRIORITÉ 2 : Recherche très précise par mots-clés (chef, département, statistique, etc.)
        # Cette recherche est TOUJOURS activée pour les questions sur des personnes spécifiques
        # Recherche systématique si la question contient des mots-clés de poste/département
        specific_keywords = ['chef', 'departement', 'département', 'responsable', 'directeur', 'directrice', 
                            'statistique', 'statistiques', 'commercial', 'finance', 'communication', 
                            'technique', 'juridique', 'rh', 'ressources humaines', 'membre', 'equipe',
                            'nom de', 'coordonnées', 'contact de']
        
        # Toujours essayer une recherche précise si la question contient des mots-clés spécifiques
        # ou si elle semble être une question sur une personne (contient "qui", "nom", "chef", etc.)
        should_search = any(kw in q_lower for kw in specific_keywords) or any(phrase in q_lower for phrase in ['qui est', 'nom de', 'chef de', 'responsable de', 'chef du', 'responsable du'])
        
        if should_search:
            person_result = search_specific_person_by_keywords(question)
            if person_result:
                nom = person_result.get('nom', '').strip()
                poste = person_result.get('poste', '').strip()
                if nom and poste:
                    # Titre adaptatif selon le contexte
                    if 'chef' in q_lower or 'responsable' in q_lower:
                        title = f"**{poste}**"
                    elif 'directeur' in q_lower or 'directrice' in q_lower:
                        title = f"**{poste}**"
                    else:
                        title = f"**{nom}**"
                    
                    parts.append(f"{title}\n\n• **{nom}** — {poste}.")
                    
                    # Ajouter email et contact si disponibles
                    email = person_result.get('email', '').strip()
                    contact = person_result.get('contact', '').strip()
                    if email or contact:
                        contact_info = []
                        if email:
                            contact_info.append(f"Email : {email}")
                        if contact:
                            contact_info.append(f"Contact : {contact}")
                        if contact_info:
                            parts.append("• " + " | ".join(contact_info))
                    
                    # Ajouter contenu si disponible (Gouvernance)
                    contenu = person_result.get('contenu', '').strip()
                    if contenu and len(contenu) > 20:
                        parts.append("\n" + contenu[:300] + ('...' if len(contenu) > 300 else ''))
                    
                    if parts:
                        return "\n\n".join(parts).strip()
            
            # RECHERCHE DE SECOURS EXPERT DATA : Exploration exhaustive avec toutes les combinaisons possibles
            # Si pas trouvé avec la recherche précise, essayer des recherches plus larges mais toujours précises
            
            # Stratégie 1 : Recherche directe avec combinaisons flexibles
            if any(kw in q_lower for kw in ['chef', 'responsable']) and any(kw in q_lower for kw in ['statistique', 'statistiques', 'departement', 'département']):
                # Recherche AND : (chef OU responsable) ET (statistique OU statistiques)
                equipe_results = aguipex_models.Equipe.objects.filter(
                    status='publier',
                    is_deleted=False
                ).filter(
                    (Q(fonction__icontains='chef') | Q(fonction__icontains='responsable')) &
                    (Q(fonction__icontains='statistique') | Q(fonction__icontains='statistiques') | 
                     Q(fonction__icontains='departement') | Q(fonction__icontains='département'))
                ).order_by('-created_at')
                
                if equipe_results.exists():
                    # Prendre le premier résultat (déjà filtré précisément)
                    best_match = equipe_results.first()
                    nom = str(best_match.name or '').strip()
                    fonction = str(best_match.fonction or '').strip()
                    if nom and fonction:
                        parts.append(f"**{fonction}**\n\n• **{nom}** — {fonction}.")
                        email = str(best_match.email or '').strip()
                        contact = str(best_match.contact or '').strip()
                        if email or contact:
                            contact_info = []
                            if email:
                                contact_info.append(f"Email : {email}")
                            if contact:
                                contact_info.append(f"Contact : {contact}")
                            if contact_info:
                                parts.append("• " + " | ".join(contact_info))
                        if parts:
                            return "\n\n".join(parts).strip()
            
            # Stratégie 2 : Recherche exhaustive dans TOUS les champs Equipe
            # Chercher chaque mot-clé dans fonction ET name pour être sûr de ne rien manquer
            all_equipe = aguipex_models.Equipe.objects.filter(
                status='publier',
                is_deleted=False
            ).all()
            
            if all_equipe.exists():
                best_match = None
                best_score = 0
                keywords_for_search = [kw for kw in q_lower.split() if len(kw) >= 2 and kw not in STOPWORDS_FR]
                
                for eq in all_equipe:
                    fonction_text = _normalize(str(eq.fonction or ''))
                    name_text = _normalize(str(eq.name or ''))
                    
                    # Score : compter combien de mots-clés matchent dans fonction (priorité) ou name
                    score = 0
                    matches_in_fonction = 0
                    for kw in keywords_for_search:
                        if kw in fonction_text:
                            score += 10  # Match dans fonction = très important
                            matches_in_fonction += 1
                        elif kw in name_text:
                            score += 2   # Match dans nom = moins important
                    
                    # Bonus si la majorité des mots-clés matchent dans fonction
                    if matches_in_fonction >= len(keywords_for_search) * 0.6:  # Au moins 60% dans fonction
                        score += 20
                    
                    if score > best_score:
                        best_score = score
                        best_match = eq
                
                # Seuil : au moins 2 mots-clés doivent matcher dans fonction pour être pertinent
                if best_match and best_score >= 20:
                    nom = str(best_match.name or '').strip()
                    fonction = str(best_match.fonction or '').strip()
                    if nom and fonction:
                        parts.append(f"**{fonction}**\n\n• **{nom}** — {fonction}.")
                        email = str(best_match.email or '').strip()
                        contact = str(best_match.contact or '').strip()
                        if email or contact:
                            contact_info = []
                            if email:
                                contact_info.append(f"Email : {email}")
                            if contact:
                                contact_info.append(f"Contact : {contact}")
                            if contact_info:
                                parts.append("• " + " | ".join(contact_info))
                        if parts:
                            return "\n\n".join(parts).strip()
            
            # Stratégie 3 : Recherche dans Gouvernance aussi (au cas où)
            all_gouv = aguipex_models.Gouvernance.objects.filter(
                status='publier',
                is_deleted=False
            ).all()
            
            if all_gouv.exists():
                best_match = None
                best_score = 0
                keywords_for_search = [kw for kw in q_lower.split() if len(kw) >= 2 and kw not in STOPWORDS_FR]
                
                for gv in all_gouv:
                    poste_text = _normalize(str(gv.poste or ''))
                    nom_text = _normalize(str(gv.nom or ''))
                    
                    score = 0
                    matches_in_poste = 0
                    for kw in keywords_for_search:
                        if kw in poste_text:
                            score += 10
                            matches_in_poste += 1
                        elif kw in nom_text:
                            score += 2
                    
                    if matches_in_poste >= len(keywords_for_search) * 0.6:
                        score += 20
                    
                    if score > best_score:
                        best_score = score
                        best_match = gv
                
                if best_match and best_score >= 20:
                    nom = str(best_match.nom or '').strip()
                    poste = str(best_match.poste or '').strip()
                    if nom and poste:
                        parts.append(f"**{poste}**\n\n• **{nom}** — {poste}.")
                        contenu = _strip_html(best_match.contenu or '')
                        if contenu and len(contenu) > 20:
                            parts.append("\n" + contenu[:300] + ('...' if len(contenu) > 300 else ''))
                        if parts:
                            return "\n\n".join(parts).strip()
        
        # Détection précise : recherche spécifique pour DGA
        is_dga_query = any(term in q_lower for term in [
            'dga', 'directeur general adjoint', 'directeur generale adjoint', 
            'directrice generale adjointe', 'directrice general adjoint',
            'adjoint', 'adjointe', 'vice directeur', 'vice directrice'
        ])
        
        # Détection précise : recherche spécifique pour DG uniquement
        is_dg_only_query = any(term in q_lower for term in [
            'dg', 'directeur general', 'directeur generale', 'directrice generale',
            'directrice general', 'qui est le directeur', 'qui est la directrice'
        ]) and not is_dga_query

        # 1. Recherche spécifique du DGA dans Gouvernance et Equipe
        if is_dga_query:
            dga_found = False
            
            # Recherche dans Gouvernance (priorité)
            gouv_dga = aguipex_models.Gouvernance.objects.filter(
                status='publier', is_deleted=False
            ).filter(
                Q(poste__icontains='adjoint') | Q(poste__icontains='adjointe') | 
                Q(poste__icontains='dga') | Q(poste__icontains='vice')
            ).order_by('id').first()
            
            if gouv_dga:
                nom_dga = str(gouv_dga.nom or '').strip()
                poste_dga = str(gouv_dga.poste or '').strip()
                contenu_dga = _strip_html(gouv_dga.contenu or '')
                if nom_dga:
                    parts.append(f"**Directeur Général Adjoint d'AGUIPEX**\n\n• **{nom_dga}** — {poste_dga}.")
                    if contenu_dga and len(contenu_dga) > 20:
                        parts.append(contenu_dga[:350] + ('...' if len(contenu_dga) > 350 else ''))
                    dga_found = True
            
            # Si pas trouvé dans Gouvernance, chercher dans Equipe
            if not dga_found:
                equipe_dga = aguipex_models.Equipe.objects.filter(
                    status='publier', is_deleted=False
                ).filter(
                    Q(fonction__icontains='adjoint') | Q(fonction__icontains='adjointe') | 
                    Q(fonction__icontains='dga') | Q(fonction__icontains='vice')
                ).order_by('-created_at').first()
                
                if equipe_dga:
                    nom_dga = str(equipe_dga.name or '').strip()
                    fonction_dga = str(equipe_dga.fonction or '').strip()
                    if nom_dga:
                        parts.append(f"**Directeur Général Adjoint d'AGUIPEX**\n\n• **{nom_dga}** — {fonction_dga}.")
                        dga_found = True
            
            if not dga_found:
                return (
                    "Je n'ai pas trouvé d'informations spécifiques sur le Directeur Général Adjoint (DGA) dans notre base de données. "
                    "Veuillez consulter la page **À propos** ou **Équipes** dans le menu pour les informations à jour."
                )
            
            return "\n\n".join(parts).strip()

        # 2. Recherche spécifique du DG uniquement
        if is_dg_only_query:
            mot_dg = aguipex_models.MotDirecteur.objects.filter(
                status='publier', is_deleted=False
            ).order_by('-created_at').first()
        if mot_dg:
            nom = str(mot_dg.nomDG or '').strip()
            poste = str(mot_dg.poste or '').strip()
            titre_msg = str(mot_dg.titre or '').strip()
            if nom or poste:
                parts.append(f"**Directeur Général d'AGUIPEX**\n\n• **{nom}** — {poste}.")
            if titre_msg:
                parts.append(f"• *{titre_msg}*")
            contenu = _strip_html(mot_dg.contenu or '')
            if contenu and len(contenu) > 20:
                parts.append(contenu[:350] + ('...' if len(contenu) > 350 else ''))
                if parts:
                    return "\n\n".join(parts).strip()

        # 3. Réponse générale : DG + DGA + équipe si demandée
        # Mot du DG (nomDG, poste) — source officielle
        mot_dg = aguipex_models.MotDirecteur.objects.filter(
            status='publier', is_deleted=False
        ).order_by('-created_at').first()
        if mot_dg:
            nom = str(mot_dg.nomDG or '').strip()
            poste = str(mot_dg.poste or '').strip()
            titre_msg = str(mot_dg.titre or '').strip()
            if nom or poste:
                parts.append(f"**Directeur Général d'AGUIPEX**\n\n• **{nom}** — {poste}.")
            if titre_msg:
                parts.append(f"• *{titre_msg}*")
            contenu = _strip_html(mot_dg.contenu or '')
            if contenu and len(contenu) > 20:
                parts.append(contenu[:350] + ('...' if len(contenu) > 350 else ''))

        # DGA dans Gouvernance (si pas de recherche spécifique)
        gouv_dga = aguipex_models.Gouvernance.objects.filter(
            status='publier', is_deleted=False
        ).filter(
            Q(poste__icontains='adjoint') | Q(poste__icontains='adjointe') | 
            Q(poste__icontains='dga') | Q(poste__icontains='vice')
        ).order_by('id').first()
        
        if gouv_dga:
            nom_dga = str(gouv_dga.nom or '').strip()
            poste_dga = str(gouv_dga.poste or '').strip()
            if nom_dga:
                if parts:
                    parts.append("")
                parts.append(f"**Directeur Général Adjoint**\n\n• **{nom_dga}** — {poste_dga}.")
        else:
            # Chercher dans Equipe si pas trouvé dans Gouvernance
            equipe_dga = aguipex_models.Equipe.objects.filter(
                status='publier', is_deleted=False
            ).filter(
                Q(fonction__icontains='adjoint') | Q(fonction__icontains='adjointe') | 
                Q(fonction__icontains='dga') | Q(fonction__icontains='vice')
            ).order_by('-created_at').first()
            
            if equipe_dga:
                nom_dga = str(equipe_dga.name or '').strip()
                fonction_dga = str(equipe_dga.fonction or '').strip()
                if nom_dga:
                    if parts:
                        parts.append("")
                    parts.append(f"**Directeur Général Adjoint**\n\n• **{nom_dga}** — {fonction_dga}.")

        # Gouvernance complète si demandée explicitement
        if any(k in q_lower for k in ['gouvernance', 'direction', 'organigramme']):
            gouv = aguipex_models.Gouvernance.objects.filter(
                status='publier', is_deleted=False
            ).exclude(
                Q(poste__icontains='adjoint') | Q(poste__icontains='adjointe') | 
                Q(poste__icontains='dga') | Q(poste__icontains='vice')
            ).order_by('id')[:6]
            if gouv.exists():
                if parts:
                    parts.append("")
                parts.append("**Gouvernance** :")
                for g in gouv:
                    nom_g = str(getattr(g, 'nom', '') or '').strip()
                    poste_g = str(getattr(g, 'poste', '') or '').strip()
                    if nom_g:
                        parts.append(f"• **{nom_g}** — {poste_g}")

        if not parts:
            return fallback
        return "\n\n".join(parts).strip()
    except Exception:
        return fallback


def get_aguipex_about_full_answer() -> str:
    """
    Réponse sur AGUIPEX (qui sommes-nous, mission, vision) à partir de la base.
    Ne lève jamais d'exception : retourne un message de repli en cas d'erreur.
    """
    fallback = (
        "AGUIPEX est l'Agence Guinéenne pour la Promotion des Exportations. "
        "Consultez la page **À propos** dans le menu pour la présentation complète."
    )
    try:
        from core import models as aguipex_models

        parts = []

        # Qui sommes-nous
        qsn = aguipex_models.QuiSommeNous.objects.filter(
            status='publier', is_deleted=False
        ).order_by('-created_at').first()
        if qsn:
            titre = str(qsn.titre or '').strip()
            detail = _strip_html(qsn.detail or '')
            if titre or detail:
                parts.append(f"**{titre or 'Qui sommes-nous ?'}**\n\n{detail[:600]}{'...' if len(detail) > 600 else ''}")

        # Vision & Mission
        vm = aguipex_models.VisionMission.objects.filter(
            status='publier', is_deleted=False
        ).order_by('-created_at').first()
        if vm:
            mission = str(getattr(vm, 'texte_mission', '') or '').strip()
            vision = str(getattr(vm, 'texte_vision', '') or '').strip()
            if mission or vision:
                parts.append("")
                if mission:
                    parts.append(f"**Mission** : {mission}")
                if vision:
                    parts.append(f"**Vision** : {vision}")

        # Presentation (court extrait)
        pres = aguipex_models.Presentation.objects.filter(
            status='publier', is_deleted=False
        ).order_by('-created_at').first()
        if pres and getattr(pres, 'content', None):
            raw = getattr(pres, 'content', '') or ''
            content = _strip_html(raw)[:300]
            if content:
                parts.append("")
                parts.append(content + ('...' if len(raw) > 300 else ''))

        if not parts:
            return fallback
        return "\n\n".join(parts).strip()
    except Exception:
        return fallback


# Stopwords français courants (liste réduite pour garder des termes métier)
STOPWORDS_FR = {
    'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'en', 'au', 'aux',
    'ce', 'cette', 'ces', 'mon', 'ma', 'mes', 'ton', 'ta', 'tes', 'son', 'sa', 'ses',
    'notre', 'nos', 'votre', 'vos', 'leur', 'leurs', 'quel', 'quelle', 'quels', 'quelles',
    'je', 'tu', 'il', 'elle', 'on', 'nous', 'vous', 'ils', 'elles',
    'être', 'est', 'sont', 'été', 'avoir', 'a', 'as', 'avons', 'avez', 'ont',
    'faire', 'fait', 'fais', 'faites', 'peut', 'pour', 'par', 'avec', 'sans', 'sous',
    'dans', 'sur', 'que', 'qui', 'quoi', 'dont', 'où', 'comment', 'pourquoi', 'combien',
    'si', 'mais', 'ou', 'donc', 'or', 'ni', 'car', 'ne', 'pas', 'plus', 'moins',
    'très', 'trop', 'bien', 'mal', 'tout', 'tous', 'toute', 'toutes', 'autre', 'autres',
    'ici', 'là', 'alors', 'ainsi', 'aussi', 'encore', 'toujours', 'jamais', 'souvent',
    'comment', 'quelque', 'certains', 'plusieurs', 'chaque', 'même', 'entre', 'vers',
}


def _normalize(text: str) -> str:
    """Normalise le texte: minuscules, suppression accents basique, ponctuation."""
    if not text or not isinstance(text, str):
        return ""
    text = text.lower().strip()
    # Remplacer caractères accentués
    accents = {'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e', 'à': 'a', 'â': 'a', 'ä': 'a',
               'ù': 'u', 'û': 'u', 'ü': 'u', 'ô': 'o', 'ö': 'o', 'î': 'i', 'ï': 'i', 'ç': 'c'}
    for a, b in accents.items():
        text = text.replace(a, b)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_keywords(question: str, max_keywords: int = 25) -> List[Tuple[str, int]]:
    """
    Extrait les mots-clés pertinents de la question (pour Word Cloud + recherche).
    Retourne une liste de (mot, poids) triée par pertinence.
    """
    normalized = _normalize(question)
    if not normalized:
        return []
    words = normalized.split()
    # Compter les occurrences, exclure stopwords et mots trop courts
    counts: Dict[str, int] = {}
    for w in words:
        if len(w) < 2 or w in STOPWORDS_FR or w.isdigit():
            continue
        counts[w] = counts.get(w, 0) + 1
    # Trier par fréquence décroissante, puis prendre les max_keywords premiers
    sorted_words = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:max_keywords]
    return sorted_words


def detect_intent(question: str, keywords: List[Tuple[str, int]]) -> str:
    """
    Détecte l'intention principale (salutation, procédures, statistiques, etc.).
    L'ordre compte : les intentions les plus précises sont détectées en premier.
    """
    q = _normalize(question)
    if not q:
        return 'general'

    # Salutation / remerciement
    if any(x in q for x in ['bonjour', 'salut', 'hello', 'bonsoir', 'coucou']):
        return 'greeting'
    if any(x in q for x in ['merci', 'remercie']):
        return 'thanks'

    # Procédures d'exportation (priorité : question précise sur comment exporter, étapes, exigences)
    procedure_export_terms = [
        'procedure', 'procedures', 'procédure', 'étapes', 'etapes', 'comment exporter',
        'comment faire', 'processus', 'exigences', 'formalites', 'formalités',
        'comment exporter', 'faire pour exporter', 'exportation du', 'exportation de',
        'exporter du', 'exporter le', 'exporter la', 'conditions export',
    ]
    if any(term in q for term in procedure_export_terms):
        return 'procedure_export'

    # Intentions métier (mots-clés typiques)
    if any(k in q for k in ['statistique', 'chiffre', 'donnee', 'export', 'import', 'balance']):
        return 'statistiques'
    if any(k in q for k in ['entreprise', 'societe', 'company', 'annuaire']):
        return 'entreprises'
    if any(k in q for k in ['produit', 'cartographie', 'mapping', 'secteur']):
        return 'produits'
    if any(k in q for k in ['foire', 'foires', 'evenement', 'salon']):
        return 'foires'
    if any(k in q for k in ['manifestation', 'manifestations', 'postuler', 'candidature']):
        return 'manifestations'
    if any(k in q for k in ['projet', 'programme']):
        return 'projets'
    if any(k in q for k in ['interprofession']):
        return 'interprofessions'
    if any(k in q for k in ['actualite', 'news', 'nouvelle']):
        return 'actualites'
    if any(phrase in q for phrase in ['donnee strategique', 'donnees strategiques']):
        return 'donnees_strategiques'
    if any(k in q for k in ['faq', 'question frequente', 'questions frequentes', 'foire aux questions']):
        return 'faq'
    # DGA / Directeur Général Adjoint (priorité haute pour recherche précise)
    if any(term in q for term in [
        'dga', 'directeur general adjoint', 'directeur generale adjoint',
        'directrice generale adjointe', 'directrice general adjoint',
        'adjoint', 'adjointe', 'vice directeur', 'vice directrice'
    ]):
        return 'equipe'
    
    # DG / équipe / direction (priorité avant "aguipex" pour "qui est le DG")
    if any(k in q for k in [
        'dg', 'directeur', 'directrice', 'qui est le', 'qui est la', 'equipe', 'équipe', 'equipes', 'équipes',
        'direction', 'patron', 'ceo', 'chef', 'membres', 'gouvernance', 'organigramme'
    ]):
        return 'equipe'
    if any(k in q for k in [
        'contact', 'adresse', 'telephone', 'email', 'ecrire',
        'siege', 'situé', 'située', 'situe', 'situee', 'localisation', 'emplacement',
        'ou est', 'ou se trouve', 'trouver aguipex'
    ]):
        return 'contact'
    if any(k in q for k in ['aguipex', 'mission', 'vision', 'qui sommes', 'presentation']):
        return 'aguipex'

    return 'general'


def search_site_content(
    keywords: List[Tuple[str, int]],
    intent: str,
    limit_per_model: int = 3,
) -> List[Dict]:
    """
    Recherche sémantique sur le contenu du site (Statistiques, Projets, Entreprises,
    Manifestations, Foires, Produits, Actualités, Données stratégiques, etc.).
    Retourne une liste de dicts { 'source', 'title', 'snippet', 'url' }.
    """
    from core import models as aguipex_models

    if not keywords:
        return []
    # Liste des mots à chercher (sans poids pour le Q)
    terms = [k[0] for k in keywords[:12]]
    results = []

    def add_result(source: str, title: str, snippet: str, url: str):
        if title or snippet:
            # Décoder les entités HTML dans title et snippet
            title_decoded = html.unescape(str(title)) if title else ''
            snippet_decoded = html.unescape(str(snippet)) if snippet else ''
            results.append({'source': source, 'title': title_decoded, 'snippet': snippet_decoded[:300], 'url': url})

    def make_q_for_fields(terms_list, *fields):
        """Construit un Q sur les champs donnés (icontains) pour au moins un terme."""
        q = Q()
        for t in terms_list:
            if len(t) >= 2:
                for f in fields:
                    q |= Q(**{f"{f}__icontains": t})
        return q

    # Statistiques (titre uniquement)
    try:
        q_s = make_q_for_fields(terms, 'titre')
        for obj in aguipex_models.Statistique.objects.filter(is_deleted=False).filter(q_s)[:limit_per_model]:
            titre = _strip_html(getattr(obj, 'titre', '') or '')
            snippet = f"{titre} — {getattr(obj, 'valeur', '')} {getattr(obj, 'unite', '') or ''}"
            add_result('Statistiques', titre, snippet.strip(), '/statistiques/')
    except Exception:
        pass

    # Projets (title, description)
    try:
        q_p = make_q_for_fields(terms, 'title', 'description')
        for obj in aguipex_models.Projet.objects.filter(is_deleted=False).filter(q_p)[:limit_per_model]:
            slug = getattr(obj, 'slug', None)
            title = _strip_html(getattr(obj, 'title', '') or '')
            desc = _strip_html(getattr(obj, 'description', '') or '')[:200]
            add_result('Projets', title, desc, f'/projets/{slug}/' if slug else '/projets/')
    except Exception:
        pass

    # Entreprises (nom, description)
    try:
        q_e = make_q_for_fields(terms, 'nom', 'description')
        for obj in aguipex_models.Entreprise.objects.filter(is_deleted=False).filter(q_e)[:limit_per_model]:
            slug = getattr(obj, 'slug', None)
            nom = html.unescape(str(getattr(obj, 'nom', '') or ''))
            desc = _strip_html(getattr(obj, 'description', '') or '')[:200]
            add_result('Entreprises', nom, desc, f'/entreprises/{slug}/' if slug else '/entreprises/')
    except Exception:
        pass

    # Manifestations commerciales (titre, description)
    try:
        q_m = make_q_for_fields(terms, 'titre', 'description')
        for obj in aguipex_models.ManifestationCommerciale.objects.filter(is_deleted=False, statut_publication='publier').filter(q_m)[:limit_per_model]:
            slug = getattr(obj, 'slug', None)
            titre = _strip_html(getattr(obj, 'titre', '') or '')
            desc = _strip_html(getattr(obj, 'description', '') or '')[:200]
            add_result('Manifestations', titre, desc, f'/manifestations-commerciales/{slug}/' if slug else '/manifestations-commerciales/')
    except Exception:
        pass

    # Foires (titre, description)
    try:
        q_f = make_q_for_fields(terms, 'titre', 'description')
        for obj in aguipex_models.Foires.objects.filter(status='publier', is_deleted=False).filter(q_f)[:limit_per_model]:
            slug = getattr(obj, 'slug', None)
            titre = _strip_html(getattr(obj, 'titre', '') or '')
            desc = _strip_html(getattr(obj, 'description', '') or '')[:200]
            add_result('Foires', titre, desc, f'/foires/{slug}/' if slug else '/foires/')
    except Exception:
        pass

    # Produits (nom, description)
    try:
        q_pr = make_q_for_fields(terms, 'title', 'description')
        for obj in aguipex_models.Produit.objects.filter(status='publier', is_deleted=False).filter(q_pr)[:limit_per_model]:
            title = _strip_html(getattr(obj, 'title', '') or '')
            desc = _strip_html(getattr(obj, 'description', '') or '')[:200]
            add_result('Produits', title, desc, '/exportations/#potentiel-exportation')
    except Exception:
        pass

    # Actualités (grand_titre, detail)
    try:
        q_a = make_q_for_fields(terms, 'grand_titre', 'detail')
        for obj in aguipex_models.Actualite.objects.filter(status='publier', is_deleted=False).filter(q_a)[:limit_per_model]:
            slug = getattr(obj, 'slug', None)
            titre = _strip_html(getattr(obj, 'grand_titre', '') or '')
            detail = _strip_html(getattr(obj, 'detail', '') or '')[:200]
            add_result('Actualités', titre, detail, f'/actualites/{slug}/' if slug else '/actualite/')
    except Exception:
        pass

    # Données stratégiques (titre, detail)
    try:
        q_d = make_q_for_fields(terms, 'titre', 'detail')
        for obj in aguipex_models.DonneeStrategique.objects.filter(status='publier', is_deleted=False).filter(q_d)[:limit_per_model]:
            slug = getattr(obj, 'slug', None)
            titre = _strip_html(getattr(obj, 'titre', '') or '')
            detail = _strip_html(getattr(obj, 'detail', '') or '')[:200]
            add_result('Données stratégiques', titre, detail, f'/donnees/{slug}/' if slug else '/donnees-strategique/')
    except Exception:
        pass

    # Interprofessions (nom)
    try:
        q_i = make_q_for_fields(terms, 'nom')
        for obj in aguipex_models.Interprofession.objects.filter(is_deleted=False).filter(q_i)[:limit_per_model]:
            slug = getattr(obj, 'slug', None)
            nom = html.unescape(str(getattr(obj, 'nom', '') or ''))
            add_result('Interprofessions', nom, '', f'/interprofessions/{slug}/' if slug else '/interprofessions/')
    except Exception:
        pass

    # FAQ (question, response) — réponses exactes publiées
    try:
        q_faq = make_q_for_fields(terms, 'question', 'response')
        for obj in aguipex_models.FAQ.objects.filter(status='publier', is_deleted=False).filter(q_faq)[:limit_per_model]:
            question_faq = html.unescape(str(getattr(obj, 'question', '') or '').strip())
            response_faq = _strip_html(getattr(obj, 'response', '') or '')
            add_result('FAQ', question_faq, response_faq[:400], '/faq/')
    except Exception:
        pass

    # Gouvernance (nom, poste) — recherche précise pour DG, DGA, direction
    try:
        if any(term in ' '.join(terms) for term in ['dg', 'dga', 'directeur', 'directrice', 'adjoint', 'adjointe', 'gouvernance', 'direction']):
            q_gouv = make_q_for_fields(terms, 'nom', 'poste')
            for obj in aguipex_models.Gouvernance.objects.filter(status='publier', is_deleted=False).filter(q_gouv)[:limit_per_model]:
                nom_g = html.unescape(str(getattr(obj, 'nom', '') or '').strip())
                poste_g = html.unescape(str(getattr(obj, 'poste', '') or '').strip())
                contenu_g = _strip_html(getattr(obj, 'contenu', '') or '')[:200]
                snippet = f"{nom_g} — {poste_g}"
                if contenu_g:
                    snippet += f" : {contenu_g}"
                add_result('Gouvernance', nom_g or 'Membre de la gouvernance', snippet.strip(), '/about/')
    except Exception:
        pass

    # Equipe (name, fonction) — recherche précise pour équipe, membres
    try:
        if any(term in ' '.join(terms) for term in ['equipe', 'équipe', 'membre', 'membres', 'directeur', 'directrice', 'adjoint', 'adjointe', 'dga']):
            q_eq = make_q_for_fields(terms, 'name', 'fonction')
            for obj in aguipex_models.Equipe.objects.filter(status='publier', is_deleted=False).filter(q_eq)[:limit_per_model]:
                name_e = html.unescape(str(getattr(obj, 'name', '') or '').strip())
                fonction_e = html.unescape(str(getattr(obj, 'fonction', '') or '').strip())
                add_result('Équipe', name_e or 'Membre de l\'équipe', f"{name_e} — {fonction_e}".strip(), '/equipe/')
    except Exception:
        pass

    return results[:15]  # Max 15 extraits


def get_cached_response(question_normalized: str) -> Optional[str]:
    """Retourne une réponse en cache si la question (normalisée) a déjà été posée."""
    cache_key = f"chatbot_response:{hash(question_normalized) % (10 ** 8)}"
    return cache.get(cache_key)


def set_cached_response(question_normalized: str, response: str, timeout: int = 3600):
    """Met en cache la réponse (1h par défaut)."""
    cache_key = f"chatbot_response:{hash(question_normalized) % (10 ** 8)}"
    cache.set(cache_key, response, timeout=timeout)


def build_response(
    question: str,
    intent: str,
    search_results: List[Dict],
    keywords: List[Tuple[str, int]],
) -> Tuple[str, str]:
    """
    Construit la réponse du bot (texte principal, compris_as pour l'UI).
    Réponses exactes par rapport à la question posée ; pas de contenu hors-sujet.
    """
    understood = "Voici ce que j'ai compris de votre question : " + ", ".join([html.unescape(str(k[0])) for k in keywords[:8]]) if keywords else "Votre question"

    if intent == 'greeting':
        return (
            "Bonjour ! Je suis l'assistant virtuel d'AGUIPEX. Je peux vous renseigner sur nos services, "
            "les procédures et statistiques d'exportation, les entreprises, les manifestations et foires, les projets et bien plus. "
            "Comment puis-je vous aider ?",
            understood,
        )
    if intent == 'thanks':
        return (
            "Je vous en prie. N'hésitez pas si vous avez d'autres questions. L'équipe AGUIPEX reste à votre disposition.",
            understood,
        )

    # Réponse dédiée : procédures d'exportation (café, produits, etc.) — claire et directe
    if intent == 'procedure_export':
        full_answer = get_procedure_export_full_answer(question)
        return (full_answer, understood)

    # Siège / adresse / contact : réponse exacte avec les infos publiées (pas de redirection vers le site)
    if intent == 'contact':
        return (get_contact_siege_full_answer(), understood)

    # DG / équipe : réponse depuis la base (MotDirecteur, Equipe, Gouvernance)
    if intent == 'equipe':
        return (get_dg_equipe_full_answer(question), understood)

    q_lower = (question or '').lower()
    # Question sur AGUIPEX (siège, où, adresse) : donner l'adresse si c'est demandé
    if intent == 'aguipex' and any(k in q_lower for k in ['siege', 'situé', 'située', 'adresse', 'ou est', 'localisation', 'emplacement']):
        return (get_contact_siege_full_answer(), understood)
    # Question sur le DG / qui est : réponse depuis la base
    if intent == 'aguipex' and any(k in q_lower for k in ['dg', 'directeur', 'qui est le', 'qui est la', 'equipe', 'équipe']):
        return (get_dg_equipe_full_answer(question), understood)
    # Réponse "À propos" depuis la base pour toute question sur AGUIPEX (évite actualités hors-sujet)
    if intent == 'aguipex':
        return (get_aguipex_about_full_answer(), understood)

    # Foires : réponse depuis la base (liste des foires publiées)
    if intent == 'foires':
        return (get_foires_full_answer(), understood)

    # Manifestations commerciales : réponse depuis la base
    if intent == 'manifestations':
        return (get_manifestations_full_answer(), understood)

    # Projets, statistiques, entreprises, produits, interprofessions, actualités, données stratégiques : réponse depuis les tables
    if intent == 'projets':
        return (get_projets_full_answer(), understood)
    if intent == 'statistiques':
        return (get_statistiques_full_answer(), understood)
    if intent == 'entreprises':
        return (get_entreprises_full_answer(), understood)
    if intent == 'produits':
        return (get_produits_full_answer(), understood)
    if intent == 'interprofessions':
        return (get_interprofessions_full_answer(), understood)
    if intent == 'actualites':
        return (get_actualites_full_answer(), understood)
    if intent == 'donnees_strategiques':
        return (get_donnees_strategiques_full_answer(), understood)
    if intent == 'faq':
        return (get_faq_full_answer(), understood)

    # (ancien message "consultez la page" supprimé : on renvoie le contenu réel via procedure_export ci-dessus)
    if False:
        return (
            "Les **procédures d'exportation** (café, fonio ou tout autre produit) sont détaillées sur notre page officielle.\n\n"
            "• Consultez la section **Procédure d'exportations** sur la page Exportations : elle décrit les étapes, les exigences et les formalités.\n\n"
            "• Vous y trouverez également le **potentiel d'exportation** et les **infrastructures** liées à l'export.\n\n"
            "Accès direct : menu **Exportations** (en haut de page) ou page **Ressources** > Données stratégiques selon le type d’information recherchée.",
            understood,
        )

    if not search_results:
        return (get_no_answer_contact_message(), understood)

    # Exclure les actualités sauf pour l'intention "actualites" (éviter réponses hors-sujet type news)
    filtered = [r for r in search_results if r.get('source') != 'Actualités' or intent == 'actualites']
    # Ne jamais réinjecter les actualités pour aguipex/equipe : garder filtered tel quel si vide
    if not filtered and search_results and intent not in ('aguipex', 'equipe'):
        filtered = search_results

    # Réponse centrée sur le contenu : explication claire, pas seulement "où trouver"
    parts = []
    seen_urls = set()
    for r in filtered[:5]:
        if r['url'] in seen_urls:
            continue
        seen_urls.add(r['url'])
        title = html.unescape(str(r.get('title') or 'Ressource'))
        snippet = html.unescape(str(r.get('snippet') or '')).strip()
        if snippet:
            parts.append(f"**{title}**\n{snippet[:400]}{'...' if len(snippet) > 400 else ''}")
        else:
            parts.append(f"**{title}** — section {r.get('source', '')}.")
    if parts:
        parts.append("\nPour plus de détails, consultez le menu **Ressources** sur notre site.")
        return ("\n\n".join(parts), understood)
    # Aucun résultat après filtrage : inviter à contacter le service de communication
    return (get_no_answer_contact_message(), understood)


def generate_session_id() -> str:
    """Génère un identifiant unique de session."""
    return uuid.uuid4().hex
