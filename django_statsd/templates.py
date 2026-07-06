"""Time Django template rendering as ``render_django`` metrics."""

from django.template import loader

from django_statsd import middleware

if not hasattr(loader, 'statsd_patched'):
    loader.statsd_patched = True  # type: ignore[attr-defined]
    loader.render_to_string = middleware.named_wrapper(
        'render_django', loader.render_to_string
    )
