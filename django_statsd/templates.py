"""Time Django template rendering as ``render_django`` metrics."""

from django.template import loader

from django_statsd import middleware

if not hasattr(loader, 'statsd_patched'):
    # Monkeypatching django.template.loader: none of the checkers know
    # about `statsd_patched`, and ty additionally resolves
    # `render_to_string` to its concrete signature, so the wrapped
    # callable is not assignable there either.
    loader.statsd_patched = True  # type: ignore[attr-defined]  # ty: ignore[unresolved-attribute]
    loader.render_to_string = middleware.named_wrapper(  # ty: ignore[invalid-assignment]
        'render_django', loader.render_to_string
    )
