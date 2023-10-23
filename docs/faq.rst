FAQ
===

Does django-hosts work with the Django Debug Toolbar?
-----------------------------------------------------

Yes, django-hosts works with `Django Debug toolbar`_ with the only
limitation that the toolbar's middleware has to be come *after*
django-hosts' ``HostsRequestMiddleware`` middleware, e.g.:

.. code-block:: python

    MIDDLEWARE = (
        'django_hosts.middleware.HostsRequestMiddleware',
        # your other middlewares..
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        'django_hosts.middleware.HostsResponseMiddleware',
    )

Also, you have to install `django-debug-toolbar 0.9.X`_ or higher.

.. _`Django Debug toolbar`: https://github.com/django-debug-toolbar/django-debug-toolbar/
.. _`django-debug-toolbar 0.9.X`: http://pypi.python.org/pypi/django-debug-toolbar

How to use it with i18n?
------------------------

There are multiple approaches to use django-hosts together with :func:`~django.conf.urls.i18n.i18n_patterns`;
here is one.

Given a project using the :mod:`django.contrib.admin`, a mono-lingual blog and a multi-lingual website,
each on their own subdomain, using a structure like::

   ├── mysite
   │   ├── hosts.py
   │   ├── __init__.py
   │   ├── settings.py
   │   ├── urls.py
   │   └── wsgi.py
   ├── blog
   │   ├── admin.py
   │   ├── apps.py
   │   ├── __init__.py
   │   ├── models.py
   │   ├── urls.py
   │   └── views.py
   └── www
       ├── admin.py
       ├── apps.py
       ├── __init__.py
       ├── models.py
       ├── urls_i18n.py
       ├── urls.py
       └── views.py

* :file:`mysite/settings.py`:

  .. code-block:: python

     # ...
     ROOT_HOSTCONF = 'mysite.hosts'
     DEFAULT_HOST = 'www'
     PARENT_HOST = 'example.net'


* :file:`mysite/hosts.py`:

  .. code-block:: python

     from django.conf import settings
     from django_hosts import patterns, host

     host_patterns = patterns(
         '',
         # will answer to www.example.net and example.net
         host('(?:www|)', 'www.urls_i18n', name='www'),
         # will answer to blog.example.net
         host('blog', 'blog.urls', name='blog'),
         # will answer to admin.example.net
         host('admin', settings.ROOT_URLCONF, name='admin'),
     )

* :file:`mysite/urls.py`:

  .. code-block:: python

     from django.contrib import admin
     from django.urls import include
     from django.urls import path

     urlpatterns = [
         path('', admin.site.urls),
         path('', include('blog.urls')),
         path('', include('www.urls')),
     ]

* :file:`blog/urls.py`:

  .. code-block:: python

     from django.urls import path

     from . import views

     app_name = 'blog'

     urlpatterns = [
         path('', views.index, name='index'),
     ]

Reversing URL:

.. code-block:: pycon

   from django_hosts.resolvers import reverse
   >>> reverse('admin:login', host='admin')
   '//admin.example.net/login/'
   >>> reverse('blog:index', host='blog')
   '//blog.example.net/en-us/'
   >>> reverse('www:index', host='www')
   '//example.net/en-us/'
