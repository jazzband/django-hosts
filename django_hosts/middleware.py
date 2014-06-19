from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch, set_urlconf, get_urlconf

from django_hosts.reverse import get_host_patterns, get_host

hosts_middleware = "django_hosts.middleware.HostsMiddleware"
toolbar_middleware = "debug_toolbar.middleware.DebugToolbarMiddleware"


class BaseHostsMiddleware(object):
    """
    Adjust incoming request's urlconf based on hosts defined in
    settings.ROOT_HOSTCONF module.
    """
    def __init__(self):
        self.current_urlconf = None
        self.host_patterns = get_host_patterns()
        try:
            self.default_host = get_host(settings.DEFAULT_HOST)
        except AttributeError:
            raise ImproperlyConfigured("Missing DEFAULT_HOST setting")
        except NoReverseMatch as e:
            raise ImproperlyConfigured("Invalid DEFAULT_HOST setting: %s" % e)

        middlewares = list(settings.MIDDLEWARE_CLASSES)
        try:
            if (middlewares.index(hosts_middleware) >
                    middlewares.index(toolbar_middleware)):
                raise ImproperlyConfigured(
                    "The django_hosts and debug_toolbar middlewares "
                    "are in the wrong order. Make sure %r comes before "
                    "%r in the MIDDLEWARE_CLASSES setting." %
                    (hosts_middleware, toolbar_middleware))
        except ValueError:
            # django-debug-toolbar middleware doesn't seem to be installed
            pass

    def get_host(self, request_host):
        for host in self.host_patterns:
            match = host.compiled_regex.match(request_host)
            if match:
                return host, match.groupdict()
        return self.default_host, {}


class HostsMiddlewareRequest(BaseHostsMiddleware):
    def process_request(self, request):
        # Find best match, falling back to settings.DEFAULT_HOST
        host, kwargs = self.get_host(request.get_host())
        # This is the main part of this middleware
        request.urlconf = host.urlconf
        request.host = host
        # But we have to temporarily override the URLconf
        # already to allow correctly reversing host URLs in
        # the host callback, if needed.
        current_urlconf = get_urlconf()
        try:
            set_urlconf(host.urlconf)
            return host.callback(request, **kwargs)
        finally:
            # Reset URLconf for this thread on the way out for complete
            # isolation of request.urlconf
            set_urlconf(current_urlconf)


class HostsMiddlewareResponse(BaseHostsMiddleware):
    def process_response(self, request, response):
        # Django resets the base urlconf when it starts to process
        # the response, so we need to set this again, in case
        # any of our middleware makes use of host, etc URLs.

        # Find best match, falling back to settings.DEFAULT_HOST
        host, kwargs = self.get_host(request.get_host())
        # This is the main part of this middleware
        request.urlconf = host.urlconf
        request.host = host

        set_urlconf(host.urlconf)
        return response


class HostsMiddleware(HostsMiddlewareRequest):
    """
    Provided for backwards-compatibility.
    """
    import warnings
    warnings.warn("django_hosts.middleware.HostsMiddleware has been split into HostsMiddlewareRequest and HostsMiddlewareResponse. Please consult the documentation and update your middleware settings.",
        DeprecationWarning
    )
