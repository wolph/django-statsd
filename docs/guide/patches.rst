Patched libraries
=================

Three modules are patched on import, each guarded so that importing
django-statsd twice does not wrap anything twice.

json
----

:mod:`django_statsd.json` wraps :func:`json.load`, :func:`json.loads`,
:func:`json.dump` and :func:`json.dumps`, submitting timings under
``json.<function>``. Serialising a large response is easy to overlook
and occasionally the answer to a puzzling view timing.

Templates
---------

:mod:`django_statsd.templates` wraps
``django.template.loader.render_to_string`` and submits the result under
``render_django``. Template rendering happens inside the view timing, so
this tells you how much of the view was the template.

redis
-----

:mod:`django_statsd.redis` subclasses :class:`redis.Redis` and times
every command as ``redis.<command>``, lower-cased, so a ``PING``
reports as ``redis.ping``. The patch replaces ``redis.Redis`` itself,
which means clients you construct afterwards are timed without any
change on your side.

Nothing here needs configuration. If the library is not installed the
patch module imports and does nothing.
