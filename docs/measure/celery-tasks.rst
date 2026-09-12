Measure your Celery tasks
=========================

A request that returns in 40 ms because it queued the work has moved
the time somewhere else. Install Celery and django-statsd starts
reporting on where it went. There's no setting to turn on.

.. literalinclude:: ../_transcripts/celery.txt
   :language: text

Two families, and they're prefixed differently, which surprises people.

``myproject.celery.<task name>`` follows your ``STATSD_PREFIX`` and
holds the timings: ``total`` for the task and ``hit`` for the counter,
named after the task so ``myproject.tasks.send_invoice`` reports under
its own dotted path. ``myproject.celery.site.hit`` counts every task
the way ``view.site.hit`` counts every request.

``celery.status.*`` carries no prefix at all. Those counters are wired
to every signal Celery exports, one counter per signal, so
``task_failure`` above is a task that failed. If you run more than one
project against one statsd, these names collide, and there's no setting
to change it. I give each project its own statsd for exactly this
reason, and I found out by wondering why ``task_failure`` was running
at twice the rate my logs said.

Timers survive a failure
------------------------

``task_prerun`` opens the timing and ``task_postrun`` closes it.
``task_failure`` clears the scope instead, which stops a failed task
from leaving a timer open for whatever the worker picks up next.

The module-level helpers from :doc:`your-own-code` work inside a task,
because the scope Celery's signals open is the one they write to.

A note on 3.0
-------------

Before 3.0 these receivers were connected with Celery's default weak
references. They were closures, so they were collected immediately and
never fired. If you ran django-statsd and saw no Celery counters, that
was why, and it's fixed.
