"""Patch :class:`redis.Redis` to time commands as ``redis.<command>``."""

from typing import Any

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
    _original_redis = redis.Redis

    class StatsdRedis(_original_redis):
        statsd_patched = True

        def execute_command(self, *args: Any, **kwargs: Any) -> Any:
            name = str(args[0]).lower() if args else 'unknown'
            with middleware.with_(f'redis.{name}'):
                # redis.Redis.execute_command ships with no annotations.
                call = super().execute_command
                return call(*args, **kwargs)  # type: ignore[no-untyped-call]

    redis.Redis = StatsdRedis  # type: ignore[misc]  # ty: ignore[invalid-assignment]
