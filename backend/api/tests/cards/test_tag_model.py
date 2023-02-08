# sourcery skip: snake-case-functions
from django.test import TestCase
from django.db.utils import IntegrityError

from api.tests.cards.factories import TagFactory


class TestTagModel(TestCase):

    def setUp(self) -> None:
        self.tag = TagFactory()

    def test_title_case_insensitive_unique(self) -> None:
        tag = TagFactory()
        tag.title = self.tag.title.upper()

        try:
            tag.save(update_fields=('title',))
        except IntegrityError as err:
            self.assertEqual(type(err), IntegrityError)
        else:
            self.fail('IntegrityError not raised')
