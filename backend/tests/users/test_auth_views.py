from unittest import mock

from django.contrib.auth.models import AnonymousUser
from rest_framework import status

from tests.users.base import BaseUserTest


class TestLoginView(BaseUserTest):

    def test_login_user_accepted(self) -> None:
        response = self.post_request(self.login_url, self.user.username, self.password)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['username'], self.user.username)

    def test_login_another_user_accepted(self) -> None:
        response = self.post_request(self.login_url, self.user.username, self.password)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['username'], self.user.username)

        self.assertEqual(response.wsgi_request.user.id, self.user.id)

        other_resp = self.post_request(
            self.login_url, self.other_user.username, self.other_password
        )
        self.assertEqual(other_resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(other_resp.data['id'], self.other_user.id)
        self.assertEqual(other_resp.data['username'], self.other_user.username)
        values = self.client.session.values()
        self.assertFalse(self.user.get_session_auth_hash() in values)
        self.assertTrue(self.other_user.get_session_auth_hash() in values)

        self.assertNotEqual(other_resp.wsgi_request.user.id, self.user.id)
        self.assertEqual(other_resp.wsgi_request.user.id, self.other_user.id)

    def test_login_user_wrong_password_bad_request(self) -> None:
        response = self.post_request(self.login_url, self.user.username, '12345')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['non_field_errors'][0], 'Access denied: wrong username or password.'
        )

    def test_wrong_user_correct_password_bad_request(self) -> None:
        response = self.post_request(self.login_url, self.other_user.username, self.password)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['non_field_errors'][0], 'Access denied: wrong username or password.'
        )


class TestLogoutView(BaseUserTest):

    def test_logout_auth_user_success(self) -> None:
        response = self.post_request(self.login_url, self.user.username, self.password)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(response.wsgi_request.user == self.user)
        self.assertTrue(len(response.wsgi_request.session.values()) != 0)

        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(response.wsgi_request.user == AnonymousUser())
        self.assertTrue(len(response.wsgi_request.session.values()) == 0)

        self.assertIsNone(response.data)

    @mock.patch('users.views._logger_warning.warning')
    def test_logout_unauth_user_logging_success(self, logger_warning) -> None:
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        logger_warning.assert_called_with(f'Logout: {response.wsgi_request.user}')

        self.assertIsNone(response.data)


class TestRegisterView(BaseUserTest):
    def test_post(self):
        pass
