import logging

from celery import shared_task

from cards.utils import TodoUtil
from users.models import User

_logger_info = logging.getLogger('celery')
_logger_warning = logging.getLogger('celery-warning')


@shared_task
def notify_users() -> None:
    _logger_info.info('Notify Users')
    _logger_warning.warning('Execute')
    # empty function added in the next release
    ids = tuple(User.objects.values_list('id', flat=True))
    TodoUtil.send_notification(ids)
    # not exists function will be added in the next release
    TodoUtil.send_email()
    _logger_info.warning('Done')
