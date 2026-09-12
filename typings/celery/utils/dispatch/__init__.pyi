# Local stub for celery, which ships no type information. Only the
# surface django_statsd.celery touches is declared.
from collections.abc import Callable
from typing import Any

class Signal:
    name: str
    def connect(
        self, *args: Any, weak: bool = ..., **kwargs: Any
    ) -> Callable[..., Any]: ...
    def send(
        self, sender: Any = ..., **named: Any
    ) -> list[tuple[Callable[..., Any], Any]]: ...
