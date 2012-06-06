from __future__ import absolute_import
import django_statsd

try:
    import json

    if not hasattr(json, 'statsd_patched'):
        json.statsd_patched = True
        json.load = django_statsd.wrapper('json', json.load)
        json.loads = django_statsd.wrapper('json', json.loads)
        json.dump = django_statsd.wrapper('json', json.dump)
        json.dumps = django_statsd.wrapper('json', json.dumps)
except ImportError:
    pass

try:
    import cjson

    if not hasattr(json, 'statsd_patched'):
        cjson.statsd_patched = True
        cjson.encode = django_statsd.wrapper('cjson', cjson.encode)
        cjson.decode = django_statsd.wrapper('cjson', cjson.decode)
except ImportError:
    pass

