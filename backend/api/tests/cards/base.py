# sourcery skip: snake-case-functions
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase

from api.tests.cards.factories import TodoFactory, TagFactory
from api.tests.users.factories import UserFactory


class BaseCardsTest(APITestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()
        cls.todos = [TodoFactory(owner=cls.user) for _ in range(10)]
        cls.other_todo = TodoFactory()

        cls.tags = [TagFactory() for _ in range(2)]

        cls.todos[0].tags.add(cls.tags[0].id)
        cls.todos[0].tags.add(cls.tags[1].id)
        cls.todos[1].tags.add(cls.tags[0].id)
        cls.todos[2].tags.add(cls.tags[1].id)

        cls.todos_url = reverse_lazy('todo-list')
        cls.todos_detail_url = reverse_lazy('todo-detail', args=(cls.todos[-1].id,))
        cls.tags_url = reverse_lazy('tag-list')
        cls.tags_detail_url = reverse_lazy('tag-detail', args=(cls.tags[-1].id,))
