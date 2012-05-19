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
    'django_hosts.tests',
    'django_nose',
]

ROOT_URLCONF = 'django_hosts.tests.urls.root'

SITE_ID = 1

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

SECRET_KEY = 'something-something'
