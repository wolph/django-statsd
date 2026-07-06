# The module is intentionally named `json` to mirror the patched
# library (like `celery.py`/`redis.py`/`templates.py`); it is public
# API (`django_statsd.json`, see `__init__.__all__` and
# `docs/django_statsd.rst`), so renaming it would be a breaking change.
# ruff: noqa: A005
"""Time stdlib :mod:`json` calls as ``json.<function>`` metrics."""

import json

from django_statsd import middleware

if not hasattr(json, 'statsd_patched'):
    json.statsd_patched = True  # type: ignore[attr-defined]
    json.load = middleware.wrapper('json', json.load)
    json.loads = middleware.wrapper('json', json.loads)
    json.dump = middleware.wrapper('json', json.dump)
    json.dumps = middleware.wrapper('json', json.dumps)
