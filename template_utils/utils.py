"""
Utility functions for working with templates and for writing custom
template tags.

"""

from django import template


def resolve_variable_or_literal(path, context):
    """
    Given a string and a template context, tries to return the most
    appropriate resolution of that string for that context.

    Tries the following steps, in order:

        1. Call ``template.resolve_variable``; if it succeeds, return
           that value.

        2. Check to see if the string is numeric; if so, return it
           converted to an ``int``.

        3. If both of the above fail, return the string as-is.
    
    """
    try:
        result = template.resolve_variable(path, context)
    except template.VariableDoesNotExist:
        if path.isdigit():
            result = int(path)
        else:
            result = path
    return result
