# Changelog

## 3.0.0 (2026-09-12)

### Breaking changes

- Python 3.10+ and Django 5.2+ are now required. Django is an explicit
  install dependency. Django 4.2 reached end of life in April 2026, so
  the supported matrix is Django 5.2, 6.0 and 6.1.
- `django_statsd.urls` (Python 2 `httplib` patching) has been removed. It
  had been silently dead code on Python 3.
- `cjson` and `coffin` patching removed (both packages are long dead).
- `django_statsd.__about__` removed. Use `django_statsd.__version__`.
- Database timing has been reimplemented on Django's
  `connection.execute_wrapper()` and must be enabled with the new
  `STATSD_TRACK_DATABASE` setting. The old `TimingCursorWrapper` never
  worked on Python 3, so no working behaviour was lost.

### Fixed

- The middleware scope now uses `asgiref.local.Local` instead of
  `threading.local`, making it correct under ASGI/async deployments.
- The tracked view name is stored on the request scope instead of the
  shared middleware instance, fixing a race between concurrent requests.
- Celery signal receivers were connected with weak references to local
  closures and were garbage-collected immediately. The `celery.status.*`
  counters now actually fire, per signal invocation instead of once at
  import.
- `process_exception`/`process_response` no longer raise `AttributeError`
  when the scope was never started.

### Internal

- Modern packaging (`pyproject.toml` + `uv_build`), `py.typed`, ruff
  lint/format, strict typing checked by mypy, basedpyright, pyrefly and
  ty, 100% test coverage enforced in CI, split GitHub Actions workflows
  with PyPI Trusted Publishing, furo-themed documentation.

## 2.7.0 and earlier

See the [git history](https://github.com/WoLpH/django-statsd/commits/master).
