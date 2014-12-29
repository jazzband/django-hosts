DATABASE_ENGINE = 'sqlite3'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django_hosts',
    'tests',
]

ROOT_URLCONF = 'tests.urls.root'

SITE_ID = 1

SECRET_KEY = 'something-something'

MIDDLEWARE_CLASSES = []
