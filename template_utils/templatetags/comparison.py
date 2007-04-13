"""
Tags for performing basic value comparisons in templates.

"""

from django import template

COMPARISON_DICT = {
    'less': lambda x: x < 0,
    'less_or_equal': lambda x: x <= 0,
    'greater_or_equal': lambda x: x >= 0,
    'greater': lambda x: x > 0,
    }

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


class ComparisonNode(template.Node):
    def __init__(self, var1, var2, comparison, nodelist_true, nodelist_false):
        self.var1, self.var2 = var1, var2
        self.comparison = comparison
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
    
    def render(self, context):
        # The values to compare may have been passed as template
        # variables or as literal values, so resolve them before
        # doing the comparison.
        var1 = resolve_variable_or_literal(self.var1, context)
        var2 = resolve_variable_or_literal(self.var2, context)
        result = cmp(var1, var2)
        if COMPARISON_DICT[self.comparison](result):
            return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)


def do_comparison(parser, token):
    """
    Compares two values.
    
    Syntax::
    
        {% if_[comparison] [var1] [var2] %}
        ...
        {% else %}
        ...
        {% endif_[comparison] %}

    The {% else %} block is optional, and ``var1`` and ``var2`` may be
    variables or literal values.
    
    Supported comparisons are ``less``, ``less_or_equal``, ``greater``
    and ``greater_or_equal``.
    
    Examples::
    
        {% if_less some_object.id 3 %}
        <p>{{ some_object }} has an id less than 3.</p>
        {% endif_less %}
    
        {% if_greater_or_equal forloop.counter 4 %}
        <p>This is at least the fifth time through the loop.</p>
        {% else %}
        <p>This is one of the first four trips through the loop.</p>
        {% endif_greater_or_equal %}
    
    """
    bits = token.contents.split()
    if len(bits) != 3:
        raise template.TemplateSyntaxError("'%s' tag takes two arguments" % bits[0])
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    comparison = bits[0].split('if_')[1]
    return ComparisonNode(bits[1], bits[2], comparison, nodelist_true, nodelist_false)

register = template.Library()
for tag_name in ('if_less', 'if_less_or_equal', 'if_greater_or_equal', 'if_greater'):
    register.tag(tag_name, do_comparison)
