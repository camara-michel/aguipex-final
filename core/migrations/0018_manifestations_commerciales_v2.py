# Nouveau système Manifestations Commerciales (étapes avec date_debut/date_fin, traçabilité)

import ckeditor.fields
import django.core.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0017_suppression_manifestations_anciennes'),
    ]

    operations = [
        # Les tables existent déjà en base (créées par migration 0015), donc on met à jour uniquement l'état Django
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='ManifestationCommerciale',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('titre', models.CharField(max_length=255, verbose_name='Titre')),
                        ('slug', models.SlugField(blank=True, max_length=280, null=True)),
                        ('description', ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Description')),
                        ('statut_global', models.CharField(choices=[('bientot_prevu', 'Bientôt prévu'), ('a_postuler', 'À postuler'), ('selection_terminee', 'Sélection terminée'), ('manifestation_terminee', 'Manifestation terminée')], default='bientot_prevu', max_length=30, verbose_name='Statut global')),
                        ('statut_publication', models.CharField(choices=[('brouillon', 'Brouillon'), ('publier', 'Publier')], default='brouillon', max_length=10, verbose_name='Publication (Front Office)')),
                        ('date_debut', models.DateField(blank=True, null=True, verbose_name='Date de début')),
                        ('date_fin', models.DateField(blank=True, null=True, verbose_name='Date de fin')),
                        ('lieu', models.CharField(blank=True, max_length=200, null=True, verbose_name='Lieu')),
                        ('pays', models.CharField(blank=True, max_length=100, null=True, verbose_name='Pays')),
                        ('is_deleted', models.BooleanField(default=False, verbose_name='Est supprimé')),
                        ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                        ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                    ],
                    options={
                        'verbose_name': 'Manifestation commerciale',
                        'verbose_name_plural': 'Manifestations commerciales',
                        'ordering': ['-date_debut', '-created_at'],
                    },
                ),
                migrations.CreateModel(
                    name='EtapeManifestation',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('ordre', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)], verbose_name='Ordre (1 à 4)')),
                        ('titre', models.CharField(max_length=200, verbose_name="Titre de l'étape")),
                        ('description', ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Description')),
                        ('date_debut', models.DateField(blank=True, null=True, verbose_name='Date de début')),
                        ('date_fin', models.DateField(blank=True, null=True, verbose_name='Date de fin')),
                        ('is_deleted', models.BooleanField(default=False, verbose_name='Est supprimé')),
                        ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                        ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                        ('manifestation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='etapes', to='core.manifestationcommerciale', verbose_name='Manifestation')),
                    ],
                    options={
                        'verbose_name': 'Étape de manifestation',
                        'verbose_name_plural': 'Étapes de manifestation',
                        'ordering': ['manifestation', 'ordre'],
                        'unique_together': {('manifestation', 'ordre')},
                    },
                ),
                migrations.CreateModel(
                    name='CandidatureManifestation',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('nom_entreprise', models.CharField(blank=True, max_length=200, null=True, verbose_name="Nom de l'entreprise")),
                        ('email_contact', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email du contact')),
                        ('telephone_contact', models.CharField(blank=True, max_length=30, null=True, verbose_name='Téléphone')),
                        ('message', models.TextField(blank=True, null=True, verbose_name='Message')),
                        ('statut_metier', models.CharField(choices=[('refus', 'Refus'), ('accepte', 'Accepté')], default='refus', max_length=20, verbose_name='Statut métier')),
                        ('statut_back_office', models.CharField(choices=[('brouillon', 'Brouillon'), ('publie', 'Publié')], default='brouillon', max_length=10, verbose_name='Statut back office')),
                        ('date_candidature', models.DateTimeField(auto_now_add=True, verbose_name='Date de candidature')),
                        ('is_deleted', models.BooleanField(default=False, verbose_name='Est supprimé')),
                        ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                        ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                        ('entreprise', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='candidatures_manifestation', to='core.entreprise', verbose_name='Entreprise')),
                        ('etape_actuelle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='candidatures_etape', to='core.etapemanifestation', verbose_name='Étape actuelle')),
                        ('manifestation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='candidatures', to='core.manifestationcommerciale', verbose_name='Manifestation')),
                    ],
                    options={
                        'verbose_name': 'Candidature à une manifestation',
                        'verbose_name_plural': 'Candidatures aux manifestations',
                        'ordering': ['manifestation', '-date_candidature'],
                    },
                ),
                migrations.CreateModel(
                    name='CandidatureEtapeHistorique',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('date_entree', models.DateTimeField(auto_now_add=True, verbose_name="Date d'entrée à l'étape")),
                        ('date_sortie', models.DateTimeField(blank=True, null=True, verbose_name="Date de sortie de l'étape")),
                        ('candidature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historique_etapes', to='core.candidaturemanifestation', verbose_name='Candidature')),
                        ('etape', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historique_candidatures', to='core.etapemanifestation', verbose_name='Étape')),
                    ],
                    options={
                        'verbose_name': 'Historique étape candidature',
                        'verbose_name_plural': 'Historiques étapes candidatures',
                        'ordering': ['candidature', 'date_entree'],
                    },
                ),
                migrations.CreateModel(
                    name='CandidatureDecision',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('decision_admin', models.CharField(choices=[('accepter', 'Accepter'), ('refuser', 'Refuser')], max_length=10, verbose_name='Décision admin')),
                        ('date_transition', models.DateTimeField(auto_now_add=True, verbose_name='Date de transition')),
                        ('candidature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='decisions', to='core.candidaturemanifestation', verbose_name='Candidature')),
                        ('admin_responsable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='decisions_candidature', to=settings.AUTH_USER_MODEL, verbose_name='Admin responsable')),
                        ('etape', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='decisions_candidatures', to='core.etapemanifestation', verbose_name='Étape au moment de la décision')),
                    ],
                    options={
                        'verbose_name': 'Décision candidature',
                        'verbose_name_plural': 'Décisions candidatures',
                        'ordering': ['-date_transition'],
                    },
                ),
            ],
            database_operations=[],
        ),
    ]
