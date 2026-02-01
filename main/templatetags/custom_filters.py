# main/templatetags/custom_filters.py
from django import template
from django.forms import Widget

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplie la valeur par l'argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def sub(value, arg):
    """Soustrait l'argument de la valeur"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def subtract(value, arg):
    """Alias pour sub - Soustrait l'argument de la valeur"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def add_class(field, css_class):
    """Ajoute une classe CSS à un champ de formulaire"""
    try:
        if hasattr(field, 'as_widget'):
            # C'est un champ de formulaire Django
            return field.as_widget(attrs={'class': css_class})
        elif hasattr(field, 'field'):
            # C'est un BoundField
            existing_classes = field.field.widget.attrs.get('class', '')
            if existing_classes:
                new_classes = f"{existing_classes} {css_class}"
            else:
                new_classes = css_class
            
            field.field.widget.attrs['class'] = new_classes
            return field
        else:
            return field
    except (AttributeError, TypeError):
        return field

@register.filter
def add_css(field, css_class):
    """Alias pour add_class"""
    return add_class(field, css_class)

@register.filter
def widget_type(field):
    """Retourne le type de widget d'un champ de formulaire"""
    try:
        return field.field.widget.__class__.__name__
    except AttributeError:
        return ''

@register.filter
def field_type(field):
    """Retourne le type d'un champ de formulaire"""
    try:
        return field.field.__class__.__name__
    except AttributeError:
        return ''

@register.filter
def placeholder(field, text):
    """Ajoute un attribut placeholder à un champ de formulaire"""
    try:
        if hasattr(field, 'field'):
            field.field.widget.attrs['placeholder'] = text
            return field
        return field
    except (AttributeError, TypeError):
        return field

@register.filter
def percentage(value, total):
    """Calcule le pourcentage"""
    try:
        if total == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def divide(value, arg):
    """Divise la valeur par l'argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def modulo(value, arg):
    """Retourne le modulo de la valeur par l'argument"""
    try:
        return int(value) % int(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def range_filter(value):
    """Crée une liste de nombres de 0 à value-1"""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)

@register.filter
def format_number(value):
    """Formate un nombre avec des espaces comme séparateurs de milliers"""
    try:
        return "{:,}".format(int(value)).replace(",", " ")
    except (ValueError, TypeError):
        return value

@register.filter
def format_currency(value, currency="FCFA"):
    """Formate un nombre comme une devise"""
    try:
        formatted_number = "{:,.0f}".format(float(value)).replace(",", " ")
        return f"{formatted_number} {currency}"
    except (ValueError, TypeError):
        return f"{value} {currency}"

@register.filter
def truncate_chars(value, length):
    """Tronque une chaîne à une longueur donnée"""
    try:
        length = int(length)
        if len(str(value)) > length:
            return str(value)[:length] + "..."
        return str(value)
    except (ValueError, TypeError):
        return value

@register.filter
def truncate_words_custom(value, length):
    """Tronque une chaîne à un nombre de mots donné"""
    try:
        words = str(value).split()
        length = int(length)
        if len(words) > length:
            return ' '.join(words[:length]) + "..."
        return str(value)
    except (ValueError, TypeError):
        return value

@register.filter
def get_item(dictionary, key):
    """Récupère un élément d'un dictionnaire par sa clé"""
    try:
        return dictionary.get(key, '')
    except (AttributeError, TypeError):
        return ''

@register.filter
def get_attr(obj, attr):
    """Récupère un attribut d'un objet"""
    try:
        return getattr(obj, attr, '')
    except (AttributeError, TypeError):
        return ''

@register.filter
def times(number):
    """Retourne une liste de nombres de 0 à number-1 (pour les boucles)"""
    try:
        return range(int(number))
    except (ValueError, TypeError):
        return range(0)

@register.filter
def to_int(value):
    """Convertit une valeur en entier"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

@register.filter
def to_float(value):
    """Convertit une valeur en float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

@register.filter
def absolute(value):
    """Retourne la valeur absolue"""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return value

@register.filter
def length_is(value, length):
    """Vérifie si la longueur d'une valeur est égale à length"""
    try:
        return len(value) == int(length)
    except (TypeError, ValueError):
        return False

@register.filter
def startswith(value, prefix):
    """Vérifie si une chaîne commence par un préfixe"""
    try:
        return str(value).startswith(str(prefix))
    except (AttributeError, TypeError):
        return False

@register.filter
def endswith(value, suffix):
    """Vérifie si une chaîne se termine par un suffixe"""
    try:
        return str(value).endswith(str(suffix))
    except (AttributeError, TypeError):
        return False

@register.filter
def replace_spaces(value, replacement="_"):
    """Remplace les espaces par un autre caractère"""
    try:
        return str(value).replace(" ", replacement)
    except (AttributeError, TypeError):
        return value

@register.filter
def split_string(value, delimiter):
    """Divise une chaîne selon un délimiteur"""
    try:
        return str(value).split(delimiter)
    except (AttributeError, TypeError):
        return [value]

@register.filter
def join_with(value, separator):
    """Joint les éléments d'une liste avec un séparateur"""
    try:
        return separator.join(str(item) for item in value)
    except (TypeError, AttributeError):
        return value

# Filtres pour les calculs financiers spécifiques
@register.filter
def budget_progress(collected, required):
    """Calcule le pourcentage de progression d'un budget"""
    try:
        if float(required) == 0:
            return 0
        progress = (float(collected) / float(required)) * 100
        return min(progress, 100)  # Cap à 100%
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def remaining_budget(required, collected):
    """Calcule le budget restant à collecter"""
    try:
        remaining = float(required) - float(collected)
        return max(remaining, 0)  # Ne peut pas être négatif
    except (ValueError, TypeError):
        return required

@register.filter
def progress_color(percentage):
    """Retourne une classe CSS selon le pourcentage de progression"""
    try:
        percentage = float(percentage)
        if percentage >= 90:
            return "bg-success"
        elif percentage >= 75:
            return "bg-info"
        elif percentage >= 50:
            return "bg-warning"
        else:
            return "bg-danger"
    except (ValueError, TypeError):
        return "bg-secondary"

# Filtres pour les dates
@register.filter
def days_until(date_value):
    """Calcule le nombre de jours jusqu'à une date"""
    try:
        from django.utils import timezone
        from datetime import datetime
        
        if isinstance(date_value, str):
            date_value = datetime.strptime(date_value, '%Y-%m-%d').date()
        
        today = timezone.now().date()
        delta = date_value - today
        return delta.days
    except (ValueError, TypeError, AttributeError):
        return 0

@register.filter
def is_past_date(date_value):
    """Vérifie si une date est dans le passé"""
    try:
        from django.utils import timezone
        from datetime import datetime
        
        if isinstance(date_value, str):
            date_value = datetime.strptime(date_value, '%Y-%m-%d').date()
        
        today = timezone.now().date()
        return date_value < today
    except (ValueError, TypeError, AttributeError):
        return False

@register.filter
def is_today(date_value):
    """Vérifie si une date est aujourd'hui"""
    try:
        from django.utils import timezone
        from datetime import datetime
        
        if isinstance(date_value, str):
            date_value = datetime.strptime(date_value, '%Y-%m-%d').date()
        
        today = timezone.now().date()
        return date_value == today
    except (ValueError, TypeError, AttributeError):
        return False