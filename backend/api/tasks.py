from __future__ import absolute_import, unicode_literals

import logging
import os
from typing import Callable

from celery import Celery, current_app, shared_task
from django.core.cache import cache

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

logger = logging.getLogger('api')
app = Celery('api')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


# def cancel_celery_task_by_cache_key(cache_key: str) -> None:
#     task_id = cache.get(cache_key)
#     if task_id:
#         current_app.control.revoke(task_id, terminate=True)
#         cache.delete(cache_key)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


# @shared_task
# def run_sync_proc(proc: Callable, *args, **kwargs):
#     """Run specific synchronization procedure."""
#     logger.info(f'Sync {proc.__name__} started...')
#     try:
#         proc(*args, **kwargs)
#     except Exception as ex:
#         logger.info(f'Sync Failed: {ex}')
#     else:
#         logger.info(f'Sync {proc.__name__} success.')
