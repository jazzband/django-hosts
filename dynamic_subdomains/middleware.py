import re

from django.core.urlresolvers import set_urlconf
from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed

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

        SUBDOMAINS = (
            ('api', 'path.to.api.urls'),
            ('beta', 'path.to.beta.urls'),
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

        SUBDOMAINS = (
            (r'(foo|bar)', 'path.to.urls'),
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

        SUBDOMAINS = (
            ('www', ROOT_URLCONF),
            ('\w+', 'path.to.custom_urls'),
        )

    Here, requests to ``www.example.com`` will be routed as normal but a
    request to ``lamby.example.com`` is routed to ``path.to.custom_urls``.

    As patterns are matched in order, we placed ``www`` first as it otherwise
    would have matched against ``\w+`` and thus routed to the wrong
    destination.

    Alternatively, we could have used negative lookahead:

        SUBDOMAINS = (
            ('(?!www)\w+', 'path.to.custom_urls'),
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

        SUBDOMAINS = (
            ('www', ROOT_URLCONF),
            ('(?P<username>\w+)', 'path.to.custom_urls', 'path.to.custom_fn'),
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
        self.subdomains = []

        if not settings.SUBDOMAINS:
            raise MiddlewareNotUsed

        # Compile subdomains. We add a literal fullstop to the end of every
        # pattern to avoid rather unwieldy escaping in every definition.
        for entry in settings.SUBDOMAINS:
            try:
                pattern, target = entry
                callback = lambda *args, **kwargs: None
            except ValueError:
                pattern, target, callback_fn = entry
                callback = from_dotted_path(callback_fn)

            self.subdomains.append(
                (re.compile(r'%s(\.|$)' % pattern), target, callback)
            )

    def process_request(self, request):
        host = request.get_host()

        for pattern, target, callback in self.subdomains:
            match = pattern.match(host)

            if match:
                request.urlconf = target
                try:
                    set_urlconf(target)
                    return callback(request, **match.groupdict())
                finally:
                    set_urlconf(None)
