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
    request.site = SimpleLazyObject(lambda: get_site(request, *args, **kwargs))
