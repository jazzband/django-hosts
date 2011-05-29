#!/usr/bin/env python
import os
import sys
import coverage
from os.path import join

from django.conf import settings
from django.core.management import call_command

here = os.path.dirname(os.path.abspath(__file__))

if not settings.configured:
    settings.configure(
        DATABASE_ENGINE='sqlite3',
        INSTALLED_APPS=[
            'hosts',
        ],
    )

from django.test.simple import run_tests


def runtests(*test_args):
    if not test_args:
        test_args = ['hosts']
    cov = coverage.coverage(branch=True,
        include=[join(here, 'hosts', '*.py')],
        omit=[join(here, 'hosts', 'tests', '*.py')])
    cov.load()
    cov.start()
    failures = run_tests(test_args, verbosity=1, interactive=True)
    cov.stop()
    cov.save()
    sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
