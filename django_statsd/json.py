# The module is intentionally named `json` to mirror the patched
# library (like `celery.py`/`redis.py`/`templates.py`); it is public
# API (`django_statsd.json`, see `__init__.__all__` and
# `docs/django_statsd.rst`), so renaming it would be a breaking change.
# ruff: noqa: A005
"""Time stdlib :mod:`json` calls as ``json.<function>`` metrics."""

import json

from django_statsd import middleware

if not hasattr(json, 'statsd_patched'):
    # Monkeypatching the stdlib json module: none of the checkers know
    # about `statsd_patched`, and ty additionally resolves `json.load`
    # et al. to their concrete stdlib signatures, so a wrapped callable
    # is not assignable there either.
    json.statsd_patched = True  # type: ignore[attr-defined]  # ty: ignore[unresolved-attribute]
    json.load = middleware.wrapper('json', json.load)  # ty: ignore[invalid-assignment]
    json.loads = middleware.wrapper('json', json.loads)  # ty: ignore[invalid-assignment]
    json.dump = middleware.wrapper('json', json.dump)  # ty: ignore[invalid-assignment]
    json.dumps = middleware.wrapper('json', json.dumps)  # ty: ignore[invalid-assignment]
