from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Load data for app'

    def add_arguments(self, parser) -> None:
        parser.add_argument('--app_label', type=str, nargs='?')

    def handle(self, *args, **options) -> None:
        cards_fixtures = (
            'tags',
            'todos',
        )
        users_fixtures = ('users',)

        app_label = options['app_label']
        load_all_fixtures = app_label is None

        if app_label == 'users' or load_all_fixtures:
            for fixture in users_fixtures:
                call_command('loaddata', f'{fixture}')

        if app_label == 'cards' or load_all_fixtures:
            for fixture in cards_fixtures:
                call_command('loaddata', f'{fixture}')
