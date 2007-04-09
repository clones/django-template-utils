from django import template


class ComparisonNode(template.Node):
    def __init__(self, var1, var2, comparison, nodelist_true, nodelist_false):
        self.var1, self.var2 = var1, var2
        self.comparison = comparison
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
    
    def render(self, context):
        # Resolving the variables to compare is a bit verbose,
        # but it has to be for this to work.
        try:
            # First, try to resolve as a template variable.
            var1 = template.resolve_variable(self.var1, context)
        except template.VariableDoesNotExist:
            # Maybe it's a number.
            if self.var1.isdigit():
                var1 = int(self.var1)
            # Not a variable or a number; keep it as-is.
            else:
                var1 = self.var1
        # And now we do it all over again for the second one.
        try:
            var2 = template.resolve_variable(self.var2, context)
        except template.VariableDoesNotExist:
            if self.var2.isdigit():
                var2 = int(self.var2)
            else:
                var2 = self.var2
        comparison = cmp(var1, var2)
        result_dict = {
            'less': comparison < 0,
            'less_or_equal': comparison <= 0,
            'greater_or_equal': comparison >= 0,
            'greater': comparison > 0
            }
        if result_dict[self.comparison]:
            return self.nodelist_true.render(context)
        else:
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
