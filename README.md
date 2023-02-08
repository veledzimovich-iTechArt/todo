# todo

## DjangoRest

# Content

[Run app](#run-app)

[Run tests](#run-tests)

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
REDIS_HOST='127.0.0.1'
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
ALLOWED_HOSTS = ['localhost', '0.0.0.0', 'api']

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
    'http://0.0.0.0:3000',
]
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://0.0.0.0:3000',
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

