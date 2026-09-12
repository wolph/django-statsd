# Local stub for celery, which ships no type information.
# django_statsd.celery walks dir(signals) and connects a receiver to
# every Signal it finds, so every signal celery exports is declared.
from celery.utils.dispatch import Signal

after_setup_logger: Signal
after_setup_task_logger: Signal
after_task_publish: Signal
beat_embedded_init: Signal
beat_init: Signal
before_task_publish: Signal
celeryd_after_setup: Signal
celeryd_init: Signal
eventlet_pool_apply: Signal
eventlet_pool_postshutdown: Signal
eventlet_pool_preshutdown: Signal
eventlet_pool_started: Signal
heartbeat_sent: Signal
import_modules: Signal
setup_logging: Signal
task_failure: Signal
task_internal_error: Signal
task_postrun: Signal
task_prerun: Signal
task_received: Signal
task_rejected: Signal
task_retry: Signal
task_revoked: Signal
task_sent: Signal
task_success: Signal
task_unknown: Signal
user_preload_options: Signal
worker_before_create_process: Signal
worker_init: Signal
worker_process_init: Signal
worker_process_shutdown: Signal
worker_ready: Signal
worker_shutdown: Signal
worker_shutting_down: Signal
