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

Also, currently (2012/01/01) django-hosts only works well
together with the `development version`_ (the upcoming 0.9.X) of
Django Debug toolbar.


.. _`Django Debug toolbar`: https://github.com/django-debug-toolbar/django-debug-toolbar/
.. _`development version`: https://github.com/django-debug-toolbar/django-debug-toolbar/