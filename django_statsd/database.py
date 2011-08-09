from __future__ import with_statement
import django_statsd

class TimingCursorWrapper(object):
    def execute(self, *args, **kwargs):
        with django_statsd.with_('sql.execute'):
            return self.cursor.execute(*args, **kwargs)

    def executemany(self, *args, **kwargs):
        with django_statsd.with_('sql.executemany'):
            return self.cursor.executemany(*args, **kwargs)

