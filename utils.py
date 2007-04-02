from django.conf import settings

def apply_markup_filter(text, **extra_kwargs):
    """
    Applies a text-to-HTML conversion function to a piece of text and
    returns the generated HTML.
    
    The function to use is derived from the value of the setting
    ``MARKUP_FILTER``, which should be a 2-tuple:
    
        * The first element should be the name of a markup filter --
          e.g.,"markdown" -- to apply. If no markup filter is desired,
          set this to None.
    
        * The second element should be a dictionary of keyword
          arguments which will be passed to the markup function. If no
          extra arguments are desired, set this to an empty
          dictionary; some arguments may still be inferred as needed,
          however.
    
    So, for example, to use Markdown with safe mode turned on (safe
    mode removes raw HTML), put this in your settings file::
    
        MARKUP_FILTER = ('markdown', { 'safe_mode': True })
    
    Or, to use no filtering at all::
    
        MARKUP_FILTER = (None, {})
    
    If you want to supply additional keyword arguments only on one
    specific use of this function, include them in the call and they
    will be passed along. So, for example, if you had the following in
    your settings file::
    
        MARKUP_FILTER = ('markdown', {})
    
    and wanted to enable safe mode for one specific call, you could
    pass that in::
    
        safe_text = apply_markup_filter(some_text, safe_mode=True)
    
    The 'safe_mode=True' would be passed on to Markdown.
    
    Currently supports Textile, Markdown and reStructuredText, using
    names identical to the template filters found in
    ``django.contrib.markup``, and 'linebreaks', which simply applies
    Django's 'linebreaks' filter and leaves all other text unchanged.
    
    """
    markup_func, markup_kwargs = settings.MARKUP_FILTER
    if markup_func is None: # No processing is needed.
        return text
    
    markup_kwargs.update(**extra_kwargs)
    
    if markup_func not in ('textile', 'markdown', 'restructuredtext', 'linebreaks'):
        raise ValueError("'%s' is not a valid value for the first element of MARKUP_FILTER; acceptable values are 'textile', 'markdown', 'restructuredtext', 'linebreaks', and None" % markup_func)
    
    if markup_func == 'textile':
        import textile
        if 'encoding' not in markup_kwargs:
            markup_kwargs.update(encoding=settings.DEFAULT_CHARSET)
        if 'output' not in markup_kwargs:
            markup_kwargs.update(output=settings.DEFAULT_CHARSET)
        return textile.textile(text, **markup_kwargs)
    
    elif markup_func == 'markdown':
        import markdown
        return markdown.markdown(text, **markup_kwargs)
    
    elif markup_func == 'restructuredtext':
        from docutils import core
        if 'settings_overrides' not in markup_kwargs:
            markup_kwargs.update(settings_overrides=getattr(settings, "RESTRUCTUREDTEXT_FILTER_SETTINGS", {}))
        if 'writer_name' not in markup_kwargs:
            markup_kwargs.update(writer_name='html4css1')
        parts = core.publish_parts(source=text, **markup_kwargs)
        return parts['fragment']
    
    elif markup_func == 'linebreaks':
        from django.utils.html import linebreaks
        return linebreaks(text)
