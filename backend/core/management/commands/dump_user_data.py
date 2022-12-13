from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Dump user fixtures'

    def handle(self, *args, **options) -> None:
        call_command('dumpdata', 'users.User', output='backend/users/fixtures/users.json')
        call_command('dumpdata', 'cards.Todo', output='backend/cards/fixtures/todos.json')
        call_command('dumpdata', 'cards.Tag', output='backend/cards/fixtures/tags.json')
