FAQ
===

Does django-hosts work with the Django Debug Toolbar?
-----------------------------------------------------

Yes, django-hosts works with `Django Debug toolbar`_ with the only
limitation that the toolbar's middleware has to be come *after*
django-hosts' ``HostsRequestMiddleware`` middleware, e.g.:

.. code-block:: python

    MIDDLEWARE_CLASSES = (
        'django_hosts.middleware.HostsRequestMiddleware',
        # your other middlewares..
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        'django_hosts.middleware.HostsResponseMiddleware',
    )

Also, you have to install `django-debug-toolbar 0.9.X`_ or higher.

.. _`Django Debug toolbar`: https://github.com/django-debug-toolbar/django-debug-toolbar/
.. _`django-debug-toolbar 0.9.X`: http://pypi.python.org/pypi/django-debug-toolbar

How do I get Django's full page cache working?
----------------------------------------------

When using Django's cache middleware it calculates the cache key using the
request's path, at least until the 1.7 release. So if you're using 1.7 or later
you can stop reading now.

If you're using an older version than 1.7 we'll automatically apply a monkey
patch to the functions in Django that deal with generating the cache keys
to work around the problems with them. They will work the same as the way it
is in Django 1.7. This is neccesary to make sure full page caching works
as intended. See the `commit in Django`_ that fixed the issue there to see what
differs between the old and the new versions of the functions.

.. _`commit in Django`: http://git.io/8Ieptg
