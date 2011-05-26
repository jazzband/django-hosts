from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import set_urlconf

from .reverse import get_host_patterns

class HostsMiddleware(object):
    """
    Adjust incoming request's urlconf based on hosts defined in
    settings.ROOT_HOSTCONF module.
    """
    def __init__(self):
        self.host_patterns = get_host_patterns()
        try:
            self.default = self.host_patterns[settings.DEFAULT_HOST]
        except AttributeError:
            raise ImproperlyConfigured("Missing DEFAULT_HOST setting")
        except KeyError:
            raise ImproperlyConfigured("Invalid DEFAULT_HOST setting")

    def process_request(self, request):
        host = request.get_host()
        # Find best match, falling back to settings.DEFAULT_HOST
        for host in self.host_patterns.itervalues():
            match = host['compiled_regex'].match(host)
            if match:
                kwargs = match.groupdict()
                break
        else:
            host, kwargs = self.default, {}
        urlconf, callback = host['urlconf'], host['callback']
        request.urlconf = urlconf
        try:
            set_urlconf(urlconf)
            return callback(request, **kwargs)
        finally:
            set_urlconf(None)
