Overview
========

This middleware routes requests to specific hosts to different URL
schemes ("hostconf").

For example, if you own ``example.com`` but want to serve specific content
at ``api.example.com` and ``beta.example.com``, add the following to your
``hosts.py``::

    from hosts import patterns, host

    host_patterns = patterns('path.to',
        host(r'api', 'api.urls', name='api'),
        host(r'beta', 'beta.urls', name='beta'),
    )

This causes requests to ``{api,beta}.example.com`` to be routed to their
corresponding URLconf. You can use your ``urls.py`` as a template for these
URLconfs.

Patterns are evaluated in order. If no pattern matches, the request is
processed in the usual way, ie. using ``settings.ROOT_URLCONF``.

Pattern format
==============

The patterns on the left-hand side are regular expressions. For example,
the following ``settings.ROOT_HOSTCONF`` will route ``foo.example.com``
and ``bar.example.com`` to the same URLconf.

::

    from hosts import patterns, host

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
    from hosts import patterns, host

    host_patterns = patterns('',
        host(r'www', settings.ROOT_URLCONF, name='static'),
        host(r'\w+', 'path.to.custom_urls', name='wildcard'),
    )

Here, requests to ``www.example.com`` will be routed as normal but a
request to ``lamby.example.com`` is routed to ``path.to.custom_urls``.

As patterns are matched in order, we placed ``www`` first as it otherwise
would have matched against ``\w+`` and thus routed to the wrong
destination.

Alternatively, we could have used negative lookahead::

    from hosts import patterns, host

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
    from hosts import patterns, host

    host_patterns = patterns('',
        host(r'www', settings.ROOT_URLCONF, name='static'),
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

Notes
=====

  * When using dynamic hosts based on user input, ensure users cannot
    specify names that conflict with static subdomains such as "www" or
    their subdomain will not be accessible.

  * Don't forget to add ``handler404`` and ``handler500`` entries for your
    custom URLconfs.
