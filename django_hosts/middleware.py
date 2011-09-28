from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch, set_urlconf, get_urlconf

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

    def get_host(self, request_host):
        for host in self.host_patterns:
            match = host.compiled_regex.match(request_host)
            if match:
                return host, match.groupdict()
        return self.default_host, {}

    def process_request(self, request):
        # Find best match, falling back to settings.DEFAULT_HOST
        host, kwargs = self.get_host(request.get_host())
        request.urlconf = host.urlconf
        request.host = host
        try:
            current_urlconf = get_urlconf()
            set_urlconf(host.urlconf)
            return host.callback(request, **kwargs)
        finally:
            # Reset URLconf for this thread on the way out for complete
            # isolation of request.urlconf
            set_urlconf(current_urlconf)
