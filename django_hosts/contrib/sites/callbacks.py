from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.sites.models import Site


def request_site(request, slug):
    site = get_object_or_404(Site,
        domain__iexact=u'%s.%s' % (slug, settings.PARENT_HOST))
    request.site = site
