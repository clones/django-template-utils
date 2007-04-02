"""
A filter which can perform many types of text-to-HTML conversion.

"""

from django.template import Library
from template_utils.markup import markup_filter

def apply_markup(value, arg=None):
    """
    Applies text-to-HTML conversion.

    Takes an optional argument to specify the name of a filter to use.

    """
    if arg is not None:
        return markup_filter(value, filter_name=arg)
    return markup_filter(value)

register = Library()
register.filter(apply_markup)
