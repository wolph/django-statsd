from __future__ import absolute_import
import django_statsd

try:
    import httplib

    class StatsdHTTPConnection(httplib.HTTPConnection):

        def __init__(self, *args, **kwargs):
            origHTTPConnection.__init__(self, *args, **kwargs)

        def _get_host_name(self):
            hostname = self.host
            if self.port != 80:
                hostname += '-%d' % self.port

            hostname = hostname.replace('.', '-')
            return hostname

        def connect(self, *args, **kwargs):
            django_statsd.start('url.%s' % self._get_host_name())
            return origHTTPConnection.connect(self, *args, **kwargs)

        def close(self, *args, **kwargs):
            if self.sock is not None:
                django_statsd.stop('url.%s' % self._get_host_name())
            return origHTTPConnection.close(self, *args, **kwargs)

        def __del__(self, *args, **kwargs):
            if self.sock is not None:
                django_statsd.stop('url.%s' % self._get_host_name())
            return origHTTPConnection.__del__(self, *args, **kwargs)

    origHTTPConnection = None
    # NOTE issubclass is true if both are the same class
    if not issubclass(httplib.HTTPConnection, StatsdHTTPConnection):
        origHTTPConnection = httplib.HTTPConnection
        httplib.HTTPConnection = StatsdHTTPConnection
except ImportError:
    pass
