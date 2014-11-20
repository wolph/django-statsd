from __future__ import absolute_import
import django_statsd

try:
    from coffin.template import loader
    if not hasattr(loader, 'statsd_patched'):
        loader.statsd_patched = True
        loader.render_to_string = django_statsd.named_wrapper(
            'render_jinja', loader.render_to_string)

except ImportError:
    pass

try:
    from django.template import loader
    if not hasattr(loader, 'statsd_patched'):
        loader.statsd_patched = True
        loader.render_to_string = django_statsd.named_wrapper(
            'render_django', loader.render_to_string)

except ImportError:
    pass
