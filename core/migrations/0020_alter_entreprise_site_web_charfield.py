# Alter Entreprise.site_web: URLField -> CharField pour accepter toute saisie

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_chatbot_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entreprise',
            name='site_web',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Site web'),
        ),
    ]
