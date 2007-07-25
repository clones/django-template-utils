"""
Template tags which can do retrieval of content from any model.

"""


from django import template
from django.conf import settings
from django.db.models import get_model


class GenericContentNode(template.Node):
    """
    Base Node class for retrieving objects from any model.

    By itself, this class will retrieve a number of objects from a
    particular model (specified by an "app_name.model_name" string)
    and store them in a specified context variable (these are the
    ``num``, ``model`` and ``varname`` arguments to the constructor,
    respectively), but is also intended to be subclassed for
    customization.

    There are two ways to add extra bits to the eventual database lookup:

    1. Add the setting ``GENERIC_CONTENT_LOOKUP_KWARGS`` to your
       settings file; this should be a dictionary whose keys are
       "app_name.model_name" strings correponding to models, and whose
       values are dictionaries of keyword arguments which will be
       passed to ``filter()``.

    2. Subclass and override ``_get_query_set``; all that's expected
       is that it will return a ``QuerySet`` or ``None``; if it
       returns a ``QuerySet``, that will be used to get the object(s)
       to add to the template context. The default ``QuerySet`` for
       the specified model (filtered as described above) will be
       available as ``self.query_set`` if you want to work with it.
    
    """
    def __init__(self, model, num, varname):
        self.model, self.num, self.varname = model, int(num), varname
        lookup_dict = getattr(settings, 'GENERIC_CONTENT_LOOKUP_KWARGS', {})
        model = get_model(*self.model.split('.'))
        lookup_kwargs = lookup_dict.get(self.model, {})
        if model is not None:
            self.query_set = model._default_manager.filter(**lookup_kwargs)
        else:
            self.query_set = model
        
    def _get_query_set(self):
        return self.query_set
    
    def render(self, context):
        query_set = self._get_query_set()
        if query_set is not None:
            if self.num == 1:
                context[self.varname] = query_set[0]
            else:
                context[self.varname] = list(query_set[:self.num])
        return ''


class RandomObjectsNode(GenericContentNode):
    """
    A subclass of ``GenericContentNode`` which overrides
    ``_get_query_set`` to apply random ordering.
    
    """
    def _get_query_set(self):
        if self.query_set is not None:
            self.query_set = self.query_set.order_by('?')
        return self.query_set


class RetrieveObjectNode(template.Node):
    def __init__(self, model, pk, varname):
        self.model, self.pk, self.varname = model, pk, varname
    
    def render(self, context):
        # PK lookup assumes we know exactly which object we want,
        # so the extra settings-based filtering applied in the other
        # tags is not used here.
        model = get_model(*self.model.split('.'))
        if model is not None:
            try:
                context[self.varname] = model._default_manager.get(pk=self.pk)
            except (AssertionError, model.DoesNotExist): # Bad lookup: no matching object or too many matching objects.
                pass
        return ''


def do_latest_object(parser, token):
    """
    Retrieves the latest object from a given model, in that model's
    default ordering, and stores it in a context variable.
    
    Syntax::
    
        {% get_latest_object [app_name].[model_name] as [varname] %}
    
    Example::
    
        {% get_latest_object comments.freecomment as latest_comment %}
    
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes three arguments" % bits[0])
    if bits [2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return GenericContentNode(bits[1], 1, bits[3])


def do_latest_objects(parser, token):
    """
    Retrieves the latest ``num`` objects from a given model, in that
    model's default ordering, and stores them in a context variable.
    
    Syntax::
    
        {% get_latest_objects [app_name].[model_name] [num] as [varname] %}
    
    Example::
    
        {% get_latest_objects comments.freecomment 5 as latest_comments %}
    
    """
    bits = token.contents.split()
    if len(bits) != 5:
        raise template.TemplateSyntaxError("'%s' tag takes four arguments" % bits[0])
    if bits [3] != 'as':
        raise template.TemplateSyntaxError("third argument to '%s' tag must be 'as'" % bits[0])
    return GenericContentNode(bits[1], bits[2], bits[4])

def do_random_object(parser, token):
    """
    Retrieves a random object from a given model, and stores it in a
    context variable.
    
    Syntax::
    
        {% get_random_object [app_name].[model_name] as [varname] %}
    
    Example::
    
        {% get_random_object comments.freecomment as random_comment %}
    
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes three arguments" % bits[0])
    if bits [2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return RandomObjectsNode(bits[1], 1, bits[3])


def do_random_objects(parser, token):
    """
    Retrieves ``num`` random objects from a given model, and stores
    them in a context variable.
    
    Syntax::
    
        {% get_random_objects [app_name].[model_name] [num] as [varname] %}
    
    Example::
    
        {% get_random_objects comments.freecomment 5 as random_comments %}
    
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
    
        {% retrieve_object flatpages.flatpage 12 as my_flat_page %}
    
    """
    bits = token.contents.split()
    if len(bits) != 5:
        raise template.TemplateSyntaxError("'%s' tag takes four arguments" % bits[0])
    if bits[3] != 'as':
        raise template.TemplateSyntaxError("third argument to '%s' tag must be 'as'" % bits[0])
    return RetrieveObjectNode(bits[1], bits[2], bits[4])

register = template.Library()
register.tag('get_latest_object', do_latest_object)
register.tag('get_latest_objects', do_latest_objects)
register.tag('get_random_object', do_random_object)
register.tag('get_random_objects', do_random_objects)
register.tag('retrieve_object', do_retrieve_object)
