"""
Utilities for text-to-HTML conversion.

"""

from django.conf import settings

def textile(text, **kwargs):
    import textile
    if 'encoding' not in kwargs:
        kwargs.update(encoding=settings.DEFAULT_CHARSET)
    if 'output' not in kwargs:
        kwargs.update(output=settings.DEFAULT_CHARSET)
    return textile.textile(text, **kwargs)

def markdown(text, **kwargs):
    import markdown
    return markdown.markdown(text, **kwargs)

def restructuredtext(text, **kwargs):
    from docutils import core
    if 'settings_overrides' not in kwargs:
        kwargs.update(settings_overrides=getattr(settings,
                                                 "RESTRUCTUREDTEXT_FILTER_SETTINGS",
                                                 {}))
    parts = core.publish_parts(source=text,
                               writer_name='html4css1',
                               **kwargs)
    return parts['fragment']

DEFAULT_MARKUP_FILTERS = {
    'textile': textile,
    'markdown': markdown,
    'restructuredtext': restructuredtext
    }

class MarkupFormatter(object):
    """
    Generic markup formatter which can handle multiple text-to-HTML
    conversion systems.

    Overview
    --------
    
    Any programmatic method of converting plain text to HTML can be
    supported by registering a new "filter"; the filter should be a
    function which accepts a string as its first positional argument
    and optional extra keyword arguments (so the filter function must
    accept ``**kwargs``), and returns the string converted to
    HTML. The default filter set includes Markdown, reStructuredText
    and Textile, using the same names as the template filters in
    ``django.contrib.markup``.
    
    To register a new filter, call the ``register`` method and pass it
    a name to use for the filter, and the filter function. For
    example::
    
        formatter = MarkupFormatter()
        formatter.register('my_filter', my_filter_func)
    
    Instances are callable, so you can work with them like so::
    
        formatter = MarkupFormatter()
        my_html = formatter(my_string)
    
    The filter to use is determined in either of two ways:

        1. If the keyword argument ``filter_name`` is supplied, it
           will be used as the filter name.
    
        2. Absent an explicit argument, the filter name will be taken
           from the ``MARKUP_FILTER`` setting in your Django settings
           file (see below).
    
    Additionally, arbitrary keyword arguments can be supplied, and
    they will be passed on to the filter function.
    
    The Django setting ``MARKUP_FILTER`` can be used to specify
    default behavior; its value should be a 2-tuple:
    
        * The first element should be the name of a filter.
    
        * The second element should be a dictionary to use as keyword
          arguments for that filter.
    
    So, for example, to have the default behavior apply Markdown with
    safe mode enabled, you would add this to your Django settings
    file::
    
        MARKUP_FILTER = ('markdown', { 'safe_mode': True }
    
    The filter named in this setting does not have to be from the
    default set; as long as you register a filter of that name before
    trying to use the formatter, it will work.
    
    To have the default behavior apply no conversion whatsoever, set
    ``MARKUP_FILTER`` like so::
    
        MARKUP_FILTER = (None, {})
    
    When the ``filter_name`` keyword argument is supplied, the
    ``MARKUP_FILTER`` setting is ignored entirely -- neither a filter
    name nor any keyword arguments will be read from it.
    
    
    Examples
    --------
    
    Using the default behavior, with the filter name and arguments
    taken from the ``MARKUP_FILTER`` setting::
    
        formatter = MarkupFormatter()
        my_string = 'Lorem ipsum dolor sit amet.\n\nConsectetuer adipiscing elit.'
        my_html = formatter(my_string)
    
    Explicitly naming the filter to use::
    
        my_html = formatter(my_string, filter_name='markdown')
    
    Passing keyword arguments::
    
        my_html = formatter(my_string, filter_name='markdown', safe_mode=True)
    
    Perform no conversion (return the text as-is)::
    
        my_html = formatter(my_string, filter_name=None)
    
    """
    def __init__(self):
        self.filters = {}
        for filter_name, filter_func in DEFAULT_MARKUP_FILTERS.iteritems():
            self.register(filter_name, filter_func)
    
    def register(self, filter_name, filter_func):
        """
        Registers a new filter for use.
        
        """
        self.filters[filter_name] = filter_func
    
    def __call__(self, text, **kwargs):
        if 'filter_name' in kwargs:
            filter_name = kwargs['filter_name']
            filter_kwargs = {}
        else:
            filter_name, filter_kwargs = settings.MARKUP_FILTER
        if filter_name is None:
            return text
        if filter_name not in self.filters:
            raise ValueError("'%s' is not a registered markup filter. Registered filters are: %s." % (filter_name,
                                                                                                       ', '.join(self.filters.iterkeys())))
        filter_func = self.filters[filter_name]
        filter_kwargs.update(**kwargs)
        return filter_func(text, **filter_kwargs)

markup_filter = MarkupFormatter()
