Overview
========

This middleware routes requests to specific hosts to different URL
schemes ("hostconf").

For example, if you own ``example.com`` but want to serve specific content
at ``api.example.com`` and ``beta.example.com``, add the following to your
``hosts.py``::

    from django_hosts import patterns, host

    host_patterns = patterns('path.to',
        host(r'api', 'api.urls', name='api'),
        host(r'beta', 'beta.urls', name='beta'),
    )

This causes requests to ``{api,beta}.example.com`` to be routed to their
corresponding URLconf. You can use your ``urls.py`` as a template for these
URLconfs.

Patterns are evaluated in order. If no pattern matches, the request is
processed in the usual way, ie. using ``settings.ROOT_URLCONF``.

Installation
============

- Install the app with your favorite package manager, e.g.::

    pip install django-hosts

- Add ``'django_hosts'`` to your ``INSTALLED_APPS`` setting.

- Add ``'django_hosts.middleware.HostsMiddleware'`` to your
  ``MIDDLEWARE_CLASSES`` setting.

- Create a module containing your default host patterns,
  e.g. in the ``hosts.py`` file next to your ``urls.py``.

- Set the ``ROOT_HOSTCONF`` setting to the dotted Python
  import path of the module containing your default host patterns, e.g.::

    ROOT_HOSTCONF = 'mysite.hosts'

- Set the ``DEFAULT_HOST`` setting to the name of the host pattern you
  want to refer to as the default pattern. It'll be used if no other
  pattern matches or you don't give a name to the ``host_url`` template
  tag (see below).

Pattern format
==============

The patterns on the left-hand side are regular expressions. For example,
the following ``settings.ROOT_HOSTCONF`` will route ``foo.example.com``
and ``bar.example.com`` to the same URLconf.

::

    from django_hosts import patterns, host

    host_patterns = patterns('',
        host(r'(foo|bar)', 'path.to.urls', name='foo-or-bar'),
    )

.. note:

  * Patterns are matched against the extreme left of the requested host

  * It is implied that all patterns end either with a literal full stop
    (ie. ".") or an end of line metacharacter.

  * As with all regular expressions, various metacharacters need quoting.

Dynamic hosts using regular expressions
=======================================

Patterns being regular expressions allows setups to feature dynamic (or
"wildcard") host schemes::

    from django.conf import settings
    from django_hosts import patterns, host

    host_patterns = patterns('',
        host(r'www', settings.ROOT_URLCONF, name='www'),
        host(r'(\w+)', 'path.to.custom_urls', name='wildcard'),
    )

Here, requests to ``www.example.com`` will be routed as normal but a
request to ``lamby.example.com`` is routed to ``path.to.custom_urls``.

As patterns are matched in order, we placed ``www`` first as it otherwise
would have matched against ``\w+`` and thus routed to the wrong
destination.

Alternatively, we could have used negative lookahead::

    from django_hosts import patterns, host

    host_patterns = patterns('',
        host(r'(?!www)\w+', 'path.to.custom_urls', name='wildcard'),
    )

Callback methods to simplify dynamic hosts
==========================================

The previous section outlined using regular expressions to implement
dynamic hosts.

However, inside every view referenced by the target URLconf we would have
to parse the host from ``request.get_host()`` and lookup its corresponding
object instance, violating DRY. If these dynamic hosts had a lot of views
this would become particularly unwieldy.

To remedy this, you can optionally specify a callback method to be called
if your host matches::

    from django.conf import settings
    from django_hosts import patterns, host

    host_patterns = patterns('',
        host(r'www', settings.ROOT_URLCONF, name='www'),
        host(r'(?P<username>\w+)', 'path.to.custom_urls',
             callback='path.to.custom_fn', name='with-callback'),
    )

    [..]

    from django.shortcuts import get_object_or_404
    from django.contrib.auth.models import User

    def custom_fn(request, username):
        request.viewing_user = get_object_or_404(User, username=username)

This example avoids the duplicated work in every view by attaching a
``viewing_user`` instance to the request object. Views referenced by the
"dynamic" URLconf can now assume that this object exists.

The custom method is called with the ``request`` object and any named
captured arguments, similar to regular Django url processing.

Callbacks may return either ``None`` or an ``HttpResponse`` object. If it
returns ``None``, the request continues to be processed and the appropriate
view is eventually called. If a callback returns an ``HttpResponse``
object, that ``HttpResponse`` is returned to the client without any further
processing.

.. note:

    Callbacks are executed with the URLconf set to the second argument in
    the ``host_patterns`` list. For example, in the example above, the
    callback will be executed with the URLconf as ``path.to.custom_urls``
    and not the default URLconf.

    This can cause problems when reversing URLs within your callback as
    they may not be "visible" to ``django.core.urlresolvers.reverse`` as
    they are specified in (eg.) the default URLconf.

    To remedy this, specify the ``URLconf`` parameter when calling
    ``reverse``.

Template tags
=============

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

then this example will create a link to the admin dashboard::

    {% load hosts %}

    <a href="{% host_url dashboard on our-admin %}">Admin dashboard</a>

which will be rendered as::

    <a href="//admin/dashboard/">Admin dashboard</a>

.. note::

    The double slash at the beginning of the href is an easy way
    to not have to worry about which scheme (http or https) is used.
    Your browser will automatically choose the currently used scheme.
    If you're on ``https://mysite.com/`` a link with an href
    of ``//mysite.com/about/`` would actually point to
    ``https://mysite.com/about/``. For more information see the
    `The protocol-relative URL`_ article by Paul Irish or the
    appropriate `section in RFC 3986`_.

.. _The protocol-relative URL: http://paulirish.com/2010/the-protocol-relative-url/
.. _section in RFC 3986: http://tools.ietf.org/html/rfc3986#section-4.2

In case you want to append a default domain name to the domain part of
the rendered URL you can simply set the ``PARENT_HOST``, e.g::

    PARENT_HOST = 'example.com'

This would render the link above as::

    <a href="//admin.example.com/dashboard/">Admin dashboard</a>

Alternatively -- in case you don't want to append this parent domain
to all URLs you can also spell out the domain in the host pattern::

    from django.conf import settings
    from django_hosts import patterns, host

    host_patterns = patterns('',
        host(r'admin\.example\.com', settings.ROOT_URLCONF, name='admin'),
    )

If your host pattern contains an argument (or key argument), like::

    from django.conf import settings
    from django_hosts import patterns, host

    host_patterns = patterns('',
        host(r'www', settings.ROOT_URLCONF, name='homepage'),
        host(r'(\w+)', 'path.to.support_urls', name='wildcard'),
        host(r'(?P<username>\w+)', 'path.to.user_urls', name='user-area'),
    )

you can also easily pass arguments to the ``host_url`` template tag::

    {% load hosts %}

    <a href="{% host_url user-dashboard on user-area username='johndoe' %}">John's dashboard</a>
    <a href="{% host_url faq-index on wildcard 'help' %}">FAQ</a>

Which will be rendered (with a ``PARENT_HOST`` of ``'example.com'``) as::

    <a href="//johndoe.example.com/">John's dashboard</a>
    <a href="//help.example.com/faq/">FAQ</a>

Notes
=====

  * When using dynamic hosts based on user input, ensure users cannot
    specify names that conflict with static subdomains such as "www" or
    their subdomain will not be accessible.

  * Don't forget to add ``handler404`` and ``handler500`` entries for your
    custom URLconfs.

Changelog
=========

0.2.1 (2011/05/31)
------------------

- Fixed issue related to the ``PARENT_HOST`` setting when used with
  empty host patterns.

- Stopped automatically emulating hosts in debug mode.

0.2 (2011/05/31)
----------------

- **BACKWARDS INCOMPATIBLE** Renamed the package to ``django_hosts``

  Please change your import from::

    from hosts import patterns, hosts

  to::

    from django_hosts import patterns, hosts

- **BACKWARDS INCOMPATIBLE** Changed the data type that the
  ``django_hosts.patterns`` function returns to be a list instead of a
  SortedDict to follow conventions of Django's URL patterns.
  You can use that for easy extension of the patterns, e.g.::

    from django_hosts import patterns, host
    from mytemplateproject.hosts import host_patterns

    host_patterns += patterns('',
        host('www2', 'mysite.urls.www2', name='www2')
    )

- Extended tests to have full coverage.

- Fixed prefix handling.

0.1.1 (2011/05/30)
------------------

- Fixed docs issues.

- Use absolute imports where possible.

0.1 (2011/05/29)
----------------

- Initial release with middleware, reverse and templatetags.


Thanks
======

Many thanks to the folks at playfire_ for releasing their
django-dynamic-subdomains_ app, which was the inspiration for ``django-hosts``.

.. _playfire: http://code.playfire.com/
.. _django-dynamic-subdomains: https://github.com/playfire/django-dynamic-subdomains/
