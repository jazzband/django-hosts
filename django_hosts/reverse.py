import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch, reverse
from django.utils.encoding import force_unicode
from django.utils.functional import memoize
from django.utils.importlib import import_module
from django.utils.regex_helper import normalize

from django_hosts.defaults import host as host_cls

_hostconf_cache = {}
_hostconf_module_cache = {}
_host_patterns_cache = {}
_host_cache = {}


def get_hostconf():
    try:
        return settings.ROOT_HOSTCONF
    except AttributeError:
        raise ImproperlyConfigured("Missing ROOT_HOSTCONF setting")
get_hostconf = memoize(get_hostconf, _hostconf_cache, 0)


def get_hostconf_module(hostconf=None):
    if hostconf is None:
        hostconf = get_hostconf()
    return import_module(hostconf)
get_hostconf_module = memoize(get_hostconf_module, _hostconf_module_cache, 1)


def get_host(name):
    for host in get_host_patterns():
        if host.name == name:
            return host
    raise NoReverseMatch("No host called '%s' exists" % name)
get_host = memoize(get_host, _host_cache, 1)


def get_host_patterns():
    hostconf = get_hostconf()
    module = get_hostconf_module(hostconf)
    try:
        return module.host_patterns
    except AttributeError:
        raise ImproperlyConfigured("Missing host_patterns in '%s'" % hostconf)
get_host_patterns = memoize(get_host_patterns, _host_patterns_cache, 0)


def clear_host_caches():
    global _hostconf_cache, _hostconf_module_cache, \
           _host_patterns_cache, _host_cache
    _hostconf_cache.clear()
    _hostconf_module_cache.clear()
    _host_patterns_cache.clear()
    _host_cache.clear()


def reverse_host(host, args=None, kwargs=None):
    """
    Given the host name and the appropriate parameters,
    reverses the host, e.g.::

        >>> from django.conf import settings
        >>> settings.ROOT_HOSTCONF = 'mysite.hosts'
        >>> settings.PARENT_HOST = 'example.com'
        >>> from django_hosts.reverse import reverse_host
        >>> reverse_host('with_username', 'jezdez')
        'jezdez.example.com'

    :param name: the name of the host as specified in the hostconf
    :args: the host arguments to use to find a matching entry in the hostconf
    :kwargs: similar to args but key value arguments
    :raises django.core.urlresolvers.NoReverseMatch: if no host matches
    :rtype: reversed hostname
    """
    if args and kwargs:
        raise ValueError("Don't mix *args and **kwargs in call to reverse()!")

    args = args or ()
    kwargs = kwargs or {}

    if not isinstance(host, host_cls):
        host = get_host(host)

    unicode_args = [force_unicode(x) for x in args]
    unicode_kwargs = dict(((k, force_unicode(v))
                          for (k, v) in kwargs.iteritems()))

    for result, params in normalize(host.regex):
        if args:
            if len(args) != len(params):
                continue
            candidate = result % dict(zip(params, unicode_args))
        else:
            if set(kwargs.keys()) != set(params):
                continue
            candidate = result % unicode_kwargs

        if re.match(host.regex, candidate, re.UNICODE):  # pragma: no cover
            parent_host = getattr(settings, 'PARENT_HOST', '').lstrip('.')
            if parent_host:
                if candidate:
                    candidate = '%s.%s' % (candidate, parent_host)
                else:
                    candidate = parent_host
            return candidate

    raise NoReverseMatch("Reverse host for '%s' with arguments '%s' "
                         "and keyword arguments '%s' not found." %
                         (host.name, args, kwargs))


def reverse_full(host, view,
                 host_args=None, host_kwargs=None,
                 view_args=None, view_kwargs=None):
    """
    Given the host and view name and the appropriate parameters,
    reverses the fully qualified URL, e.g.::

        >>> from django.conf import settings
        >>> settings.ROOT_HOSTCONF = 'mysite.hosts'
        >>> settings.PARENT_HOST = 'example.com'
        >>> from django_hosts.reverse import reverse_full
        >>> reverse_full('www', 'about')
        '//www.example.com/about/'

    :param host: the name of the host
    :param view: the name of the view
    :host_args: the host arguments
    :host_kwargs: the host keyed arguments
    :view_args: the arguments of the view
    :view_kwargs: the keyed arguments of the view
    :rtype: fully qualified URL with path
    """
    host = get_host(host)
    host_part = reverse_host(host,
                             args=host_args,
                             kwargs=host_kwargs)
    path_part = reverse(view,
                        args=view_args or (),
                        kwargs=view_kwargs or {},
                        urlconf=host.urlconf)
    return u'//%s%s' % (host_part, path_part)
