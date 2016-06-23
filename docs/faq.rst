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
