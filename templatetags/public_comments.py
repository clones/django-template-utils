"""
Template tags designed to work with applications which use comment
moderation.

"""

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import get_model
from django.template import Library
from django.contrib.comments.templatetags.comments import CommentListNode
from django.contrib.contenttypes.models import ContentType


class DoPublicCommentList(object):
    """
    Retrieves comments for a particular object and stores them in a
    context variable.

    The difference between this tag and Django's built-in comment list
    tags is that this tag will only return comments with
    ``is_public=True``. If your application uses any sort of comment
    moderation which sets ``is_public=False``, you'll probably want to
    use this tag, as it makes the template logic simpler by only
    returning approved comments.
    
    Syntax::
    
        {% get_public_comment_list for [app_name].[model_name] [object_id] as [varname] %}
    
    or::
    
        {% get_public_free_comment_list for [app_name].[model_name] [object_id] as [varname] %}
    
    When called using ``get_public_comment_list``, this tag retrieves
    instances of ``Comment`` (e.g., comments which require
    registration). When called using ``get_public_free_comment_list``,
    this tag retrieves instances of ``FreeComment`` (comments which do
    not require registration).
    
    To retrieve comments in reverse order (e.g., oldest comments
    first), pass 'reversed' as an extra argument after ``varname``.
    
    So, for example, to retrieve registered comments for a flatpage
    with ``id`` 12, use like this::
    
        {% get_public_comment_list for flatpages.FlatPage 12 as comment_list %}
    
    To retrieve unregistered comments for the same object::
    
        {% get_public_free_comment_list for flatpages.FlatPage 12 as comment_list %}
    
    To retrieve in reverse order (oldest comments first)::
    
        {% get_public_free_comment_list for flatpages.FlatPage 12 as comment_list reversed %}
        
    """
    def __init__(self, free):
        self.free = free

    def __call__(self, parser, token):
        bits = token.contents.split()
        if len(bits) not in (6, 7):
            raise template.TemplateSyntaxError("'%s' tag takes 5 or 6 arguments" % bits[0])
        if bits[1] != 'for':
            raise template.TemplateSyntaxError("first argument to '%s' tag must be 'for'" % bits[0])
        try:
            app_name, model_name = bits[2].split('.')
        except ValueError:
            raise template.TemplateSyntaxError("second argument to '%s' tag must be in the form 'app_name.model_name'" % bits[0])
        model = get_model(app_name, model_name)
        if model is None:
            raise template.TemplateSyntaxError("'%s' tag got invalid model '%s.%s'" % (bits[0], app_name, model_name))
        content_type = ContentType.objects.get_for_model(model)
        var_name, object_id = None, None
        if tokens[3].isdigit():
            object_id = bits[3]
            try:
                content_type.get_object_for_this_type(pk=obj_id)
            except ObjectDoesNotExist:
                raise template.TemplateSyntaxError("'%s' tag got reference to %s object with id %s, which doesn't exist" % (bits[0], content_type.name, object_id))
        else:
            var_name = bits[3]
        if bits[4] != 'as':
            raise template.TemplateSyntaxError("fourth argument to '%s' tag must be 'as'" % bits[0])
        if len(bits) == 7:
            if bits[6] != 'reversed':
                raise template.TemplateSyntaxError("sixth argument to '%s' tag, if given, must be 'reversed'" % bits[0])
            ordering = '-'
        else:
            ordering = ''
        return CommentListNode(app_name, model_name, var_name, object_id, bits[5], self.free, ordering, extra_kwargs={ 'is_public__exact': True })

register = template.Library()
register.tag('get_public_comment_list', DoPublicCommentList(False))
register.tag('get_public_free_comment_list', DoPublicCommentList(True))
