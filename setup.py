import codecs
from os import path
from setuptools import setup, find_packages


def read(*parts):
    filename = path.join(path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()

setup(
    name='django-hosts',
    description='Dynamic and static host resolving for Django. '
                'Maps hostnames to URLconfs.',
    long_description=read('README.rst'),
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    url='https://django-hosts.readthedocs.io/',
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    license='BSD',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
