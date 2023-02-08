# sourcery skip: snake-case-functions
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase


from api.tests.users.factories import UserFactory


class BaseUserTest(APITestCase):

    def post_request(self, url, username, password, email=''):
        data = {
            'username': username,
            'password': password,
            'email': email
        }
        return self.client.post(url, data=data, format='json')

    @classmethod
    def setUpTestData(cls) -> None:
        cls.password = 'password'
        cls.user = UserFactory()
        cls.user.set_password(cls.password)
        cls.user.save(update_fields=('password',))
        cls.other_password = 'other_password'
        cls.other_user = UserFactory()
        cls.other_user.set_password(cls.other_password)
        cls.other_user.save(update_fields=('password',))

        cls.login_url = reverse_lazy('login')
        cls.logout_url = reverse_lazy('logout')
        cls.register_url = reverse_lazy('register')
        cls.user_list_url = reverse_lazy('users')
        cls.user_detail_url = reverse_lazy('user', args=(cls.user.id,))

        cls.user_profile = reverse_lazy('user-profile', args=(cls.user.id,))
