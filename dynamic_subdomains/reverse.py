import re
import urllib

from django.conf import settings
from django.utils.encoding import force_unicode
from django.core.urlresolvers import NoReverseMatch, reverse
from django.utils.regex_helper import normalize

def reverse_subdomain(name, args=(), kwargs=None):
    if args and kwargs:
        raise ValueError("Don't mix *args and **kwargs in call to reverse()!")

    if kwargs is None:
        kwargs = {}

    try:
        subdomain = settings.SUBDOMAINS[name]
    except KeyError:
        raise NoReverseMatch("No subdomain called %s exists" % name)

    unicode_args = [force_unicode(x) for x in args]
    unicode_kwargs = dict([(k, force_unicode(v)) for (k, v) in kwargs.items()])

    for result, params in normalize(subdomain['regex']):
        if args:
            if len(args) != len(params):
                continue
            candidate = result % dict(zip(params, unicode_args))
        else:
            if set(kwargs.keys()) != set(params):
                continue
            candidate = result % unicode_kwargs

        if re.match(subdomain['regex'], candidate, re.UNICODE):
            return candidate

    raise NoReverseMatch(
        "Reverse subdomain for '%s' with arguments '%s' and keyword arguments "
        "'%s' not found." % (name, args, kwargs)
    )

def reverse_crossdomain_part(subdomain, path, subdomain_args=(), subdomain_kwargs=None):
    if subdomain_kwargs is None:
        subdomain_kwargs = {}


    domain_part = reverse_subdomain(
        subdomain,
        args=subdomain_args,
        kwargs=subdomain_kwargs,
    )

    if getattr(settings, 'EMULATE_SUBDOMAINS', settings.DEBUG):
        return '%s?%s' % (
            reverse('debug-subdomain-redirect'),
            urllib.urlencode((
                ('domain', domain_part),
                ('path', path),
            ))
        )

    return u'//%s%s' % (domain_part, path)

def reverse_crossdomain(subdomain, view, subdomain_args=(), subdomain_kwargs=None, view_args=(), view_kwargs=None):
    if view_kwargs is None:
        view_kwargs = {}

    try:
        urlconf = settings.SUBDOMAINS[subdomain]['urlconf']
    except KeyError:
        raise NoReverseMatch("No subdomain called %s exists" % subdomain)

    path = reverse(
        view,
        args=view_args,
        kwargs=view_kwargs,
        urlconf=urlconf,
    )

    return reverse_crossdomain_part(
        subdomain,
        path,
        subdomain_args,
        subdomain_kwargs,
    )
