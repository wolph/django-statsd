Quickstart
==========

Two ways in. The first needs nothing but Python and proves your metrics
are real by printing the bytes. The second brings up statsd, Graphite and
Grafana so you can watch them turn into graphs.

One minute, no Docker
---------------------

**1. Install.**

.. code-block:: bash

    pip install django-statsd

**2. Listen on the statsd port.** In one terminal, from a checkout of
this repository:

.. code-block:: console

    $ uv run python examples/udp_listener.py

No checkout to hand? ``ncat -ul 8125`` does the same job.

**3. Wire up Django.** One app entry and two middlewares. The tracker
goes at the top of the stack and the timer at the bottom, so that between
them they wrap everything else you run.

.. code-block:: python

    INSTALLED_APPS = [
        'django_statsd',
    ]

    MIDDLEWARE = [
        'django_statsd.middleware.StatsdMiddleware',
        'django_statsd.middleware.StatsdMiddlewareTimer',
    ]

    STATSD_HOST = '127.0.0.1'
    STATSD_PORT = 8125
    STATSD_PREFIX = 'myproject'
    STATSD_TRACK_MIDDLEWARE = True

Your own middlewares go between those two entries.
``STATSD_TRACK_MIDDLEWARE`` defaults to ``False``, so the middlewares
install and stay quiet until you set it. That lets the configuration
change land in one deploy and the metrics in the next.

**4. Serve one request.**

.. code-block:: console

    $ python manage.py runserver
    $ curl http://127.0.0.1:8000/dashboard/

**5. Read the first terminal.** Eight packets from that one request:

.. literalinclude:: ../_transcripts/wire.txt
   :language: text

That is the whole protocol. A name, a colon, a value, a type suffix, one
UDP packet each, and nothing sent back. ``1|c`` is a counter increment
and ``|ms`` a timing in milliseconds.

The names read left to right. ``myproject`` is your ``STATSD_PREFIX``
and ``view`` is the middleware's own. Then the HTTP method and the dotted
path of the view function, so ``dashboard`` here lives in
``myproject/views.py``. Under that name, ``total`` is the whole request
and the three ``process_*`` entries are the phases inside it. ``hit`` is
a counter, which is how you get a request rate per view without dividing
anything. The last three are project-wide: every request django-statsd
saw, every response it classified, and this response's status class.

:doc:`../reference/metrics` has the full list of names, each one
recorded the same way this one was.

Five minutes, with graphs
-------------------------

**1. Start the stack.** From a checkout:

.. code-block:: console

    $ docker compose -f examples/docker-compose.yml up -d --wait

``--wait`` returns once Graphite and Grafana both report healthy, which
takes a minute or so on a cold pull. The stack binds 18225 for statsd,
18280 for Graphite and 13200 for Grafana rather than the usual 8125,
8080 and 3000, so it stays out of the way of anything already running on
this machine.

**2. Point your project at it.**

.. code-block:: python

    STATSD_HOST = '127.0.0.1'
    STATSD_PORT = 18225
    STATSD_PREFIX = 'myproject'
    STATSD_TRACK_MIDDLEWARE = True
    STATSD_TRACK_DATABASE = True

Then use your site. Click around, run your test suite against it, point a
load generator at it. Whatever traffic you make is what you will see.

**3. Open** http://localhost:13200. Grafana has the datasource
configured and a dashboard loaded, and there is no login prompt. Give it
ten seconds to fill: statsd aggregates on a ten-second flush, so nothing
appears before the first one.

.. image:: https://raw.githubusercontent.com/WoLpH/django-statsd/master/docs/images/dashboard.png
   :alt: Grafana showing response times, request rate, where the time goes and exceptions
   :width: 100%

That screenshot is this stack, fed by django-statsd over UDP.
``docs/generate/dashboard.py`` records it by bringing up the same compose
file, so the picture and the thing you run are the same thing.

**4. Already have a Grafana?** The datasource and dashboard files are in
``examples/grafana/provisioning/``, ready to lift into it.

**5. Stop it when you are done.**

.. code-block:: console

    $ docker compose -f examples/docker-compose.yml down

Add ``-v`` to throw away the stored metrics as well.

Testing your own code
---------------------

Metrics tend to be the part of a codebase nobody tests, because a real
statsd server is a nuisance in a test suite. Two ways around that.

Disable the connection, and every call becomes a no-op while the API
stays identical:

.. code-block:: python

    STATSD_DISABLED = True

That belongs in your test settings. The middlewares still run and
``request.statsd`` still works, so nothing needs a branch for tests.

Or capture what would have been sent and assert on it, which is what
django-statsd's own suite does:

.. code-block:: python

    from unittest import mock

    import statsd

    def test_checkout_counts_attempts(client):
        with mock.patch.object(statsd.Connection, 'send') as send:
            client.get('/checkout/')

        submitted = {
            name for call in send.call_args_list for name in call.args[0]
        }
        assert any(
            name.endswith('payment.attempt') for name in submitted
        )

Those are the real metric names, not a paraphrase of them. Copy the
pattern and your tests fail when a metric name changes, which is usually
the moment you want to hear about it.

Where to go next
----------------

- :doc:`../measure/views`: what the middlewares record, and how to skip
  the views you do not care about
- :doc:`../measure/your-own-code`: timing a block through
  ``request.statsd`` or the module-level helpers
- :doc:`../measure/queries`, :doc:`../measure/celery-tasks` and
  :doc:`../measure/patched-libraries`: the other three things that get
  timed
- :doc:`../reference/metrics`: every name, recorded from a real run
- :doc:`../reference/settings`: the full list of settings

django-statsd sends through `python-statsd
<https://python-statsd.readthedocs.io/en/latest/>`_, so its documentation
covers the layer underneath. Its `metrics page
<https://python-statsd.readthedocs.io/en/latest/metrics.html>`_ has the
table of what each metric type writes, and its `connections page
<https://python-statsd.readthedocs.io/en/latest/connections.html>`_
covers sampling, disabling and what happens when the server is down.
