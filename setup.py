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
    install_requires = ['django >= 1.1, <1.4'],
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
