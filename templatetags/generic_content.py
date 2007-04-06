"""
Template tags which can do retrieval of content from any model.

"""

from django import template
from django.db.models import get_model, Manager


class LatestObjectsNode(template.Node):
    def __init__(self, model, num, varname):
        self.model, self.num, self.varname = model, num, varname
    
    def render(self, context):
        model = get_model(*self.model.split('.'))
        if model is not None:
            context[self.varname] = model._default_manager.all()[:int(self.num)]
        return ''


class RandomObjectsNode(template.Node):
    def __init__(self, model, num, varname):
        self.model, self.num, self.varname = model, num, varname
    
    def render(self, context):
        model = get_model(*self.model.split('.'))
        if model is not None:
            context[self.varname] = model._default_manager.order_by('?')[:self.num]
        return ''


class RetrieveObjectNode(template.Node):
    def __init__(self, model, pk, varname):
        self.model, self.pk, self.varname = model, num, varname
    
    def render(self, context):
        model = get_model(*self.model.split('.'))
        if model is not None:
            try:
                context[self.varname] = model._default_manager.get(pk=self.pk)
            except (AssertionError, model.DoesNotExist): # Bad lookup: no matching object or too many matching objects.
                pass
        return ''


def do_latest_objects(parser, token):
    """
    Retrieves the latest ``num`` objects from a given model, in that
    model's default ordering, and stores them in a context variable.
    
    Syntax::
    
        {% get_latest_objects [app_name].[model_name] [num] as [varname] %}
    
    Example::
    
        {% get_latest_objects comments.FreeComment 5 as latest_comments %}
    
    """
    bits = token.contents.split()
    if len(bits) != 5:
        raise template.TemplateSyntaxError("'%s' tag takes four arguments" % bits[0])
    if bits [3] != 'as':
        raise template.TemplateSyntaxError("third argument to '%s' tag must be 'as'" % bits[0])
    return LatestObjectsNode(bits[1], bits[2], bits[4])

def do_random_objects(parser, token):
    """
    Retrieves ``num`` random objects from a given model, and stores
    them in a context variable.
    
    Syntax::
    
        {% get_random_objects [app_name].[model_name] [num] as [varname] %}
    
    Example::
    
        {% get_random_objects comments.FreeComment 5 as random_comments %}
    
    """
    bits = token.contents.split()
    if len(bits) != 5:
        raise template.TemplateSyntaxError("'%s' tag takes four arguments" % bits[0])
    if bits [3] != 'as':
        raise template.TemplateSyntaxError("third argument to '%s' tag must be 'as'" % bits[0])
    return RandomObjectsNode(bits[1], bits[2], bits[4])

def do_retrieve_object(parser, token):
    """
    Retrieves a specific object from a given model by primary-key
    lookup, and stores it in a context variable.
    
    Syntax::
    
        {% retrieve_object [app_name].[model_name] [pk] as [varname] %}
    
    Example::
    
        {% retrieve_object flatpages.FlatPage 12 as my_flat_page %}
    
    """
    bits = token.contents.split()
    if len(bits) != 5:
        raise template.TemplateSyntaxError("'%s' tag takes four arguments" % bits[0])
    if bits[3] != 'as':
        raise template.TemplateSyntaxError("third argument to '%s' tag must be 'as'" % bits[0])
    return RetrieveObjectNode(bits[1], bits[2], bits[4])

register = template.Library()
register.tag('get_latest_objects', do_latest_objects)
register.tag('get_random_objects', do_random_objects)
register.tag('retrieve_object', do_retrieve_object)
