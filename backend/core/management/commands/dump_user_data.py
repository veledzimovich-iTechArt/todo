from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.apps import apps
import os


class Command(BaseCommand):
    help = 'Dump user and card fixtures'

    def handle(self, *args, **options):
        # Users fixtures
        users_path = apps.get_app_config('users').path
        users_file = os.path.join(users_path, 'fixtures', 'users.json')
        os.makedirs(os.path.dirname(users_file), exist_ok=True)
        call_command('dumpdata', 'users.User', output=users_file)

        # Cards fixtures
        cards_path = apps.get_app_config('cards').path

        todos_file = os.path.join(cards_path, 'fixtures', 'todos.json')
        tags_file = os.path.join(cards_path, 'fixtures', 'tags.json')
        os.makedirs(os.path.dirname(todos_file), exist_ok=True)

        call_command('dumpdata', 'cards.Todo', output=todos_file)
        call_command('dumpdata', 'cards.Tag', output=tags_file)
