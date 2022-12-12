# DjangoRest

# Run app
```bash
git clone https://github.com/veledzimovich-iTechArt/todo
cd todo
mv backend/env backend/.env
docker compose build
docker compose up
```

# Initial Django setup
## Create project
```bash
mkdir todo
cd todo/
python3 -m venv django
source venv-django/bin/activate
mkdir backend
# common
pip3 install django djangorestframework django-cors-headers celery django-redis psycopg2 python-dotenv
pip3 freeze > backend/requirements.txt
# dev
pip3 install autopep8 flake8 pycodestyle pytest memory_profiler django-debug-toolbar pytest-django
pip3 freeze > backend/requirements-dev.txt
cd backend/
# Note the trailing '.' character
django-admin startproject Main .
```
## Add database
```bash
psql -c 'create database todo;'
```
## Add apps
```bash
python manage.py startapp users
python manage.py startapp cards
```

1. Main/settings.py
```python
AUTH_USER_MODEL = 'user.User'
PROJECT_APPS = [
    'users',
    'cards'
]
INSTALLED_APPS = [
    # ...
    'corsheaders',
    'rest_framework',
    *PROJECT_APPS
]
MIDDLEWARE = [
    # rest
    'corsheaders.middleware.CorsMiddleware',
    # before 'django.middleware.common.CommonMiddleware'
]
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://0.0.0.0:3000',
]
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://0.0.0.0:3000',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'todo',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
```
2. users/models.py
```python
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, verbose_name='Phone', null=True, blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return '{0} ({1})'.format(self.username, self.email)

```
3. cards/models.py
4. cards/admin.py
5. cards/serializers.py
6. cards/views.py
7. Main/urls.py
8. First run
```bash
python manage.py migrate

python manage.py createsuperuser --email a.veledzimovich@itechart-group.com --username admin
# password: test12345
python manage.py runserver
```

9. Add env file
```bash
touch backend/env
```

## Add owner to the Todo
1. cards/models.py
```python
class Todo(models.Model):
    owner = models.ForeignKey(User, related_name='todos', on_delete=models.CASCADE)
```
2. cards/views.py
```python
class TodoView(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    queryset = Todo.objects.all()
    permission_classes = [
        # for list
        permissions.IsAuthenticatedOrReadOnly,
        # for object allows to edit only for the owner
        IsOwnerOrReadOnly
    ]

    def perform_create(self, serializer: TodoSerializer) -> None:
        serializer.validated_data['owner'] = self.request.user
        super().perform_create(serializer)
```
3. Main/urls.py
```python
urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]
```
4. cards/permissions.py
```python
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user
```

## Add user auth
### Sesssion based

https://kylebebak.github.io/post/django-rest-framework-auth-csrf

1. Main.settings.py
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

2. users/serilizers.py
```python
from django.contrib.auth import password_validation
class LoginSerializer(serializers.Serializer):
    # ...
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(trim_whitespace=False, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']

    def validate_password(self, value: str) -> str:
        password_validation.validate_password(value, self.instance)
        return value
    # ...
```

3. users/view.py
```python
class LoginView(views.APIView):
    # ...
class LogoutView(views.APIView):
    # ...
class UserRegisterView(generics.CreateAPIView):
    # ...
```

4. users/urls.py
```python
re_path(r'^login/', LoginView.as_view(), name='login'),
re_path(r'^logout/', LogoutView.as_view(), name='logout'),
re_path(r'^register/', UserRegisterView.as_view(), name='register')
```
Add in POSTMAN X-CSRFToken

5. check Main.settings.py
```python
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_HTTPONLY = True
```

6. src/utils/cookieUtil.js
```js
export function getCookies(document) {
    let result = {};
    document.cookie.split(';').forEach(cookie => {
        let array = cookie.split('=')
        if (array.length > 1) {
            result[array[0].trim()] = array[1].trim()
        }
    });
    return result
};

export function setCookie(document, key, value, days=1) {
    const d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
    let expires = "Expires=" + d.toUTCString();
    document.cookie = `${key}=${value}; ${expires};`;
};

export function removeCookie(document, key) {
    document.cookie = `${key}=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;`;
};
```

7. src/App.js
```js
  refreshPage = () => {
    axios.defaults.headers.common['X-CSRFToken'] = getCookies(document)['csrftoken'];
    this.getTags();
    this.getCards();
  };
  signIn = (username, password) => {
    this.signInToggle();
    axios
      .post('/api/login/', { "username": username, "password": password })
      .then((res) => {
        setCookie(document, "loggedUserName", res.data.username);
        this.refreshPage();
      })
      .catch((err) => this.handleErrors(err, this.signInToggle));
  };
```

# HOW TO

## add pythom interpreter VScode
Python: select interpreter > Enter interpreter path > Find

## fix 301 status
edit Main.settings.py and add '/' in FE
```python
APPEND_SLASH = False
```

## add pytest
```bash
pip3 install pytest-django
touch pytest.ini
```
pytest.ini
```ini
[pytest]
DJANGO_SETTINGS_MODULE = Main.settings
python_files = tests.py test_*.py *_tests.py
```

?
coverage run --source='.' manage.py test polls
coverage report
coverage html

## set database extension for case-insensitive
1. create new template
psql
\c template1
CREATE EXTENSION citext;

2. cards/models.py
```python
from django.contrib.postgres.fields import CICharField, CITextField, CIEmailField
class Tag(models.Model):
    title = CICharField(max_length=120, unique=True)
```
```bash
python manage.py makemigrations
```

3. add CITextExtension() in migration
```python
from django.contrib.postgres.operations import CITextExtension
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0001_initial'),
    ]
    operations = [
        CITextExtension(),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('title', django.contrib.postgres.fields.citext.CICharField(max_length=120, unique=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.AlterModelOptions(
            name='todo',
            options={'ordering': ['title']},
        ),
        migrations.AddField(
            model_name='todo',
            name='tags',
            field=models.ManyToManyField(blank=True, to='cards.tag'),
        ),
    ]
```

## load all fixtures
1. Dump data
```bash
python manage.py dumpdata users.User > users/fixtures/users.json
python manage.py dumpdata cards.Todo > cards/fixtures/todos.json
python manage.py dumpdata cards.Tag > cards/fixtures/tags.json
```

2. Create command
```bash
mkdir -p backend/core/mangement/commands
touch backend/core/mangement/commandsload_all_data.py
```
```python
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
```

## django-debug-toolbar
1. Main/settings.py
```python
INSTALLED_APPS = [
    # ...
    "debug_toolbar",
    # ...
]
MIDDLEWARE = [
    # ...
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    # ...
]

if DEBUG:
    INTERNAL_IPS = [
        "127.0.0.1"
    ]
    # add django-debug-toolbar in docker
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())

    INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]
```
2. Main/urls.py
```python
urlpatterns = [
    # ...
    path('__debug__/', include('debug_toolbar.urls')),
]
```

## create custom user model when app has data in database
1. Edit Main.settings.py
AUTH_USER_MODEL = 'auth.User'

2. Reset migrations
python manage.py migrate auth zero
python manage.py migrate admin zero
python manage.py migrate contenttypes zero
python manage.py migrate sessions zero

manually remove DB tables for auth admin contenttypes sessions if they are exist

3. Create user app
python manage.py startapp users

3. Set owner
cards/models.py
```python
from Main.settings import AUTH_USER_MODEL
class Todo(models.Model):
    owner = models.ForeignKey(
        AUTH_USER_MODEL, related_name='todos', on_delete=models.CASCADE
    )
```

4. Initial empty migration
```bash
python manage.py makemigrations --empty users
python manage.py migrate
```

5. Create user model
rm users/migrations/0001_initial.py

```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Meta:
        db_table = 'auth_user'
```

6. Edit Main.settings.py
AUTH_USER_MODEL = 'users.User'

```bash
python manage.py makemigrations
```
edit migration and set default value for Card owner = 1
```python
field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE,
                        related_name='todos', to=settings.AUTH_USER_MODEL),
```

7. Set admin
```bash
python manage.py createsuperuser --email a.veledzimovich@itechart-group.com --username admin
# password: test12345
```
check that auth_user id = 1

8. Migrate

```bash
python manage.py migrate
```

9. Make some changes
cards/models.py
```python
from users.models import User
class Todo(models.Model):
    owner = models.ForeignKey(
        User, related_name='todos', on_delete=models.CASCADE
    )
```
users/models.py
```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=15, verbose_name='Phone', null=True, blank=True
    )

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return '{0}({1})'.format(self.get_full_name(), self.email)
```
```bash
python manage.py migrate
```

10. Setup django admin

users/admin.py
```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional info', {'fields': ('phone',)}),
    )


admin.site.register(User, CustomUserAdmin)
```

11. Change table name to users.User
I generally wouldn't recommend renaming anything, because your database structure will become inconsistent. Some of the tables will have the users_ prefix, while some of them will have the auth_ prefix. But on the other hand, you could argue that the User model is now a part of the users app, so it shouldn't have the auth_ prefix.

comment  db_table = 'auth_user'
```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, verbose_name='Phone', null=True, blank=True)

    class Meta:
        # db_table = 'auth_user'
```
```bash
python manage.py migrate
```

## setup redis
1. Main/settigs.py
```python
INSTALLED_APPS = [
    # ...
    "django_redis",
    # ...
]
REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'

REDIS_DEFAULT_CACHE_DB = '0'
REDIS_SESSION_DB = '1'
REDIS_LOGIN_ATTEMPTS_DB = '2'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://{}:{}/{}'.format(REDIS_HOST, REDIS_PORT, REDIS_DEFAULT_CACHE_DB),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 60 * 60 * 24  # one day
    },
    'session': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://{}:{}/{}'.format(REDIS_HOST, REDIS_PORT, REDIS_SESSION_DB),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 60 * 60 * 24  # one day
    }
}
DISABLE_CACHE = False
if DISABLE_CACHE:
    CACHES['default'] = {
        'BACKEND': 'adlynx_core.cache.ExtendedDummyCache'
    }

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 60 * 60 * 24
```
2. run redis
```bash
redis-server --dbfilename dump.rdb --dir . --daemonize yes
```

##  setup celery
1. Main/settigs.py
```python
INSTALLED_APPS = [
    # ...
    "celery",
    # ...
]

# Celery settings
REDIS_BROKER_DB = '2'
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BROKER_DB}'
# use json to prevent error with superuser
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_TASK_RESULT_EXPIRES = 360
CELERY_TASK_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ENABLE_UTC = True
CELERY_BEAT_SCHEDULE = {}
```

2. Main/__init__.py
```python
# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ('celery_app',)
```

3. Main/tasks.py
```python
import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main.settings')

app = Celery('Main')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

4. run celery
macos
```bash
celery  -A Main worker --loglevel=INFO --concurrency=2 -B -s celerybeat-schedule
```
linux
```bash
celery -A Main worker -l INFO --concurrency=2 -B -s celerybeat-schedule
```

## setup logging

https://docs.djangoproject.com/en/4.1/topics/logging/

# Intial React setup
## Create project
``` bash
npx create-react-app frontend
cd frontend
npm start
npm install bootstrap@4.6.0 reactstrap@8.9.0 --legacy-peer-deps
```
src/index.js
```js
import 'bootstrap/dist/css/bootstrap.css';
```
## Add axios
``` bash
npm install axios@0.21.1
```
package.json
```json
"proxy": "http://localhost:8000",
```
src/App.js
```js
// with proxy, you can provide relative paths
axios.get("/api/todos/")
```
3. use dynamic proxy
```bash
npm install http-proxy-middleware
touch src/setupProxy.js
echo "REACT_APP_PROXY='http://localhost:8000'" > frontend/.env.local
```

# Intial Docker setup
1. Create files
```bash
touch backend/Dockerfile
touch backend/.dockerignore
touch frontend/Dockerfile
touch frontend/.dockerignore
touch docker-compose.yaml
```
```bash
docker-compose build
docker-compose up
```
2. Check docker-compose.yaml
3. Optimize containers
https://medium.com/nerd-for-tech/bigger-dockerignore-smaller-docker-images-49fa22e51c7