# Generated manually for Visiteur model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_produit_pour_site'),
    ]

    operations = [
        migrations.CreateModel(
            name='Visiteur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_complet', models.CharField(max_length=200, verbose_name='Nom complet')),
                ('email', models.EmailField(max_length=254, verbose_name='Adresse e-mail')),
                ('pays', models.CharField(max_length=100, verbose_name='Pays')),
                ('ville_residence', models.CharField(max_length=100, verbose_name='Ville de résidence')),
                ('telephone', models.CharField(max_length=20, verbose_name='Numéro de téléphone')),
                ('date_visite', models.DateTimeField(auto_now_add=True, verbose_name='Date de visite')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='Adresse IP')),
            ],
            options={
                'verbose_name': 'Visiteur',
                'verbose_name_plural': 'Visiteurs',
                'ordering': ['-date_visite'],
            },
        ),
    ]
