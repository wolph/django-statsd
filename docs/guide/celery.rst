Celery metrics
==============

Install celery and django-statsd starts reporting on it. There is no
setting to turn on.

Task status counters
--------------------

Every signal celery exports gets a counter under ``celery.status``, so a
``task_failure`` signal increments ``celery.status.task_failure``. The
receivers are connected with ``weak=False`` on purpose: they are
closures, and with celery's default weak references they were collected
immediately and never fired at all. If you ran django-statsd before 3.0
and saw no celery counters, that was why.

Task timings
------------

``task_prerun`` and ``task_postrun`` open and close a timing named after
the task, so a task reports the same way a view does. ``task_failure``
clears the scope, which keeps a failed task from leaving a timer open
for the next task on that worker.

Timing inside a task
--------------------

The module-level helpers described in :doc:`manual-timing` work inside a
task, because the scope the celery signals open is the same scope they
write to.
