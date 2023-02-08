# sourcery skip: snake-case-functions
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase

from api.tests.users.factories import UserFactory


class BaseUserTest(APITestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()
        cls.other_user = UserFactory()

        cls.login_url = reverse_lazy('login')
        cls.logout_url = reverse_lazy('logout')
        cls.register_url = reverse_lazy('register')
