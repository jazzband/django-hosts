DATABASE_ENGINE = 'sqlite3'

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django_hosts',
    'django_hosts.tests',
    'django_jenkins',
]

ROOT_URLCONF = 'django_hosts.tests.urls.root'

SITE_ID = 1

JENKINS_TASKS = (
    'django_jenkins.tasks.run_pyflakes',
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.django_tests',
)
