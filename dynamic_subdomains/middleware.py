import re

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed, ImproperlyConfigured
from django.core.urlresolvers import set_urlconf

from .utils import from_dotted_path

class SubdomainMiddleware(object):
    """
    Adjust incoming request's urlconf based on `settings.SUBDOMAINS`.

    Overview
    ========

    This middleware routes requests to specific subdomains to different URL
    schemes ("urlconf").

    For example, if you own ``example.com`` but want to serve specific content
    at ``api.example.com` and ``beta.example.com``, add the following to your
    ``settings.py``:

        from dynamic_subdomains.defaults import patterns, subdomain

        SUBDOMAINS = patterns(
            subdomain('api', 'path.to.api.urls', name='api'),
            subdomain('beta', 'path.to.beta.urls', name='beta'),
        )

    This causes requests to ``{api,beta}.example.com`` to be routed to their
    corresponding urlconf. You can use your ``urls.py`` as a template for these
    urlconfs.

    Patterns are evaluated in order. If no pattern matches, the request is
    processed in the usual way, ie. using ``settings.ROOT_URLCONF``.

    Pattern format
    ==============

    The patterns on the left-hand side are regular expressions. For example,
    the following ``settings.SUBDOMAINS`` will route ``foo.example.com`` and
    ``bar.example.com`` to the same urlconf.

        SUBDOMAINS = patterns(
            subdomain(r'(foo|bar)', 'path.to.urls', name='foo-or-bar'),
        )

    .. note:

      * Patterns are matched against the extreme left of the requested host

      * It is implied that all patterns end either with a literal full stop
        (ie. ".") or an end of line metacharacter.

      * As with all regular expressions, various metacharacters need quoting.

    Dynamic subdomains using regular expressions
    ============================================

    Patterns being regular expressions allows setups to feature dynamic (or
    "wildcard") subdomain schemes:

        SUBDOMAINS = patterns(
            subdomain('www', ROOT_URLCONF, name='static'),
            subdomain('\w+', 'path.to.custom_urls', name='wildcard'),
        )

    Here, requests to ``www.example.com`` will be routed as normal but a
    request to ``lamby.example.com`` is routed to ``path.to.custom_urls``.

    As patterns are matched in order, we placed ``www`` first as it otherwise
    would have matched against ``\w+`` and thus routed to the wrong
    destination.

    Alternatively, we could have used negative lookahead:

        SUBDOMAINS = patterns(
            subdomain('(?!www)\w+', 'path.to.custom_urls', name='wildcard'),
        )

    Callback methods to simplify dynamic subdomains
    ===============================================

    The previous section outlined using regular expressions to implement
    dynamic subdomains.

    However, inside every view referenced by the target urlconf we would have
    to parse the subdomain from ``request.get_host()`` and lookup its
    corresponding object instance, violating DRY. If these dynamic subdomains
    had a lot of views this would become particularly unwieldy.

    To remedy this, you can optionally specify a callback method to be called
    if your subdomain matches:

        SUBDOMAINS = patterns(
            subdomain('www', ROOT_URLCONF, name='static'),
            subdomain('(?P<username>\w+)', 'path.to.custom_urls',
                      callback='path.to.custom_fn', name='with-callback'),
        )

        [..]

        from django.shortcuts import get_object_or_404
        from django.contrib.auth.models import User

        def custom_fn(request, username):
            request.viewing_user = get_object_or_404(User, username=username)

    This example avoids the duplicated work in every view by attaching a
    ``viewing_user`` instance to the request object. Views referenced by the
    "dynamic" urlconf can now assume that this object exists.

    The custom method is called with the ``request`` object and any named
    captured arguments, similar to regular Django url processing.

    Callbacks may return either ``None`` or an ``HttpResponse`` object. If it
    returns ``None``, the request continues to be processed and the appropriate
    view is eventually called. If a callback returns an ``HttpResponse``
    object, that ``HttpResponse`` is returned to the client without any further
    processing.

    .. note:

        Callbacks are executed with the urlconf set to the second argument in
        the ``SUBDOMAINS`` list. For example, in the example above, the
        callback will be executed with the urlconf as ``path.to.custom_urls``
        and not the default urlconf.

        This can cause problems when reversing URLs within your callback as
        they may not be "visible" to ``django.core.urlresolvers.reverse`` as
        they are specified in (eg.) the default urlconf.

        To remedy this, specify the ``urlconf`` parameter when calling
        ``reverse``.

    Notes
    =====

      * When using dynamic subdomains based on user input, ensure users cannot
        specify names that conflict with static subdomains such as "www" or
        their subdomain will not be accessible.

      * Don't forget to add ``handler404`` and ``handler500`` entries for your
        custom urlconfs.
    """

    def __init__(self):
        try:
            settings.SUBDOMAINS
        except AttributeError:
            raise ImproperlyConfigured("Missing settings.SUBDOMAINS setting")

        try:
            self.default = settings.SUBDOMAINS[settings.SUBDOMAIN_DEFAULT]
        except AttributeError:
            raise ImproperlyConfigured(
                "Missing settings.SUBDOMAIN_DEFAULT setting")
        except KeyError:
            raise ImproperlyConfigured(
                "settings.SUBDOMAIN_DEFAULT does not point to a valid domain")

        if not settings.SUBDOMAINS:
            raise MiddlewareNotUsed()

        # Compile subdomains. We add a literal fullstop to the end of every
        # pattern to avoid rather unwieldy escaping in every definition.
        for subdomain in settings.SUBDOMAINS.values():
            callback = subdomain.get('callback', lambda *args, **kwargs: None)
            if isinstance(callback, (basestring,)):
                callback = from_dotted_path(callback)

            subdomain['_regex'] = re.compile(r'%s(\.|$)' % subdomain['regex'])
            subdomain['_callback'] = callback

    def process_request(self, request):
        host = request.get_host()

        # Find best match, falling back to settings.SUBDOMAIN_DEFAULT
        for subdomain in settings.SUBDOMAINS.values():
            match = subdomain['_regex'].match(host)
            if match:
                kwargs = match.groupdict()
                break
        else:
            kwargs = {}
            subdomain = self.default

        urlconf = subdomain['urlconf']
        callback = subdomain['_callback']

        request.urlconf = urlconf
        try:
            set_urlconf(urlconf)
            return callback(request, **kwargs)
        finally:
            set_urlconf(None)
