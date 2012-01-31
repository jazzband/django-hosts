import codecs
from os import path
from setuptools import setup, find_packages

read = lambda filepath: codecs.open(filepath, 'r', 'utf-8').read()

setup(
    name='django-hosts',
    description="Dynamic and static hosts support for Django.",
    long_description=read(path.join(path.dirname(__file__), 'README.rst')),
    version='0.4.1',
    url='http://django-hosts.rtfd.org/',
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    license='BSD',
    packages=find_packages(),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
