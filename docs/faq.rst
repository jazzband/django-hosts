===
FAQ
===

Does django-hosts work with the Django Debug Toolbar?
-----------------------------------------------------

Yes, django-hosts works with `Django Debug toolbar`_ with the only
limitation that the toolbar's middleware has to be come *after*
the middleware of django-hosts, e.g.:

.. code-block:: python

    MIDDLEWARE_CLASSES = (
        # your other middlewares..

        'django_hosts.middleware.HostsMiddleware',
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

Also, you've at least installed `django-debug-toolbar 0.9.X`_ or higher.

.. _`Django Debug toolbar`: https://github.com/django-debug-toolbar/django-debug-toolbar/
.. _`django-debug-toolbar 0.9.X`: http://pypi.python.org/pypi/django-debug-toolbar