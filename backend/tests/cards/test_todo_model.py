# sourcery skip: snake-case-functions
from django.test import TestCase

from tests.cards.factories import TodoFactory

# Create your tests here.


class TestTodoModel(TestCase):

    def setUp(self) -> None:
        self.todo = TodoFactory()

    def test_owner_field_exists(self) -> None:
        todo_fields = [field.name for field in self.todo._meta.get_fields()]
        self.assertIn('owner', todo_fields)

    def test_get_default_incompleted(self) -> None:
        self.assertEqual(self.todo.completed, False)
