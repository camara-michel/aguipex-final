# Chatbot AGUIPEX - Sessions, messages, mots-clés (Word Cloud)

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_manifestations_commerciales_v2'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(db_index=True, max_length=64, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Session chatbot',
                'verbose_name_plural': 'Sessions chatbot',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('user', 'Utilisateur'), ('bot', 'Bot')], max_length=10)),
                ('content', models.TextField()),
                ('understood_as', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='core.chatsession')),
            ],
            options={
                'verbose_name': 'Message chatbot',
                'verbose_name_plural': 'Messages chatbot',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='ExtractedKeyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(db_index=True, max_length=100)),
                ('weight', models.PositiveIntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='keywords', to='core.chatmessage')),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='keywords', to='core.chatsession')),
            ],
            options={
                'verbose_name': 'Mot-clé extrait (Word Cloud)',
                'verbose_name_plural': 'Mots-clés extraits (Word Cloud)',
                'ordering': ['-weight', '-created_at'],
            },
        ),
    ]
