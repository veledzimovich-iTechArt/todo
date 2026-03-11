from cards.models import Todo, Tag


class TodoUtil:
    @staticmethod
    def send_notification(user_ids) -> None:
        pass


class TagUtil:
    @staticmethod
    def remove_tags() -> None:
        todo_ids = set(
            Todo.objects.prefetch_related('tags').values_list('tags__id', flat=True)
        )

        Tag.objects.exclude(id__in=todo_ids).delete()
