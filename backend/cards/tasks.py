import logging

from celery import shared_task
from cards.models import Tag

logger = logging.getLogger('Main')


@shared_task
def notify_users():
    logger.info(f'User')

    logger.info('Done')
