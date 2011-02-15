import re

from django.conf import settings
from django.utils.encoding import force_unicode
from django.core.urlresolvers import NoReverseMatch
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
