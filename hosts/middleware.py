from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import set_urlconf

from hosts.reverse import get_host_patterns

class HostsMiddleware(object):
    """
    Adjust incoming request's urlconf based on hosts defined in
    settings.ROOT_HOSTCONF module.
    """
    def __init__(self):
        self.host_patterns = get_host_patterns()
        try:
            self.default_host = self.host_patterns[settings.DEFAULT_HOST]
        except AttributeError:
            raise ImproperlyConfigured("Missing DEFAULT_HOST setting")
        except KeyError:
            raise ImproperlyConfigured("Invalid DEFAULT_HOST setting")

    def process_request(self, request):
        request_host = request.get_host()
        # Find best match, falling back to settings.DEFAULT_HOST
        for host in self.host_patterns.itervalues():
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
