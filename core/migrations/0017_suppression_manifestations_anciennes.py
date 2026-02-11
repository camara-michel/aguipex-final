# Migration de suppression : retrait complet des modèles Manifestations Commerciales
# pour repartir sur une structure propre (voir 0018 pour les nouveaux modèles).
# Note: Les tables peuvent ne pas exister en base (migration 0016 utilisait SeparateDatabaseAndState),
# donc on met à jour uniquement l'état Django sans opérations DB.

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0016_candidature_historique_decision'),
    ]

    operations = [
        # Les tables peuvent ne pas exister en base, donc on met à jour uniquement l'état Django
        migrations.SeparateDatabaseAndState(
            state_operations=[
        migrations.DeleteModel(name='CandidatureDecision'),
        migrations.DeleteModel(name='CandidatureEtapeHistorique'),
        migrations.DeleteModel(name='CandidatureManifestation'),
        migrations.DeleteModel(name='EtapeManifestation'),
        migrations.DeleteModel(name='ManifestationCommerciale'),
            ],
            database_operations=[],
        ),
    ]
