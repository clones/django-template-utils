from django.template import Library
from template_utils.utils import apply_markup_filter

def apply_markup(value):
    """
    Applies text-to-HTML conversion.

    """
    return apply_markup_filter(value)

register = Library()
register.filter(apply_markup)
