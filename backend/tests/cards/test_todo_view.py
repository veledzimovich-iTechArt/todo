from rest_framework import status

from tests.cards.base import BaseCardsTest


class TestGetTodoView(BaseCardsTest):

    def test_get_todos_unauth_user_success(self) -> None:
        response = self.client.get(self.todos_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_todos_auth_user_success(self) -> None:
        self.client.force_authenticate(self.user)

        response = self.client.get(self.todos_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.todos))

    def test_get_todos_for_specific_owner_success(self) -> None:
        self.client.force_authenticate(self.other_todo.owner)
        response = self.client.get(self.todos_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_complete_success(self) -> None:
        self.other_todo.completed = True
        self.other_todo.save(update_fields=('completed',))
        self.client.force_authenticate(self.other_todo.owner)
        response = self.client.get(self.todos_url)
        self.assertTrue(response.data[0]['completed'])

    def test_get_todo_filter_by_tag_success(self) -> None:
        self.client.force_authenticate(self.user)

        response = self.client.get(f'{self.todos_url}?tags={self.tags[0].id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_todo_filter_by_two_tag_success(self) -> None:
        self.client.force_authenticate(self.user)

        response = self.client.get(
            f'{self.todos_url}?tags={self.tags[0].id}&tags={self.tags[1].id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_get_todo_filter_by_wrong_tag_success(self) -> None:
        self.client.force_authenticate(self.user)

        response = self.client.get(
            f'{self.todos_url}?tags=100')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class TestPostTodoView(BaseCardsTest):
    data = {
        'title': 'test',
        'description': 'test',
        'completed': False,
    }

    def test_post_todos_unauth_user_forbidden(self) -> None:

        data = {
            **self.data,
            'tags': []
        }

        response = self.client.post(self.todos_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'], 'Authentication credentials were not provided.'
        )

    def test_post_todos_auth_user_success(self) -> None:
        data = {
            **self.data,
            'tags': [
                {'id': self.tags[-1].id, 'title': self.tags[-1].title}
            ]
        }
        self.client.force_authenticate(self.user)

        response = self.client.post(self.todos_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], self.data['title'])
        self.assertEqual(response.data['description'], self.data['description'])
        self.assertFalse(response.data['completed'])
        self.assertEqual(response.data['owner'], self.user.username)

    def test_post_todo_same_tag_success(self) -> None:
        pass

    def test_post_todo_wrong_tag_bad_request(self) -> None:
        pass


class TestDeleteTodoView(BaseCardsTest):

    def test_delete_tag_unauth_user_forbidden(self) -> None:
        response = self.client.delete(self.todos_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'], 'Authentication credentials were not provided.'
        )

    def test_delete_tag_auth_user_success(self) -> None:
        self.client.force_authenticate(self.user)
        response = self.client.delete(self.todos_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(response.data)
