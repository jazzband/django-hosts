from setuptools import setup, find_packages

setup(
    name='django-hosts',
    description="Dynamic and static hosts support for Django.",
    version='0.1',
    url='https://github.com/jezdez/django-hosts',

    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    license='BSD',

    packages=find_packages(),
    package_data={
        'hosts': [
            'contrib/toolbar/templates/hosts/*.html',
        ],
    },
)
