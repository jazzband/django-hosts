from django.shortcuts import get_object_or_404
from django.utils.functional import SimpleLazyObject

from django_hosts.reverse import reverse_host


def get_site(request, *args, **kwargs):
    if not hasattr(request, '_cached_site'):  # pragma: no cover
        from django.contrib.sites.models import Site
        host = reverse_host(request.host.name, args=args, kwargs=kwargs)
        request._cached_site = get_object_or_404(Site, domain__iexact=host)
    return request._cached_site


def host_site(request, *args, **kwargs):
    """
    A callback function which uses the :mod:`django.contrib.sites` contrib
    app included in Django to match a host to a
    :class:`~django.contrib.sites.models.Site` instance, setting a
    ``request.site`` attribute on success.

    :param request: the request object passed from the middleware
    :param \*args: the parameters as matched by the host patterns
    :param \*\*kwargs: the keyed parameters as matched by the host patterns

    It's important to note that this uses
    :func:`~django_hosts.reverse.reverse_host` behind the scenes to
    reverse the host with the given arguments and keyed arguments to
    enable a flexible configuration of what will be used to retrieve
    the :class:`~django.contrib.sites.models.Site` instance -- in the end
    the callback will use a ``domain__iexact`` lookup to get it.

    For example, imagine a host conf with a username parameter::

        from django.conf import settings
        from django_hosts import patterns, host

        settings.PARENT_HOST = 'example.com'

        host_patterns = patterns('',
            host(r'www', settings.ROOT_URLCONF, name='www'),
            host(r'(?P<username>\w+)', 'path.to.custom_urls',
                 callback='django_hosts.callbacks.host_site',
                 name='user-sites'),
        )

    When requesting this website with the host ``jezdez.example.com``,
    the callback will act as if you'd do::

        request.site = Site.objects.get(domain__iexact='jezdez.example.com')

    ..since the result of calling :func:`~django_hosts.reverse.reverse_host`
    with the username ``'jezdez'`` is ``'jezdez.example.com'``.

    Later, in your views, you can nicely refer to the current site
    as ``request.site`` for further site-specific functionality.
    """
    request.site = SimpleLazyObject(lambda: get_site(request, *args, **kwargs))
