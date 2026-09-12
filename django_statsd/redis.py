"""Patch :class:`redis.Redis` to time commands as ``redis.<command>``."""

from collections.abc import Callable
from typing import Any, cast

from django_statsd import middleware

try:
    import redis
except ImportError:  # pragma: no cover
    redis = None  # type: ignore[assignment]


if (
    # mypy infers `redis` as non-Optional here because the `except
    # ImportError: redis = None` assignment above is itself a type
    # error (silenced via ignore[assignment]) and so does not widen
    # the declared type; the guard is still required at runtime for
    # environments where the optional `redis` dependency is missing.
    redis is not None  # type: ignore[redundant-expr]
    and not getattr(redis.Redis, 'statsd_patched', False)
):
    # The pre-patch class, kept as a handle for tests and for anything
    # that needs to reach past the patch. The class below subclasses
    # `redis.Redis` by name so its base stays statically resolvable.
    _original_redis = redis.Redis

    class StatsdRedis(redis.Redis):
        """A :class:`redis.Redis` that times every command it runs."""

        statsd_patched = True

        def execute_command(self, *args: Any, **kwargs: Any) -> Any:
            """Run a command, timed as ``redis.<command>``."""
            name = str(args[0]).lower() if args else 'unknown'
            with middleware.with_(f'redis.{name}'):
                # redis ships py.typed but leaves execute_command
                # unannotated. Casting keeps the unknown from leaking
                # into this method's return value.
                # mypy already reads it as Callable, hence the
                # redundant-cast suppression.
                call = cast(  # type: ignore[redundant-cast]
                    'Callable[..., Any]', super().execute_command
                )
                return call(*args, **kwargs)

    redis.Redis = StatsdRedis  # type: ignore[misc]  # ty: ignore[invalid-assignment]
