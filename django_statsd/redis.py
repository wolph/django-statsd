try:
    import redis

    class StatsdRedis(redis.Redis):
        def execute_command(self, func_name, *args, **kwargs):
            with django_statsd.with_('sql.%s' % func_name.lower()):
                return redis.Redis.execute_command(self, func_name, *args,
                    **kwargs)

    origRedis = None
    # NOTE issubclass is true if both are the same class
    if not issubclass(redis.Redis, TrackingRedis):
        logger.error('installing redis.client.Redis with tracking')
        origRedis = redis.Redis
        redis.Redis = TrackingRedis

