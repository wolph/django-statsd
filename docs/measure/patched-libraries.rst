Patched libraries
=================

Three things get timed whether or not you ask, because they're the
usual suspects behind a view that is slow for no visible reason.

.. literalinclude:: ../_transcripts/patched_libraries.txt
   :language: text

``render_django`` is the template render, nested under the view that
rendered it.

json
----

:mod:`django_statsd.json` wraps :func:`json.load`, :func:`json.loads`,
:func:`json.dump` and :func:`json.dumps`, and reports them as
``json.<function>``. Serialising a large response is easy to overlook
and is occasionally the entire answer.

Templates
---------

:mod:`django_statsd.templates` wraps
``django.template.loader.render_to_string`` and reports
``render_django``. Rendering happens inside the view timing, so this
tells you how much of the view was the template.

redis
-----

:mod:`django_statsd.redis` subclasses :class:`redis.Redis` and times
each command as ``redis.<command>`` in lower case, so a ``PING``
arrives as ``redis.ping``. It replaces ``redis.Redis`` itself, so
clients you build afterwards are timed without any change on your side.

Each patch checks a marker before it runs, so importing django-statsd
twice doesn't wrap anything twice. None of them need configuration, and
a library that isn't installed is skipped.
