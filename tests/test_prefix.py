from __future__ import with_statement
from unittest import TestCase
import mock
from django_statsd import middleware


class TestPrefix(TestCase):

    @mock.patch('statsd.Client')
    def test_prefix(self, mock_client):
        from django import test

        def get_keys():
            return set(sum(
                [list(x[0][1]) for x in mock_client._send.call_args_list],
                []
            ))

        middleware.StatsdMiddleware.start()
        middleware.StatsdMiddleware.stop()

        assert get_keys() >= set((
            'some_key_prefix.view.hit',
            'some_key_prefix.view.site.hit',
            'some_key_prefix.view.total',
        ))

        test.Client().get('/test_app/')
        assert get_keys() >= set([
            'some_key_prefix.view.get.tests.test_app.views.index.hit',
            'some_key_prefix.view.get.tests.test_app.views.index.'
            'process_request',
            'some_key_prefix.view.get.tests.test_app.views.index.'
            'process_response',
            'some_key_prefix.view.get.tests.test_app.views.index.'
            'process_view',
            'some_key_prefix.view.get.tests.test_app.views.index.total',
            'some_key_prefix.view.hit',
            'some_key_prefix.view.site.hit',
            'some_key_prefix.view.total',
        ])
