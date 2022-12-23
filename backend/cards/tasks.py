import logging

from celery import shared_task

from datetime import datetime
from cards.utils import TodoUtil, TagUtil
from users.models import User

_logger_info = logging.getLogger('celery')
_logger_warning = logging.getLogger('celery-warning')


@shared_task
def notify_users() -> None:
    _logger_warning.warning('Execute')

    if datetime.today().day % 2 == 0:
        ids = tuple(User.objects.values_list('id', flat=True))
        # empty function added in the next release
        TodoUtil.send_notification(ids)
    else:
        _logger_info.info('Waiting for notification')
    # not exists function will be added in the next release
    # TodoUtil.send_email()
    _logger_info.warning('Done')


@shared_task
def remove_unused_tags() -> None:
    _logger_warning.warning('Remove tags')
    TagUtil.remove_tags()
    _logger_info.warning('Done')
