.. include:: ../README.rst

Usage
-----

Patterns being regular expressions allows setups to feature dynamic (or
"wildcard") host schemes::

    from django.conf import settings
    from django_hosts import patterns, host

    host_patterns = patterns('',
        host(r'www', settings.ROOT_URLCONF, name='www'),
        host(r'(\w+)', 'path.to.custom_urls', name='wildcard'),
    )

Here, requests to ``www.example.com`` will be routed as normal but a
request to ``admin.example.com`` is routed to ``path.to.custom_urls``.

As patterns are matched in order, we placed ``www`` first as it otherwise
would have matched against ``\w+`` and thus routed to the wrong
destination.

Alternatively, we could have used negative lookahead, given the value
of the ``ROOT_URLCONF`` setting::

    from django_hosts import patterns, host

    host_patterns = patterns('',
        host(r'(?!www)\w+', 'path.to.custom_urls', name='wildcard'),
    )

Settings
--------

.. currentmodule:: django.conf.settings


.. attribute:: ROOT_HOSTCONF (required)

    The dotted Python import path of the module containing your host
    patterns. Similar to ``ROOT_URLCONF``.

.. attribute:: DEFAULT_HOST (required)

    The *name* of the host pattern you want to refer to as the default
    pattern. Used if no other host pattern matches or no host name is
    passed to the :func:`~django_hosts.templatetags.hosts.host_url`
    template tag.

.. attribute:: PARENT_HOST (optional)

    The parent domain name to be :ref:`appended to the reversed domain <fqdn>`
    (e.g. using the :func:`~django_hosts.templatetags.hosts.host_url`
    template tag).

.. attribute:: HOST_SITE_TIMEOUT (optional)

    The time to cache the host in the default cache backend, in seconds,
    when using the :func:`~django_hosts.callbacks.cached_host_site` callback.
    Defaults to ``3600``.

Contents
--------

.. toctree::
   :maxdepth: 2

   callbacks
   templatetags
   reference
   changelog
   faq

Issues
------

For any bug reports and feature requests, please use the
`Github issue tracker`_.

Thanks
------

Many thanks to the folks at playfire_ for releasing their
django-dynamic-subdomains_ app, which was the inspiration for this app.

.. _playfire: http://code.playfire.com/
.. _django-dynamic-subdomains: https://github.com/playfire/django-dynamic-subdomains/
.. _`Github issue tracker`: https://github.com/ennio/django-hosts/issues
