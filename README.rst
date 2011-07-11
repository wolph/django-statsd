Introduction
============

`django_statsd` is a middleware that uses `python-statsd` to log query
and view durations to statsd.

* Python Statsd
    - https://github.com/WoLpH/python-statsd
* Graphite
    - http://graphite.wikidot.com
* Statsd 
    - code: https://github.com/etsy/statsd
    - blog post: http://codeascraft.etsy.com/2011/02/15/measure-anything-measure-everything/


Install
=======

To install simply execute `python setup.py install`.
If you want to run the tests first, run `python setup.py nosetests`


Usage
=====

Just add `django_statsd` to the `installed_apps` and add
`django_statsd.middleware.TimingMiddleware` to `MIDDLEWARE_CLASSES`


Advanced Usage
--------------

    >>> def some_view(request):
    ...     with request.timings('something_to_time'):
    ...         # do something here
    ...         pass
    >>>    
    >>> def some_view(request):
    ...     request.timings.start('something_to_time')
    ...     # do something here
    ...     request.timings.stop('something_to_time')

