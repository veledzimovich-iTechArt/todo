from rest_framework import status

from cards.models import Tag
from api.tests.cards.base import BaseCardsTest


class TestGetTagView(BaseCardsTest):

    def test_get_tags_unauth_user_success(self) -> None:
        response = self.client.get(self.tags_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.tags))

        response = self.client.get(self.tag_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.tags))

    def test_get_tags_auth_user_success(self) -> None:
        self.client.force_authenticate(self.user)
        response = self.client.get(self.tags_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.tags))

        response = self.client.get(self.tag_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.tags[-1].id)


class TestPostTagView(BaseCardsTest):

    def test_post_tag_unauth_user_forbidden(self) -> None:
        response = self.client.post(
            self.tags_url, data={"title": "test"}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'], 'Authentication credentials were not provided.'
        )

    def test_post_tag_auth_user_success(self) -> None:
        self.client.force_authenticate(self.user)
        response = self.client.post(
            self.tags_url, data={"title": "test"}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.count(), len(self.tags) + 1)
        self.assertEqual(response.data['title'], 'test')


class TestDeleteTagView(BaseCardsTest):

    def test_delete_tag_unauth_user_forbidden(self) -> None:
        response = self.client.delete(self.tag_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'], 'Authentication credentials were not provided.'
        )

    def test_delete_tag_auth_user_success(self) -> None:
        self.client.force_authenticate(self.user)
        response = self.client.delete(self.tag_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(response.data)
