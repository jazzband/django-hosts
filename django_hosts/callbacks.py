from django.conf import settings
from django.shortcuts import get_object_or_404


def request_site(request, slug):
    from django.contrib.sites.models import Site
    domain = u'%s.%s' % (slug, settings.PARENT_HOST)
    site = get_object_or_404(Site, domain__iexact=domain)
    request.site = site
