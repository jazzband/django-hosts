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

If you're using any version older than 1.7 you'll need to extend Django's
cache middleware to make sure the cache keys are correctly generated using
the request's host **and** the request's path. Here's how to do that:

.. code-block:: python

    from django.conf import settings
    from django.middleware.cache import (UpdateCacheMiddleware,
                                         FetchFromCacheMiddleware)

    class HostUpdateCacheMiddleware(UpdateCacheMiddleware):
        def process_response(self, request, response):
            self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX + request.get_host()
            return super(HostUpdateCacheMiddleware, self).process_response(request, response)

    class HostFetchFromCacheMiddleware(FetchFromCacheMiddleware):
        def process_request(self, request):
            self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX + request.get_host()
            return super(HostFetchFromCacheMiddleware, self).process_request(request)

Save those middlewares somewhere in your site's code and refer to them in the
``MIDDLEWARE_CLASSES`` setting instead of Django's originals.
