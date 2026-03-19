import logging

from celery import shared_task

from datetime import datetime
from cards.utils import NotifyUtil, TagUtil, EmailUtil
from users.models import User

_logger_info = logging.getLogger('celery')
_logger_warning = logging.getLogger('celery-warning')


@shared_task
def notify_users() -> None:
    _logger_warning.warning('Notify users')

    # Notify users who have incomplete todos
    ids = tuple(
        User.objects
        .filter(todos__completed=False)
        .values_list("id", flat=True)
        .distinct()
    )

    if datetime.today().day % 2 == 0:
        NotifyUtil.send_notification(ids)
    else:
        NotifyUtil.send_notification(
            ids,
            message="Don't forget to check your todos!",
            level='warning'
        )
    # not exists function will be added in the next release
    # EmailUtil.send_email(ids)

    _logger_info.warning('Done')


@shared_task
def remove_unused_tags() -> None:
    _logger_warning.warning('Remove tags')
    TagUtil.remove_tags()


