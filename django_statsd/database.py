"""Database query timing through Django's ``execute_wrapper`` hooks.

Enabled by the ``STATSD_TRACK_DATABASE`` setting;
:class:`~django_statsd.middleware.StatsdMiddleware` wraps every configured
connection for the duration of each request and submits the query
durations as ``sql.<alias>`` timings.
"""

from collections.abc import Callable
from typing import Any

QueryContext = dict[str, Any]
ExecuteFunc = Callable[[str, Any, bool, QueryContext], Any]
ExecuteWrapper = Callable[[ExecuteFunc, str, Any, bool, QueryContext], Any]


def statsd_execute_wrapper(alias: str) -> ExecuteWrapper:
    """Build an execute wrapper timing queries as ``sql.<alias>``."""
    # Imported here to avoid a circular import: middleware imports this
    # module when installing the wrappers.
    from django_statsd import middleware

    def timed_execute(
        execute: ExecuteFunc,
        sql: str,
        params: Any,
        many: bool,
        context: QueryContext,
    ) -> Any:
        with middleware.with_(f"sql.{alias}"):
            return execute(sql, params, many, context)

    return timed_execute
