import codecs
import re
import os
import sys
from setuptools import setup, find_packages, Command

def read(*parts):
    return open(os.path.join(os.path.dirname(__file__), *parts)).read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


class RunTests(Command):
    """From django-celery"""
    description = "Run the django test suite from the tests dir."
    user_options = []
    extra_env = {}
    extra_args = []

    def run(self):
        for env_name, env_value in self.extra_env.items():
            os.environ[env_name] = str(env_value)

        this_dir = os.getcwd()
        testproj_dir = os.path.join(this_dir, 'django_hosts', 'tests')
        os.chdir(testproj_dir)
        sys.path.append(testproj_dir)
        from django.core.management import execute_manager
        os.environ['DJANGO_SETTINGS_MODULE'] = os.environ.get(
            'DJANGO_SETTINGS_MODULE', 'django_hosts.test_settings')
        settings_file = os.environ['DJANGO_SETTINGS_MODULE']
        settings_mod = __import__(settings_file, {}, {}, [''])
        prev_argv = list(sys.argv)
        try:
            sys.argv = [__file__, 'test'] + self.extra_args
            execute_manager(settings_mod, argv=sys.argv)
        finally:
            sys.argv = prev_argv

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


setup(
    name='django-hosts',
    description="Dynamic and static hosts support for Django.",
    long_description=read('README.rst'),
    version=find_version("django_hosts", "__init__.py"),
    url='http://django-hosts.rtfd.org/',
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    license='BSD',
    packages=find_packages(),
    cmdclass={"test": RunTests},
    classifiers=[
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
