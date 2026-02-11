"""
Filtres personnalisés pour améliorer l'affichage des caractères spéciaux et du HTML.
"""
import html
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='unescape_html')
def unescape_html(value):
    """
    Décode les entités HTML (comme &eacute;, &ndash;, &agrave;, etc.) en caractères Unicode.
    Utile pour afficher correctement les caractères spéciaux stockés comme entités HTML.
    """
    if value is None:
        return ''
    if isinstance(value, str):
        # Décoder les entités HTML (décode &eacute; -> é, &agrave; -> à, etc.)
        decoded = html.unescape(value)
        # Décoder aussi les entités numériques si nécessaire
        try:
            # Gérer les entités comme &#233; ou &#xE9;
            import re
            def decode_entity(match):
                entity = match.group(1)
                if entity.startswith('x') or entity.startswith('X'):
                    # Entité hexadécimale
                    return chr(int(entity[1:], 16))
                else:
                    # Entité décimale
                    return chr(int(entity))
            decoded = re.sub(r'&#([0-9A-Fa-fxX]+);', decode_entity, decoded)
        except:
            pass
        return mark_safe(decoded)
    return value


@register.filter(name='clean_html_entities')
def clean_html_entities(value):
    """
    Nettoie et décode les entités HTML tout en préservant le HTML valide.
    """
    if value is None:
        return ''
    if isinstance(value, str):
        # Décoder les entités HTML
        decoded = html.unescape(value)
        return mark_safe(decoded)
    return value

