from __future__ import with_statement
from unittest import TestCase
import mock
from django_statsd import middleware


class TestPrefix(TestCase):
    @mock.patch('statsd.Client')
    def test_prefix(self, mock_client):
        from django import test
        middleware.StatsdMiddleware.start()
        middleware.StatsdMiddleware.stop()

        client = test.Client()

        def get_keys():
            return set(sum(
                [x[0][1].keys() for x in mock_client._send.call_args_list],
                []
            ))

        assert get_keys() == set((
            'some_key_prefix.view.hit',
            'some_key_prefix.view.site.hit',
            'some_key_prefix.view.total',
        ))
        client.get('/test_app/')
        assert get_keys() == set(['some_key_prefix.view.get.views.index.hit',
            'some_key_prefix.view.get.views.index.process_request',
            'some_key_prefix.view.get.views.index.process_response',
            'some_key_prefix.view.get.views.index.process_view',
            'some_key_prefix.view.get.views.index.total',
            'some_key_prefix.view.hit',
            'some_key_prefix.view.site.hit',
            'some_key_prefix.view.total'])


