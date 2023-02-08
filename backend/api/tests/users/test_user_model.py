# sourcery skip: snake-case-functions
from django.test import TestCase

from api.tests.users.factories import UserFactory

# Create your tests here.


class TestUserModel(TestCase):

    def setUp(self) -> None:
        self.user = UserFactory()

    def test_phone_field_exists(self) -> None:
        user_fields = [field.name for field in self.user._meta.get_fields()]
        self.assertIn('phone', user_fields)

    def test_email_field_exists(self) -> None:
        user_fields = [field.name for field in self.user._meta.get_fields()]
        self.assertIn('email', user_fields)

    def test_str_representation(self) -> None:
        str_repr = '{0} ({1})'.format(self.user.username, self.user.email)
        self.assertEqual(str(self.user), str_repr)
