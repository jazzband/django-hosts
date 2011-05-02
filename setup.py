#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-dynamic-subdomains',
    description="Dynamic and static subdomain support for Django.",
    version='0.1',
    url='http://code.playfire.com/',

    author='Playfire.com',
    author_email='tech@playfire.com',
    license='BSD',

    packages=find_packages(),
    package_data={
        'dynamic_subdomains': [
            'templates/*/*.html',
        ],
    },
)
