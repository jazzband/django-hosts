Template tags
=============

.. currentmodule:: django_hosts.templatetags.hosts

.. function:: host_url(view_name, [view_args, view_kwargs], host_name, [host_args, host_kwargs, as_var])

Now if you want to actually refer to the full URLs in your templates
you can use the included ``host_url`` template tag. So imagine having a
host pattern of::

    from django.conf import settings
    from django_hosts import patterns, host

    host_patterns = patterns('',
        host(r'admin', settings.ROOT_URLCONF, name='our-admin'),
    )

and a ``ROOT_URLCONF`` of::

    from django.conf.urls.defaults import patterns, url

    urlpatterns = patterns('mysite.admin',
        url(r'^dashboard/$', 'dashboard', name='dashboard'),
    )

then this example will create a link to the admin dashboard:

.. code-block:: html+django

    {% load hosts %}

    <a href="{% host_url dashboard on our-admin %}">Admin dashboard</a>

which will be rendered as:

.. code-block:: html+django

    <a href="//admin/dashboard/">Admin dashboard</a>

.. note::

    The double slash at the beginning of the href is an easy way
    to not have to worry about which scheme (http or https) is used.
    Your browser will automatically choose the currently used scheme.
    If you're on ``https://mysite.com/`` a link with an href
    of ``//mysite.com/about/`` would actually point to
    ``https://mysite.com/about/``.

    For more information see the `The protocol-relative URL`_ article
    by Paul Irish or the appropriate `section in RFC 3986`_.

.. _asvar:

Setting a context variable
--------------------------

.. versionadded:: 0.4.0

If you'd like to retrieve a URL without displaying it, you can save the
result of the template tag in a template variable and use it later on, e.g.:

.. code-block:: html+django

    {% load hosts %}

    {% host_url homepage as homepage_url %}
    <a href="{{ homepage_url }}" title="Go back to {{ homepage_url }}">Home</a>

.. _fqdn:

Fully qualified domain names (FQDN)
-----------------------------------

In case you want to append a default domain name to the domain part of
the rendered URL you can simply set the
:attr:`~django.conf.settings.PARENT_HOST`, e.g::

    PARENT_HOST = 'example.com'

This would render the link of the previous section as:

.. code-block:: html+django

    <a href="//admin.example.com/dashboard/">Admin dashboard</a>

Alternatively -- in case you don't want to append this parent domain
to all URLs you can also spell out the domain in the host pattern::

    from django.conf import settings
    from django_hosts import patterns, host

    host_patterns = patterns('',
        host(r'admin\.example\.com', settings.ROOT_URLCONF, name='admin'),
    )

Host and URL parameters
-----------------------

If your host pattern contains an parameter (or keyed parameter), like::

    from django.conf import settings
    from django_hosts import patterns, host

    host_patterns = patterns('',
        host(r'www', settings.ROOT_URLCONF, name='homepage'),
        host(r'(\w+)', 'path.to.support_urls', name='wildcard'),
        host(r'(?P<username>\w+)', 'path.to.user_urls', name='user-area'),
    )

you can also easily pass parameters to the
:func:`~django_hosts.templatetags.hosts.host_url` template tag:

.. code-block:: html+django

    {% load hosts %}

    <a href="{% host_url user-dashboard on user-area username='johndoe' %}">John's dashboard</a>
    <a href="{% host_url faq-index on wildcard 'help' %}">FAQ</a>

Which will be rendered (with a :attr:`~django.conf.settings.PARENT_HOST` of
``'example.com'``) as:

.. code-block:: html+django

    <a href="//johndoe.example.com/">John's dashboard</a>
    <a href="//help.example.com/faq/">FAQ</a>

.. _The protocol-relative URL: http://paulirish.com/2010/the-protocol-relative-url/
.. _section in RFC 3986: http://tools.ietf.org/html/rfc3986#section-4.2
