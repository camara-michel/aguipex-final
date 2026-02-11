"""
Signals pour le module Manifestations commerciales.
- Création automatique des 4 étapes FIXES à la création d'une manifestation.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ManifestationCommerciale, EtapeManifestation, ETAPES_MANIFESTATION_FIXES


@receiver(post_save, sender=ManifestationCommerciale)
def creer_etapes_manifestation(sender, instance, created, **kwargs):
    """
    À la création d'une manifestation, créer exactement 4 étapes (ordre 1 à 4)
    avec les libellés fixes. L'admin ne peut ni les créer, ni les supprimer, ni changer leur ordre.
    """
    if not created:
        return
    for ordre, titre in ETAPES_MANIFESTATION_FIXES:
        EtapeManifestation.objects.get_or_create(
            manifestation=instance,
            ordre=ordre,
            defaults={
                'titre': titre,
                'date_debut': instance.date_debut,
                'date_fin': instance.date_fin,
            }
        )
