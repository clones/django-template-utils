"""
A filter which can perform many types of text-to-HTML conversion.

"""

from django.template import Library
from template_utils.markup import markup_filter

def apply_markup(value):
    """
    Applies text-to-HTML conversion.

    """
    return markup_filter(value)

register = Library()
register.filter(apply_markup)
