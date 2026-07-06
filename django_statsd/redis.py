"""Patch :class:`redis.Redis` to time commands as ``redis.<command>``."""

from typing import Any

from django_statsd import middleware

try:
    import redis
except ImportError:  # pragma: no cover
    redis = None  # type: ignore[assignment]


if redis is not None and not getattr(redis.Redis, "statsd_patched", False):
    _original_redis = redis.Redis

    class StatsdRedis(_original_redis):  # type: ignore[misc,valid-type]
        statsd_patched = True

        def execute_command(self, *args: Any, **kwargs: Any) -> Any:
            name = str(args[0]).lower() if args else "unknown"
            with middleware.with_(f"redis.{name}"):
                return super().execute_command(*args, **kwargs)

    redis.Redis = StatsdRedis  # type: ignore[misc]
