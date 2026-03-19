# todo

## DjangoRest

# Content

[Run app](#run-app)

[Run tests](#run-tests)

[Django Admin](#django-admin-optional)

[Initial Django setup](#initial-django-setup)

[HOW TO](#how-to)
- [add pythom interpreter VScode](#add-pythom-interpreter-vscode)
- [fix 301 status](#fix-301-status)
- [remove admin](#remove-admin)
- [reset migration](#reset-migration)
- [add pytest](#add-pytest)
- [measure coverage](#measure-coverage)
- [test exception](#test-exception)
- [reproducible random values with factory-boy](#reproducible-random-values-with-factory-boy)
- [unique values with factory-boy](#unique-values-with-factory-boy)
- [set database extension for case-insensitive](#set-database-extension-for-case-insensitive)
- [check migration](#check-migration)
- [dump fixtures](#dump-fixtures)
- [load all fixtures](#load-all-fixtures)
- [add django debug toolbar](#add-django-debug-toolbar)
- [create custom user model when app has data in database](#create-custom-user-model-when-app-has-data-in-database)
- [setup redis](#setup-redis)
- [setup celery](#setup-celery)
- [setup logging](#setup-logging)
- [setup debug & profiling](#setup-debug--profiling)
- [setup GitHub/Actions](#setup-githubactions)

[Intial React setup](#intial-react-setup)

[Intial Docker setup](#intial-docker-setup)

[Deploy AWS](#deploy-aws)

# Run app
```bash
git clone https://github.com/veledzimovich-iTechArt/todo
cd todo
mv backend/env backend/.env
docker compose build
docker compose up
```


# Run tests
```bash
docker compose up
docker exec todo_api coverage run --source='.' -m pytest .
```

# Django Admin (optional)
```bash
# http://localhost:8000/admin
docker compose exec todo_api python manage.py changepassword admin
```

# Initial Django setup

## Create project
```bash
mkdir todo
cd todo/
python3 -m venv venv-django
source venv-django/bin/activate
mkdir backend
# common
pip3 install django djangorestframework django-cors-headers celery django-redis psycopg2 python-dotenv pytest-django factory-boy pytest coverage
pip3 freeze > backend/requirements.txt
# dev
pip3 install autopep8 flake8 pycodestyle memory_profiler django-debug-toolbar pytest-cov
pip3 freeze > backend/requirements-dev.txt
cd backend/
# Note the trailing '.' character
django-admin startproject api .
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

## Add env file
```bash
touch backend/env
```
```env
# generate your own SECRET_KEY
# django.core.management.utils.get_random_secret_key()
SECRET_KEY='12345'
DEBUG=True
# LOCAL Database
DATABASE_NAME=todo
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432
DATABASE_CONN_MAX_AGE=600

# REDIS
REDIS_HOST=127.0.0.1
```

1. api/settings.py
```python
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = bool(os.environ.get('DEBUG'))
# this is the host that Docker uses to run application
ALLOWED_HOSTS = ['localhost', '0.0.0.0', 'api', '16.16.217.216']

AUTH_USER_MODEL = 'users.User'
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
    'http://0.0.0.0:80',
]
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://0.0.0.0:80',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.environ.get('DATABASE_PORT'),
        'CONN_MAX_AGE': int(os.environ.get('DATABASE_CONN_MAX_AGE'))
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
7. api/urls.py
8. First run
```bash
python manage.py makemigrations
python manage.py migrate

python manage.py createsuperuser --email a.veledzimovich@itechart-group.com --username admin
# password: test12345
python manage.py runserver
```

## Add owner to the Todo app
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
        IsOwnerOrAdminReadOnly
    ]

    def get_queryset(self) -> QuerySet:
        tags = self.request.query_params.getlist('tags')
        filtered = (
            {}
            if self.request.user.is_superuser else
            {'owner_id': self.request.user.id}
        )
        queryset = (
            Todo.objects
            .filter(**filtered)
            .select_related('owner')
            .prefetch_related('tags')
        )
        return (
            queryset.filter(tags__id__in=tags).distinct()
            if tags else queryset
        )

    def perform_create(self, serializer: TodoSerializer) -> None:
        serializer.validated_data['owner'] = self.request.user
        super().perform_create(serializer)
```
3. api/urls.py
```python
urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]
```
4. cards/permissions.py
```python
class IsOwnerOrAdminReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        # Read permissions are allowed to admin,

        if request.method in permissions.SAFE_METHODS:
            return request.user.is_superuser

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user
```

## Add user auth
### [Sesssion based](https://kylebebak.github.io/post/django-rest-framework-auth-csrf)
1. api.settings.py
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
2. users/serializers.py
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
5. api.settings.py
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
8. Use X-CSRFToken in Postman's requests


# HOW TO

## add pythom interpreter VScode
Python: select interpreter > Enter interpreter path > Find

## fix 301 status
edit api.settings.py and add '/' in React requests axios.get("/api/todos/")
```python
APPEND_SLASH = False
```

## remove admin
```bash
python3 backend/manage.py shell
```
```python
from django.contrib.auth.models import User
User.objects.get(username='admin', is_superuser=True).delete()
```

## reset migration
```bash
# all
python3 backend/manage.py flush
# app
python backend/manage.py migrate users zero
```

## add pytest
```bash
pip3 install pytest-django factory-boy
touch backend/pytest.ini
```
pytest.ini
```ini
[pytest]
DJANGO_SETTINGS_MODULE = api.settings
python_files = tests.py test_*.py *_tests.py
```

## measure coverage
1. Install coverage
```bash
pip3 install coverage
```
2. Run coverage
```bash
coverage run --source='.' -m pytest backend
coverage run --source='.' -m unittest discover backend
coverage run --source='.' backend/manage.py test backend
coverage report
coverage html
```
1. Install pytest-cov
```bash
pip3 install pytest-cov
touch backend/.coveragerc
```
2. backend/.coveragerc
```bash
[run]
omit = api/tests/*,api/asgi.py,api/wsgi.py,manage.py,*/migrations/*
[report]
 exclude_lines=
     pragma: no cover
     if TYPE_CHECKING:
```
3. backend/pytest.ini
``` ini
addopts = --cov=.
          --cov-report term-missing:skip-covered
          --cov-fail-under 100
```
4. Run pytests
```bash
pytest -rf .
```
5. Check missing lines
``` bash
---------- coverage: platform darwin, python 3.10.9-final-0 ----------
Name                                Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
cards/models.py                        19      2    89%   16, 30
cards/permissions.py                    6      1    83%   14
-----------------------------------------------------------------
TOTAL                                 875     40    95%
```

## tests exception
```python
class TestLoginView(BaseUserTest):
# ...
    def test_no_user_no_password_serializer_error(self) -> None:
        serializer = LoginSerializer(
            data={
                'username': '',
                'password': ''
            }
        )
        try:
            serializer.validate(serializer.initial_data)
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as err:
            self.assertEqual(
                str(err.detail[0]),
                'Both "username" and "password" are required.'
            )
        else:
            self.fail('ValidationError is not raised')
```

## reproducible random values with factory-boy
```python
import factory.random

def setup_test_environment():
    factory.random.reseed_random('my_awesome_project')
```

## unique values with factory-boy
```python
name = factory.Sequence(lambda n: f'Company {n}')
```

## set database extension for case-insensitive
1. create new template
```bash
psql
\c template1
CREATE EXTENSION citext;
```
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
# if citext added after DB setup
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

## check migration
```bash
# read sql
python3 backend/manage.py sqlmigrate users 0002
# check problems
python backend/manage.py check
```

## dump fixtures
```bash
# all
python3 backend/manage.py dumpdata -o backend/api/initial_data.json
# exclude
python3 backend/manage.py dumpdata --exclude cards.todo --format=json cards > backend/api/initial_data.json
# specific
python3 backend/manage.py dumpdata users.User > backend/users/fixtures/users_data.json
```

## load all fixtures
1. Dump data
```bash
python manage.py dumpdata users.User > backend/users/fixtures/users.json
python manage.py dumpdata cards.Todo > backend/cards/fixtures/todos.json
python manage.py dumpdata cards.Tag > backend/cards/fixtures/tags.json
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
3. api/settings.py
```python
PROJECT_APPS = [
    # core app created for manage fixtures
    'core',
    # ...
]
```
4. docker-compose.yaml
```yaml
    # ...
    # comment python manage.py load_all_data if needed
    command: >
      bash -c "python manage.py migrate &&
              python manage.py load_all_data &&
              python manage.py runserver 0.0.0.0:8000"
    # ...
```

## add django debug toolbar
1. api/settings.py
```python
DEBUG_APPS = [app for app in ['debug_toolbar'] if DEBUG]
INSTALLED_APPS = [
    # ...
    *DEBUG_APPS,
    # ...
]
MIDDLEWARE = [
    *[app for app in ['debug_toolbar.middleware.DebugToolbarMiddleware'] if DEBUG],
    # ...
]

if DEBUG:
    INTERNAL_IPS = [
        '127.0.0.1'
    ]
    # add django-debug-toolbar in docker
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())

    INTERNAL_IPS += ['.'.join(ip.split('.')[:-1] + ['1']) for ip in ips]
```
2. api/urls.py
```python
from django.conf import settings
from django.urls import path, include

urlpatterns = [
    # ...
    path('__debug__/', include('debug_toolbar.urls')),
]
```

## create custom user model when app has data in database
1. api.settings.py
```python
AUTH_USER_MODEL = 'auth.User'
```
2. Reset migrations
```bash
python manage.py migrate auth zero
python manage.py migrate admin zero
python manage.py migrate contenttypes zero
python manage.py migrate sessions zero
# manually remove DB tables for auth admin contenttypes sessions if they are exist
```
3. Create users app
```bash
python manage.py startapp users
```
3. cards/models.py
```python
# from django.contrib.auth import get_user_model
# same
from api.settings import AUTH_USER_MODEL

class Todo(models.Model):
    # set owner
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
```bash
rm users/migrations/0001_initial.py
```
```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Meta:
        db_table = 'auth_user'
```

6. api.settings.py
```python
AUTH_USER_MODEL = 'users.User'
```
```bash
python manage.py makemigrations
```
cards/migrations/0003_todo_owner.py
```python
# edit migration and set default value for Card owner = 1
field=models.ForeignKey(
    default=1,
    on_delete=django.db.models.deletion.CASCADE,
    related_name='todos',
    to=settings.AUTH_USER_MODEL
),
```
7. Set admin
```bash
python manage.py createsuperuser --email a.veledzimovich@itechart-group.com --username admin
# password: test12345
# check that auth_user id = 1
```
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
```python
# I generally wouldn't recommend renaming anything, because your database structure will become inconsistent.
# Some of the tables will have the users_ prefix, while some of them will have the auth_ prefix.
# But on the other hand, you could argue that the User model is now a part of the users app, so it shouldn't have the auth_ prefix.
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
1. api/settigs.py
```python
INSTALLED_APPS = [
    # ...
    'django_redis',
    # ...
]
REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
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
1. api/settigs.py
```python
INSTALLED_APPS = [
    # ...
    'celery',
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
2. api/__init__.py
```python
# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ('celery_app',)
```
3. api/tasks.py
```python
import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

app = Celery('api')

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
```bash
# macos
celery  -A api worker --loglevel=INFO --concurrency=2 -B -s celerybeat-schedule
```
```bash
# linux
celery -A api worker -l INFO --concurrency=2 -B -s celerybeat-schedule
```

## [setup logging](https://docs.djangoproject.com/en/4.1/topics/logging/)
1. Add logs
```bash
mkdir backend/api/logs
touch backend/api/logs/.gitkeep
```
2. runserver
```bash
python manage.py runserver
```
3. backend/.gitignore
```bash
# ...
# logs
api/logs/celery.log
api/logs/api.log
```

## setup debug & profiling

### pdb
```python
import pdb
pdb.set_trace()
```

### memory_profiler
```python
from memory_profiler import profile
@profile
# ...

# manual run
os.system('mprof run adlynx-backend/manage.py runserver 127.0.0.1:8000')
```

### querylog
api/setting.py
```python
LOGGING = {
    'version': 1,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        # if default LOGGING setup add only this section
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}
```

### querycount
```bash
pip3 install django-querycount
```
api/setting.py
```python
MIDDLEWARE = [
    # ...
    'querycount.middleware.QueryCountMiddleware'
]

QUERYCOUNT = {
    'THRESHOLDS': {
        'MEDIUM': 50,
        'HIGH': 200,
        'MIN_TIME_TO_LOG': 0,
        'MIN_QUERY_COUNT_TO_LOG': 0
    },
    'IGNORE_REQUEST_PATTERNS': [],
    'IGNORE_SQL_PATTERNS': [r'silk_'],
    'DISPLAY_DUPLICATES': None,
    'RESPONSE_HEADER': 'X-DjangoQueryCount-Count'
}
```

### [silk](https://github.com/jazzband/django-silk)

```bash
pip install django-silk
```

temporary disable app
```bash
# remove all migrations
python manage.py migrate silk zero
# comment silk in INSTALLED_APPS and MIDDLEWARE in settings.py
# comment 'silk/' in urlpatterns
```

## setup GitHub/Actions
```bash
mkdir -p .github/workflows
touch .github/workflows/django-rest.yml
```
```yml
name: Django CI

on:
  push:
    branches: [ 'master' ]
  pull_request:
    branches: [ 'master' ]

jobs:
  build:

    runs-on: ubuntu-latest
    strategy:
      max-parallel: 4
      matrix:
        python-version: ['3.11.0']

    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
          POSTGRES_PORT: 5432
        ports:
          - 5432:5432
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5

    env:
        DATABASE_NAME: test
        DATABASE_USER: test
        DATABASE_PASSWORD: test
        DATABASE_HOST: '127.0.0.1'
        DATABASE_PORT: 5432
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r backend/requirements.txt
        pip install pytest-django factory-boy coverage
    - name: Run Migrations
      run: python backend/manage.py migrate
    - name: Run Tests
      run: |
        coverage run --source='.' -m pytest backend
        coverage report
```


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
src/setupProxy.js
```bash
# use dynamic proxy
npm install http-proxy-middleware
touch src/setupProxy.js
echo "REACT_APP_PROXY='http://localhost:8000'" > frontend/.env.local
```


# Intial Docker setup
## Create files
```bash
touch backend/Dockerfile
touch backend/.dockerignore
touch frontend/Dockerfile
touch frontend/.dockerignore
touch docker-compose.yaml
```
```bash
docker-compose build
# user defined name
# docker-compose build -t veledzimovich/todo .
docker-compose up
# daemonize
# docker-compose up -d
# docker-compose logs | less
```
## Check docker-compose.yaml
## [Optimize containers](https://medium.com/nerd-for-tech/bigger-dockerignore-smaller-docker-images-49fa22e51c7)



# Deploy AWS

## Step 1: Create ECR Repositories

We will store the Docker images for frontend and backend in ECR.

1. **Create ECR repository for frontend:**
   ```bash
   aws ecr create-repository \
     --repository-name todo-frontend \
     --region eu-north-1 \
     --profile vention
   ```

2. **Create ECR repository for backend:**
   ```bash
   aws ecr create-repository \
     --repository-name todo-backend \
     --region eu-north-1 \
     --profile vention
   ```

3. **Login Docker to ECR (from your local machine):**
   ```bash
   aws ecr get-login-password --region eu-north-1 --profile vention | \
     docker login --username AWS --password-stdin \
     $(aws sts get-caller-identity --query Account --output text --profile vention).dkr.ecr.eu-north-1.amazonaws.com
   ```

4. **Note the ECR repository URIs:**
   ```bash
   aws ecr describe-repositories \
     --region eu-north-1 \
     --profile vention \
     --query 'repositories[*].repositoryUri'
   ```

### ECR Repository URIs:
- "193542828389.dkr.ecr.eu-north-1.amazonaws.com/todo-frontend"
- "193542828389.dkr.ecr.eu-north-1.amazonaws.com/todo-backend"
---

## Step 2: Build and Push Docker Images (Frontend & Backend)

We build images locally and push them to ECR. We build images locally and push them to ECR.
Later, we will run them on EC2.

**Architecture note:** t3.micro instances is `linux/amd64`

1. **Get your AWS account ID and set ECR base:**
   ```bash
   export AWS_REGION=eu-north-1
   export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text --profile vention)
   export ECR_BASE="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
   ```

2. **Build and push frontend image:**
   ```bash
   cd frontend
   docker build --platform linux/amd64 -t todo-frontend .
   docker tag todo-frontend:latest ${ECR_BASE}/todo-frontend:latest
   docker push ${ECR_BASE}/todo-frontend:latest
   cd ..
   ```

3. **Build and push backend image:**
   ```bash
   cd backend
   docker build --platform linux/amd64 -t todo-backend .
   docker tag todo-backend:latest ${ECR_BASE}/todo-backend:latest
   docker push ${ECR_BASE}/todo-backend:latest
   cd ..
   ```

---

## Step 3: Create VPC and Networking

Below are CLI commands for a minimal VPC setup

1. **Create VPC:**
   ```bash
   aws ec2 create-vpc \
     --cidr-block 10.0.0.0/16 \
     --region eu-north-1 \
     --profile vention \
     --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=todo-vpc-free}]'
   ```

   Note the VPC ID and export it:
   ```bash
   export VPC_ID=vpc-0c3350b63d2dbb005
   ```

2. **Create Internet Gateway and attach to VPC:**
   ```bash
   aws ec2 create-internet-gateway \
     --region eu-north-1 \
     --profile vention \
     --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=todo-igw-free}]'
   ```

   Note the Internet Gateway ID:
   ```bash
   export IGW_ID=igw-03955857a46516bcd
   ```

   Attach:
   ```bash
   aws ec2 attach-internet-gateway \
     --internet-gateway-id ${IGW_ID} \
     --vpc-id ${VPC_ID} \
     --region eu-north-1 \
     --profile vention
   ```

3. **Create public subnet:**
   ```bash
   # Public Subnet 1 in eu-north-1a
   aws ec2 create-subnet \
     --vpc-id ${VPC_ID} \
     --cidr-block 10.0.1.0/24 \
     --availability-zone eu-north-1a \
     --region eu-north-1 \
     --profile vention \
     --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=todo-public-subnet-1a-free}]'

   # Public Subnet 2 in eu-north-1b
   aws ec2 create-subnet \
     --vpc-id ${VPC_ID} \
     --cidr-block 10.0.2.0/24 \
     --availability-zone eu-north-1b \
     --region eu-north-1 \
     --profile vention \
     --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=todo-public-subnet-1b-free}]'
   ```

   Note the subnet IDs:
   ```bash
   export PUBLIC_SUBNET_1_ID=subnet-0ca52ff27c6af369e
   export PUBLIC_SUBNET_2_ID=subnet-0f9dd5215859e6fa9
   ```

4. **Enable auto‑assign public IP for both public subnets:**
   ```bash
   aws ec2 modify-subnet-attribute \
     --subnet-id ${PUBLIC_SUBNET_1_ID} \
     --map-public-ip-on-launch \
     --region eu-north-1 \
     --profile vention

   aws ec2 modify-subnet-attribute \
     --subnet-id ${PUBLIC_SUBNET_2_ID} \
     --map-public-ip-on-launch \
     --region eu-north-1 \
     --profile vention
   ```

5. **Create a public route table and route to Internet Gateway:**
   ```bash
   aws ec2 create-route-table \
     --vpc-id ${VPC_ID} \
     --region eu-north-1 \
     --profile vention \
     --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=todo-public-rt-free}]'
   ```

   Note the route table ID:
   ```bash
   export PUBLIC_RT_ID=rtb-0eae2e631179047ed
   ```

   Add default route:
   ```bash
   aws ec2 create-route \
     --route-table-id ${PUBLIC_RT_ID} \
     --destination-cidr-block 0.0.0.0/0 \
     --gateway-id ${IGW_ID} \
     --region eu-north-1 \
     --profile vention
   ```

6. **Associate both public subnets with the public route table:**
   ```bash
   aws ec2 associate-route-table \
     --subnet-id ${PUBLIC_SUBNET_1_ID} \
     --route-table-id ${PUBLIC_RT_ID} \
     --region eu-north-1 \
     --profile vention

   aws ec2 associate-route-table \
     --subnet-id ${PUBLIC_SUBNET_2_ID} \
     --route-table-id ${PUBLIC_RT_ID} \
     --region eu-north-1 \
     --profile vention
   ```

**Summary:**
- ✅ 1 VPC
- ✅ 2 public subnets (one in each AZ)
- ✅ Internet Gateway
- ✅ Route table with `0.0.0.0/0` → IGW

                    Internet
                       |
                Internet Gateway
                       |
                      VPC
                 10.0.0.0/16
                       |
         --------------------------------
         |                              |
   Public Subnet                    Public Subnet
     10.0.1.0/24                     10.0.2.0/24
   eu-north-1a                     eu-north-1b
         |                              |
     Servers                         Servers
   (public IP)                     (public IP)

---

## Step 4: Create Security Group for EC2 Instance

The EC2 instance will host both frontend and backend containers.
We need a security group to allow HTTP (and optional SSH) access.

1. **Create security group:**
   ```bash
   aws ec2 create-security-group \
     --group-name todo-ec2-sg \
     --description "Security group for todo EC2 instance" \
     --vpc-id ${VPC_ID} \
     --region eu-north-1 \
     --profile vention
   ```

   Note the security group ID:
   ```bash
   export EC2_SG_ID=sg-053d2ea483aaa4450
   ```

2. **Allow HTTP from anywhere (port 80):**
   ```bash
   aws ec2 authorize-security-group-ingress \
     --group-id ${EC2_SG_ID} \
     --protocol tcp \
     --port 80 \
     --cidr 0.0.0.0/0 \
     --region eu-north-1 \
     --profile vention
   ```

3. **(Optional but recommended) Allow SSH only from your IP:**
   ```bash
   MY_IP=$(curl -s https://checkip.amazonaws.com)/32

   aws ec2 authorize-security-group-ingress \
     --group-id ${EC2_SG_ID} \
     --protocol tcp \
     --port 22 \
     --cidr ${MY_IP} \
     --region eu-north-1 \
     --profile vention
   ```

User browser
      |
Internet
      |
Security Group (Firewall)
      |
EC2 Server

Port 80 → allowed
Port 22 → allowed only from your IP
Other ports → blocked

---

## Step 5: Create IAM Role for EC2

1. **Create trust policy file for EC2:**
   ```bash
   cat > ec2-instance-trust-policy.json <<EOF
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Service": "ec2.amazonaws.com"
         },
         "Action": "sts:AssumeRole"
       }
     ]
   }
   EOF
   ```

2. **Create the EC2 role:**
   ```bash
   aws iam create-role \
     --role-name todo-ec2-role \
     --assume-role-policy-document file://ec2-instance-trust-policy.json \
     --profile vention
   ```

3. **Attach ECR access policy:**

   # Allow the EC2 instance role to authenticate to ECR and pull images
   aws iam attach-role-policy \
     --role-name todo-ec2-role \
     --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly \
     --profile vention
   ```

4. **Create instance profile and attach the role:**
   ```bash
   aws iam create-instance-profile \
     --instance-profile-name todo-ec2-instance-profile \
     --profile vention

   aws iam add-role-to-instance-profile \
     --instance-profile-name todo-ec2-instance-profile \
     --role-name todo-ec2-role \
     --profile vention
   ```

EC2 Instance
     │
     ▼
Instance Profile
     │
     ▼
IAM Role (todo-ec2-role)
     │
     ▼
Permission: Read from ECR

---

## Step 6: Create Key Pair and Launch EC2 Instance

1. Create a key pair (if you don’t have one)

    ```bash
    aws ec2 create-key-pair \
    --key-name todo-key \
    --query 'KeyMaterial' \
    --output text > todo-key.pem \
    --region eu-north-1 \
    --profile vention

    chmod 400 todo-key.pem
    ```

2. Find a free AMI (Amazon Machine Images)

    - In the AWS Console, go to **EC2 → AMIs** and pick:
    - Owner: **Amazon**
    - Architecture: **x86_64**
    - Type: **Amazon Linux 2** or **Amazon Linux 2023**

    Note the AMI ID (e.g., `ami-xxxxxxxxxxxxxxxxx`).

    ```bash
    export AMI_ID=ami-0aaa636894689fa47
    ```

3. Launch the EC2 instance t3.micro

    ```bash
    aws ec2 run-instances \
    --image-id ${AMI_ID} \
    --instance-type t3.micro \
    --key-name todo-key \
    --security-group-ids ${EC2_SG_ID} \
    --subnet-id ${PUBLIC_SUBNET_1_ID} \
    --associate-public-ip-address \
    --iam-instance-profile Name=todo-ec2-instance-profile \
    --count 1 \
    --region eu-north-1 \
    --profile vention
    ```

    Note the Instance ID once the instance is running.

    ```bash
    export INSTANCE_ID=i-0e0febf69a65d9a09
    ```

    ```bash
    aws ec2 describe-instances \
    --instance-ids ${INSTANCE_ID} \
    --region eu-north-1 \
    --profile vention \
    --query 'Reservations[0].Instances[0].[PublicIpAddress,PublicDnsName]' \
    --output text
    ```

    Note the Public IP

    ```bash
    # Check ALLOWED_HOSTS in Django
    export PUBLIC_IP=16.16.217.216
    ```

    **Free tier note:** t3.micro should be free (750 hours/month for the first 12 months of a new account).


## Step 7: SSH into EC2 and Install Docker

1. **SSH into the instance:**
   ```bash
   ssh -i todo-key.pem ec2-user@${PUBLIC_IP}
   ssh -i ./todo-key.pem -o IdentitiesOnly=yes ec2-user${PUBLIC_IP} -v
   ```

   ```bash
   # check connection (optional)
   nc -vz ${PUBLIC_IP} 22
   ```

2. **Install Docker (Amazon Linux 2 example):**
   ```bash
   sudo yum update -y
   sudo amazon-linux-extras install docker -y || sudo yum install docker -y
   sudo service docker start
   sudo usermod -aG docker ec2-user
   ```

3. **(Optional) Log out and back in** so your user picks up the `docker` group membership:
   ```bash
   exit
   ssh -i todo-key.pem ec2-user@${PUBLIC_IP}
   ```


4. **Verify Docker:**
   ```bash
   docker ps
   ```


## Step 8: Pull Images from ECR and Run Containers

On the EC2 instance, we will:
- Authenticate Docker to ECR
- Pull the frontend and backend images
- Create a Docker network
- Run all containers on the same instance

1. **Set region on EC2** (AWS CLI and SDKs will automatically use the EC2 instance role created in Step 5):
   ```bash
   export AWS_REGION=eu-north-1
   ```

2. **Get account ID and ECR base on EC2 (using the instance role):**
   ```bash
   export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
   export ECR_BASE="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
   ```

3. **Login Docker to ECR (from EC2):**
   ```bash
   aws ecr get-login-password --region ${AWS_REGION} | \
     docker login --username AWS --password-stdin \
     ${ECR_BASE}
   ```

4. **Pull images:**
   ```bash
   docker pull ${ECR_BASE}/todo-frontend:latest
   docker pull ${ECR_BASE}/todo-backend:latest
   ```

5. **Create Docker network (to mirror `docker-compose.yml`):**
   ```bash
   docker network create todo-network || true
   ```

6. **Run Postgres**

    Same AMI as backend

    ```bash
    docker run -d \
    --name todo_db \
    --network todo-network \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_DB=todo \
    -v todo_postgres_data:/var/lib/postgresql/data \
    postgres:15-alpine
    ```

    AWS RDS

    Create RDS without connection to EC2

    ```bash
    export RDS=todo.cxsmy20q6rs4.eu-north-1.rds.amazonaws.com
    ```

    Create connections with security group

    ```bash
    # Create Postgres container
    docker run -d \
    --name todo_postgres \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=postgres \
    postgres:15-alpine
    # Exists
    docker exec -it todo_postgres sh
    ```
    ```bash
    apk add --no-cache bind-tools
    nslookup ${RDS}
    ping -c 3 ${RDS}

    # Check if RDS is accessible
    apk add --no-cache busybox-extras
    nc -zv ${RDS} 5432

    ```


7. **Run Redis**
    ```bash
    docker run -d \
    --name todo_redis \
    --network todo-network \
    redis:7-alpine
    ```
7. **Run backend containers:**

    Same AMI as backend

    ```bash
    docker run -d \
    --name todo_api \
    --network todo-network \
    -e SECRET_KEY='django-insecure-o_x)+$!uv!wu3^lhr^fr0h#osdp#4pe%cojq!io@t$11-u^xt8' \
    -e DEBUG=False \
    -e DATABASE_NAME=todo \
    -e DATABASE_USER=postgres \
    -e DATABASE_PASSWORD=postgres \
    -e DATABASE_HOST=todo_db \
    -e DATABASE_PORT=5432 \
    -e DATABASE_CONN_MAX_AGE=600 \
    -e REDIS_HOST=todo_redis \
    -p 8000:8000 \
    ${ECR_BASE}/todo-backend:latest \
    bash -c "python manage.py migrate && \
        python manage.py collectstatic --noinput && \
        python manage.py load_all_data && \
        python manage.py runserver 0.0.0.0:8000"
    ```

    ```bash
    docker run -d \
    --name todo_celery \
    --network todo-network \
    -e SECRET_KEY='django-insecure-o_x)+$!uv!wu3^lhr^fr0h#osdp#4pe%cojq!io@t$11-u^xt8' \
    -e DEBUG=False \
    -e DATABASE_NAME=todo \
    -e DATABASE_USER=postgres \
    -e DATABASE_PASSWORD=postgres \
    -e DATABASE_HOST=todo_db \
    -e DATABASE_PORT=5432 \
    -e DATABASE_CONN_MAX_AGE=600 \
    -e REDIS_HOST=todo_redis \
    ${ECR_BASE}/todo-backend:latest \
    celery -A api worker -l INFO --concurrency=2 -B -s celerybeat-schedule
    ```

    AWS RDS

    ```bash
    docker run -d \
    --name todo_api \
    --network todo-network \
    -e SECRET_KEY='django-insecure-o_x)+$!uv!wu3^lhr^fr0h#osdp#4pe%cojq!io@t$11-u^xt8' \
    -e DEBUG=False \
    -e DATABASE_NAME=todo \
    -e DATABASE_USER=postgres \
    -e DATABASE_PASSWORD=postgres\
    -e DATABASE_HOST=todo.cxsmy20q6rs4.eu-north-1.rds.amazonaws.com \
    -e DATABASE_PORT=5432 \
    -e DATABASE_CONN_MAX_AGE=600 \
    -e REDIS_HOST=todo_redis \
    -p 8000:8000 \
    ${ECR_BASE}/todo-backend:latest \
    bash -c "python manage.py migrate && \
        python manage.py collectstatic --noinput && \
        python manage.py load_all_data && \
        python manage.py runserver 0.0.0.0:8000"
    ```

    ```bash
    docker run -d \
    --name todo_celery \
    --network todo-network \
    -e SECRET_KEY='django-insecure-o_x)+$!uv!wu3^lhr^fr0h#osdp#4pe%cojq!io@t$11-u^xt8' \
    -e DEBUG=False \
    -e DATABASE_NAME=todo \
    -e DATABASE_USER=postgres \
    -e DATABASE_PASSWORD=postgres \
    -e DATABASE_HOST=todo.cxsmy20q6rs4.eu-north-1.rds.amazonaws.com \
    -e DATABASE_PORT=5432 \
    -e DATABASE_CONN_MAX_AGE=600 \
    -e REDIS_HOST=todo_redis \
    ${ECR_BASE}/todo-backend:latest \
    celery -A api worker -l INFO --concurrency=2 -B -s celerybeat-schedule
    ```

    # Dump DB
    ```bash
    pg_dump \
    -h todo.cxsmy20q6rs4.eu-north-1.rds.amazonaws.com \
    -U postgres \
    -d todo \
    -F c \
    -f todo_aws.dump

    docker cp todo_postgres:todo_aws.dump ~/todo_aws.dump
    ```
    # Copy to local machine
    ```bash
    scp -i todo-key.pem ec2-user@${PUBLIC_IP}:~/todo_aws.dump .
    ```

   The backend will automatically use the **EC2 instance role** (`todo-ec2-role`) for AWS credentials (thanks to the IAM setup in Step 5).

8. **Run frontend container (Nginx):**
    ```bash
    docker run -d \
        --name todo_web \
        --network todo-network \
        -p 80:80 \
        ${ECR_BASE}/todo-frontend:latest
    ```
    ```bash
    # check ports
    docker exec -it todo_web netstat -tulpn
    ```

   The frontend container uses Nginx configuration that proxies API calls to the backend container through the Docker network.

9. **Verify containers are running:**
   ```bash
   docker ps
   ```

---

## Step 9: Test Deployment

1. **Get the EC2 public IP** from the AWS Console or via CLI:
   ```bash
   aws ec2 describe-instances \
     --instance-ids ${INSTANCE_ID} \
     --region eu-north-1 \
     --profile vention \
     --query 'Reservations[0].Instances[0].PublicIpAddress' \
     --output text
   ```

2. **Access the application in your browser:**
   - Frontend: `http://16.16.217.216/`

---

## Step 11: Updating the Application (Rebuild & Redeploy)

1. **Rebuild and push images from your local machine** (Strp 1 + Step 2).
2. **SSH into EC2**:
    ```bash
    export PUBLIC_IP=16.16.217.216
    ```
    ```bash
    ssh -i todo-key.pem ec2-user@${PUBLIC_IP}
    ```
    ```bash
    docker stop todo_api todo_celery todo_web todo_db todo_redis
    docker rm todo_api todo_celery todo_web todo_db todo_redis
    ```
3. **Update containers** (Step 8)

---

## Step 12: Cleanup

When you no longer need the environment, clean up to avoid any accidental charges:

**Stop and terminate EC2 instance:**
   ```bash
   aws ec2 terminate-instances \
     --instance-ids ${INSTANCE_ID} \
     --region eu-north-1 \
     --profile vention
   ```
