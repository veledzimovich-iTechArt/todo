import factory
from users.models import User


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'nickname {n}')
    email = factory.Sequence(lambda n: f'person{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    phone = factory.Faker('phone_number')
