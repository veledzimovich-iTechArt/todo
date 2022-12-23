from rest_framework.permissions import SAFE_METHODS
from rest_framework import status

from tests.users.base import BaseUserTest
from users.models import User


class TestUserListView(BaseUserTest):

    def test_get_list_unauth_success(self):
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), User.objects.count())

    def test_all_safe_methods_unauth_success(self):
        for method in SAFE_METHODS:
            call_method = getattr(self.client, method.lower())
            response = call_method(self.user_list_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_all_write_methods_unauth_forbidden(self):
        for method in ['post', 'put', 'patch', 'delete']:
            call_method = getattr(self.client, method.lower())
            response = call_method(self.user_list_url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_list_auth_success(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), User.objects.count())

    def test_all_safe_methods_auth_success(self):
        self.client.force_authenticate(self.user)
        for method in SAFE_METHODS:
            call_method = getattr(self.client, method.lower())
            response = call_method(self.user_list_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_all_write_methods_auth_not_allowed(self):
        self.client.force_authenticate(self.user)
        for method in ['post', 'put', 'patch', 'delete']:
            call_method = getattr(self.client, method.lower())
            response = call_method(self.user_list_url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class TestUserProfileView(BaseUserTest):

    def test_get_unauth_user_profile_forbidden(self) -> None:
        response = self.client.get(self.user_profile)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_other_auth_user_profile_forbidden(self) -> None:
        self.client.force_authenticate(self.other_user)
        response = self.client.get(self.user_profile)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_auth_user_profile_success(self) -> None:
        self.client.force_authenticate(self.user)
        response = self.client.get(self.user_profile)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_username_profile_success(self) -> None:
        self.client.force_authenticate(self.user)
        response = self.client.get(self.user_profile)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['first_name'], self.user.first_name)
        self.assertEqual(response.data['last_name'], self.user.last_name)
        self.assertEqual(response.data['phone'], self.user.phone)
        self.assertEqual(response.data['email'], self.user.email)
