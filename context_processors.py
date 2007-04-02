from django.conf import settings

def media(request):
    """
    Adds the values of the settings ``ADMIN_MEDIA_PREFIX`` and
    ``MEDIA_URL`` to a ``RequestContext``.
    
    """
    return { 'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX,
             'MEDIA_URL': settings.MEDIA_URL }

def settings_processor(settings_list):
    """
    Generates and returns a context-processor function which will
    read the values of the settings specified in ``settings_list``
    and return them in each ``RequestContext`` in which it is applied.
    
    Example::
    
        my_settings_processor = settings_processor(['INTERNAL_IPS', 'SITE_ID'])
    
    The function ``my_settings_processor`` would then be a valid context
    processor which would return the values of the settings ``INTERNAL_IPS``
    and ``SITE_ID`` in each ``RequestContext`` in which it was applied.
    
    """
    def _processor(request):
        from django.conf import settings
        settings_dict = {}
        for setting_name in settings_list:
            settings_dict[setting_name] = getattr(settings, setting_name)
        return settings_dict
    return _processor
