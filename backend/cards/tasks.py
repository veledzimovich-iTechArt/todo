import logging

from celery import shared_task


logger_info = logging.getLogger('celery')
logger_warning = logging.getLogger('celery-warning')


@shared_task
def notify_users():
    logger_info.info('User')
    logger_warning.warning('Execute')
    logger_info.warning('Done')
