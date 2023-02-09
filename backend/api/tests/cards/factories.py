import factory
from cards.models import Tag, Todo
from api.tests.users.factories import UserFactory


class TodoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Todo

    owner = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence', nb_words=2)
    description = factory.Faker('text')


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    title = factory.Sequence(lambda n: f'tag {n}')
