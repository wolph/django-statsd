from __future__ import with_statement
import django_statsd

class TimingCursorWrapper(object):
    def execute(self, *args, **kwargs):
        with django_statsd.with_('sql.%s' % self.db.alias):
            return self.cursor.execute(*args, **kwargs)

    def executemany(self, *args, **kwargs):
        with django_statsd.with_('sql.%s' % self.db.alias):
            return self.cursor.executemany(*args, **kwargs)

