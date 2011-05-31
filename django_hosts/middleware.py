from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch, set_urlconf

from django_hosts.reverse import get_host_patterns, get_host

class HostsMiddleware(object):
    """
    Adjust incoming request's urlconf based on hosts defined in
    settings.ROOT_HOSTCONF module.
    """
    def __init__(self):
        self.host_patterns = get_host_patterns()
        try:
            self.default_host = get_host(settings.DEFAULT_HOST)
        except AttributeError:
            raise ImproperlyConfigured("Missing DEFAULT_HOST setting")
        except NoReverseMatch, e:
            raise ImproperlyConfigured("Invalid DEFAULT_HOST setting: %s" % e)

    def process_request(self, request):
        request_host = request.get_host()
        # Find best match, falling back to settings.DEFAULT_HOST
        for host in self.host_patterns:
            match = host.compiled_regex.match(request_host)
            if match:
                kwargs = match.groupdict()
                break
        else:
            host, kwargs = self.default_host, {}
        request.urlconf = host.urlconf
        try:
            set_urlconf(host.urlconf)
            return host.callback(request, **kwargs)
        finally:
            # Reset URLconf for this thread on the way out for complete
            # isolation of request.urlconf
            set_urlconf(None)
