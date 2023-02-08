from unittest import mock

from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers
from rest_framework import status

from api.tests.users.base import BaseUserTest
from users.models import User
from users.serializers import LoginSerializer


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

    def test_no_user_no_password_serializer_error(self) -> None:
        serializer = LoginSerializer(
            data={
                'username': '',
                'password': ''
            }
        )
        try:
            serializer.validate(serializer.initial_data)
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as err:
            self.assertEqual(
                str(err.detail[0]),
                'Both "username" and "password" are required.'
            )
        else:
            self.fail('ValidationError is not raised')


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

    data = {
        'username': 'test',
        'password': 'test12345',
        'email': 'test@mail.com'
    }

    def test_register_user_suceess(self) -> None:
        data = {**self.data}
        response = self.client.post(
            self.register_url,
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.last()
        self.assertEqual(response.data['username'], user.username)
        self.assertEqual(response.data['email'], user.email)

    def test_register_user_no_username_bad_request(self) -> None:
        data = {**self.data}
        data.pop('username')
        response = self.client.post(
            self.register_url,
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_same_username_bad_request(self) -> None:
        data = {**self.data, 'username': self.user.username}
        response = self.client.post(
            self.register_url,
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_no_password_bad_request(self) -> None:
        data = {**self.data}
        data.pop('password')
        response = self.client.post(
            self.register_url,
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_wrong_password_bad_request(self) -> None:
        data = {**self.data, 'password': self.data['password'][:4]}
        response = self.client.post(
            self.register_url,
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_no_email_bad_request(self) -> None:
        data = {**self.data}
        data.pop('email')
        response = self.client.post(
            self.register_url,
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_same_email_bad_request(self) -> None:
        data = {**self.data, 'email': self.user.email}
        response = self.client.post(
            self.register_url,
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_wrong_email_bad_request(self) -> None:
        data = {**self.data, 'email': self.data['email'][:4]}
        response = self.client.post(
            self.register_url,
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
