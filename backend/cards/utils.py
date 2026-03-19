from django.contrib import messages
from django.core.cache import cache
from django.utils import timezone
from copy import deepcopy
from cards.models import Todo, Tag

class NotifyUtil:
    @staticmethod
    def send_notification(user_ids, message=None, level='info') -> None:
        """
        Send notifications to users using Django messages framework

        Args:
            user_ids: Tuple of user IDs to notify
            message: Custom message (optional)
            level: Message level ('info', 'success', 'warning', 'error')
        """
        if not message:
            message = f"You have pending todos to complete!"

        # Get message level constant
        level_map = {
            'info': messages.INFO,
            'success': messages.SUCCESS,
            'warning': messages.WARNING,
            'error': messages.ERROR
        }
        message_level = level_map.get(level, messages.INFO)

        # Store notifications in cache for retrieval when users log in
        for user_id in user_ids:
            cache_key = f'user_notifications_{user_id}'
            notifications = cache.get(cache_key, [])
            notifications.append({
                'message': message,
                'level': message_level,
                'timestamp': timezone.now().isoformat()
            })
            cache.set(cache_key, notifications, timeout=21600)  # 6 hours

    @staticmethod
    def get_user_notifications(user_id):
        """Get and clear notifications for a user"""
        cache_key = f'user_notifications_{user_id}'
        notifications = deepcopy(cache.get(cache_key, []))
        if notifications:
            cache.delete(cache_key)
        return notifications

    @staticmethod
    def add_message_to_user(request, message, level='info'):
        """Add message directly to user's request (for immediate display)"""
        level_map = {
            'info': messages.INFO,
            'success': messages.SUCCESS,
            'warning': messages.WARNING,
            'error': messages.ERROR
        }
        message_level = level_map.get(level, messages.INFO)
        messages.add_message(request, message_level, message)

class TagUtil:
    @staticmethod
    def remove_tags() -> None:
        todo_ids = set(
            Todo.objects.prefetch_related('tags').values_list('tags__id', flat=True)
        )

        Tag.objects.exclude(id__in=todo_ids).delete()

class EmailUtil:
    pass
