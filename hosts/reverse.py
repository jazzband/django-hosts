import re
import urllib

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch, reverse
from django.utils.encoding import force_unicode
from django.utils.functional import memoize
from django.utils.importlib import import_module
from django.utils.regex_helper import normalize

_hostconf_cache = {}
_host_patterns_cache = {}


def get_hostconf_module(hostconf):
    if hostconf is None:
        hostconf = settings.ROOT_HOSTCONF
    return import_module(hostconf)
get_hostconf_module = memoize(get_hostconf_module, _hostconf_cache, 1)


def get_host_patterns():
    try:
        hostconf = settings.ROOT_HOSTCONF
    except AttributeError:
        raise ImproperlyConfigured("Missing ROOT_HOSTCONF setting")
    hostconf_module = get_hostconf_module(hostconf)
    try:
        return hostconf_module.host_patterns
    except AttributeError:
        raise ImproperlyConfigured("Missing host_patterns in '%s'" % hostconf)
get_host_patterns = memoize(get_host_patterns, _host_patterns_cache, 0)

def clear_host_caches():
    global _hostconf_cache
    global _host_patterns_cache
    _hostconf_cache.clear()
    _host_patterns_cache.clear()


def reverse_host(name, args=(), kwargs=None):
    if args and kwargs:
        raise ValueError("Don't mix *args and **kwargs in call to reverse()!")

    if kwargs is None:
        kwargs = {}

    host_patterns = get_host_patterns()
    try:
        host = host_patterns[name]
    except KeyError:
        raise NoReverseMatch("No host called %s exists" % name)

    unicode_args = [force_unicode(x) for x in args]
    unicode_kwargs = dict(((k, force_unicode(v)) for (k, v) in kwargs.iteritems()))

    for result, params in normalize(host['regex']):
        if args:
            if len(args) != len(params):
                continue
            candidate = result % dict(zip(params, unicode_args))
        else:
            if set(kwargs.keys()) != set(params):
                continue
            candidate = result % unicode_kwargs

        if re.match(host['regex'], candidate, re.UNICODE):
            return candidate

    raise NoReverseMatch("Reverse host for '%s' with arguments '%s' and "
                         "keyword arguments '%s' not found." % (name, args, kwargs))

def reverse_crossdomain_part(host, path, host_args=(), host_kwargs=None, mangle=True):
    if host_kwargs is None:
        host_kwargs = {}

    domain_part = reverse_host(host, args=host_args, kwargs=host_kwargs)
    if mangle and getattr(settings, 'EMULATE_HOSTS', settings.DEBUG):
        return '%s?%s' % (
            reverse('hosts-debug-redirect'),
            urllib.urlencode((
                ('domain', domain_part),
                ('path', path),
            ))
        )
    return u'//%s%s' % (domain_part, path)

def reverse_path(host, view, args=(), kwargs=None):
    if kwargs is None:
        kwargs = {}

    host_patterns = get_host_patterns()
    try:
        urlconf = host_patterns[host]['urlconf']
    except KeyError:
        raise NoReverseMatch("No host called %s exists" % host)

    return reverse(view, args=args, kwargs=kwargs, urlconf=urlconf)

def reverse_crossdomain(host, view, host_args=(), host_kwargs=None,
        view_args=(), view_kwargs=None, mangle=True):
    path = reverse_path(host, view, view_args, view_kwargs)
    return reverse_crossdomain_part(host, path, host_args, host_kwargs, mangle=mangle)
