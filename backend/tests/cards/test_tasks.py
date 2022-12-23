import datetime as dt
import logging
from unittest import mock

from django.test import TestCase

from cards.models import Tag, Todo
from cards.tasks import notify_users, remove_unused_tags
from cards.utils import TodoUtil
from users.models import User
from tests.cards.factories import TodoFactory, TagFactory
from tests.users.factories import UserFactory


class TestCardsTask(TestCase):

    def setUp(self) -> None:
        self.user = UserFactory()
        self.todo = TodoFactory()
        self.tag1 = TagFactory()
        self.tag2 = TagFactory()

    @mock.patch.object(TodoUtil, 'send_email', mock.MagicMock(return_value=None), create=True)
    @mock.patch('cards.tasks.datetime')
    @mock.patch('cards.tasks._logger_info.warning')
    @mock.patch('cards.tasks._logger_warning.warning')
    @mock.patch('cards.tasks._logger_info.info')
    def test_notify_users_loggers(
        self,
        info_info,
        warning_warning,
        info_warning, date_mock
    ) -> None:
        date_mock.today.return_value = dt.date(2022, 1, 1)
        notify_users()
        self.assertEqual(info_info.call_count, 1)
        info_info.assert_called_with('Waiting for notification')
        self.assertEqual(warning_warning.call_count, 1)
        warning_warning.assert_called_with('Execute')
        self.assertEqual(info_warning.call_count, 1)
        info_warning.assert_called_with('Done')

    @mock.patch.object(TodoUtil, 'send_email', mock.MagicMock(return_value=None), create=True)
    @mock.patch.object(logging.handlers.RotatingFileHandler, 'emit')
    def test_rotating_handler(self, rotating_handler_emit) -> None:
        notify_users()
        self.assertEqual(rotating_handler_emit.call_count, 1)

    @mock.patch.object(TodoUtil, 'send_email', mock.MagicMock(return_value=None), create=True)
    @mock.patch('cards.tasks.datetime')
    @mock.patch('cards.tasks.TodoUtil.send_notification')
    def test_send_notification(self, send_notification, date_mock) -> None:
        date_mock.today.return_value = dt.date(2022, 1, 2)
        notify_users()
        self.assertEqual(send_notification.call_count, 1)
        ids = tuple(User.objects.values_list('id', flat=True))
        send_notification.assert_called_with(ids)

    @mock.patch('cards.tasks.TodoUtil.send_email', create=True)
    def test_send_email(self, send_email) -> None:
        notify_users()
        self.assertEqual(send_email.call_count, 0)

    def test_remove_unused_tags(self) -> None:
        self.assertEqual(Tag.objects.count(), 2)
        remove_unused_tags()
        todo_ids = Todo.objects.prefetch_related('tags').values_list('tags__id', flat=True)
        self.assertFalse(
            (
                Tag.objects
                .exclude(id__in=todo_ids)
                .exists()
            )
        )
        self.assertEqual(Tag.objects.count(), 0)

    def test_do_not_remove_used_tags(self) -> None:
        self.assertEqual(Tag.objects.count(), 2)
        self.todo.tags.add(self.tag1)
        remove_unused_tags()
        todo_ids = Todo.objects.prefetch_related('tags').values_list('tags__id', flat=True)
        self.assertFalse(
            (
                Tag.objects
                .exclude(id__in=todo_ids)
                .exists()
            )
        )
        self.assertTrue(self.todo.tags.first().id == self.tag1.id)
        self.assertEqual(Tag.objects.count(), 1)
