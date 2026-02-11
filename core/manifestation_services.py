"""
Services métier pour les Manifestations commerciales.

Règles :
- Postulation : étape A_POSTULER, statut_metier REFUS, statut_back_office BROUILLON.
- ACCEPTER : passage à l'étape suivante, statut_metier ACCEPTE, notification "Votre candidature a été validée avec succès".
- REFUSER : reste à l'étape, statut_metier REFUS, notification "Votre candidature a été refusée".
- Traçabilité : decision_admin, date_transition, admin_responsable.
"""
from django.utils import timezone

from .models import (
    CandidatureManifestation,
    CandidatureEtapeHistorique,
    CandidatureDecision,
    EtapeManifestation,
)


class TransitionCandidatureError(Exception):
    """Erreur métier lors d'une tentative de transition."""
    pass


def _notifier_entreprise(candidature, accepte: bool):
    """
    Envoie une notification à l'entreprise (email ou message).
    À compléter selon l'infra (email, in-app, etc.).
    """
    # Placeholder : en production, envoyer un email à candidature.email_contact
    # ou créer un enregistrement Notification.
    pass


def transition_candidature(candidature: CandidatureManifestation, decision: str, user=None):
    """
    Applique la décision admin (ACCEPTER ou REFUSER).

    - ACCEPTER : étape suivante, statut_metier = ACCEPTE, notification de validation.
    - REFUSER : reste à l'étape, statut_metier = REFUS, notification de refus.
    Enregistre la décision (decision_admin, date_transition, admin_responsable).
    """
    if decision not in ('accepter', 'refuser'):
        raise TransitionCandidatureError("La décision doit être 'accepter' ou 'refuser'.")

    etape_actuelle = candidature.etape_actuelle
    if not etape_actuelle or etape_actuelle.manifestation_id != candidature.manifestation_id:
        raise TransitionCandidatureError("La candidature doit avoir une étape actuelle de sa manifestation.")

    # Traçabilité : decision_admin, date_transition, admin_responsable
    CandidatureDecision.objects.create(
        candidature=candidature,
        decision_admin=decision,
        etape=etape_actuelle,
        admin_responsable=user,
    )

    if decision == 'refuser':
        CandidatureManifestation.objects.filter(pk=candidature.pk).update(
            statut_metier='refus',
            updated_at=timezone.now(),
        )
        candidature.refresh_from_db()
        _notifier_entreprise(candidature, accepte=False)
        return

    # ACCEPTER : passage à l'étape suivante
    ordre_actuel = etape_actuelle.ordre
    if ordre_actuel >= 4:
        raise TransitionCandidatureError("La candidature est déjà à l'étape finale. Aucune transition possible.")

    prochaine_etape = EtapeManifestation.objects.filter(
        manifestation_id=candidature.manifestation_id,
        ordre=ordre_actuel + 1,
        is_deleted=False,
    ).first()
    if not prochaine_etape:
        raise TransitionCandidatureError("Étape suivante introuvable pour cette manifestation.")

    # Pour passer à l'étape suivante (ex. 2 → 3 ou 3 → 4), la candidature doit être publiée (traçabilité)
    if candidature.statut_back_office != 'publie':
        raise TransitionCandidatureError(
            "La candidature doit être publiée (statut back office « Publié ») avant de pouvoir passer à l'étape suivante. "
            "Passez le statut back office à « Publié » puis réessayez."
        )

    now = timezone.now()

    # Garantir la traçabilité : si à l'étape N, toutes les étapes 2..N-1 doivent avoir une entrée dans l'historique
    _ensure_historique_chain(candidature, ordre_actuel, now)

    # Fermer toutes les entrées d'historique de l'étape actuelle qui n'ont pas encore de date_sortie
    # Cela garantit que la trace de l'étape précédente est conservée avec sa date de sortie
    historique_etape_actuelle = CandidatureEtapeHistorique.objects.filter(
        candidature=candidature,
        etape=etape_actuelle,
        date_sortie__isnull=True,
    )
    historique_etape_actuelle.update(date_sortie=now)

    # Mettre à jour la candidature pour passer à l'étape suivante
    CandidatureManifestation.objects.filter(pk=candidature.pk).update(
        etape_actuelle=prochaine_etape,
        statut_metier='accepte',
        updated_at=now,
    )
    candidature.refresh_from_db()

    # Créer une nouvelle entrée d'historique pour la nouvelle étape
    # Cette entrée aura date_entree = now et date_sortie = NULL (elle sera fermée lors de la prochaine transition)
    CandidatureEtapeHistorique.objects.create(
        candidature=candidature,
        etape=prochaine_etape,
    )
    _notifier_entreprise(candidature, accepte=True)


def _ensure_historique_chain(candidature: CandidatureManifestation, ordre_actuel: int, now):
    """
    Garantit que pour chaque étape d'ordre 2 à ordre_actuel-1 il existe au moins une entrée
    dans l'historique (traçabilité : être à l'étape 3 implique avoir été en étape 2, etc.).
    Crée les entrées manquantes avec date_entree = date_candidature, date_sortie = now.
    """
    if ordre_actuel <= 2:
        return
    etapes_manifestation = EtapeManifestation.objects.filter(
        manifestation_id=candidature.manifestation_id,
        ordre__gte=2,
        ordre__lt=ordre_actuel,
        is_deleted=False,
    ).order_by('ordre')
    date_entree_fallback = candidature.date_candidature or now
    for etape in etapes_manifestation:
        if not CandidatureEtapeHistorique.objects.filter(
            candidature=candidature,
            etape=etape,
        ).exists():
            obj = CandidatureEtapeHistorique.objects.create(
                candidature=candidature,
                etape=etape,
            )
            obj.date_entree = date_entree_fallback
            obj.date_sortie = now
            obj.save(update_fields=['date_entree', 'date_sortie'])
