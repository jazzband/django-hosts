import re
from django.core.exceptions import ImproperlyConfigured
from django.utils.datastructures import SortedDict
from django.core.urlresolvers import get_callable

def patterns(prefix, *args):
    hosts = SortedDict()

    for arg in args:
        if isinstance(arg, (list, tuple)):
            arg = host(prefix=prefix, *arg)
        name = arg['name']
        if name in hosts:
            raise ImproperlyConfigured("Duplicate host name: %s" % name)
        if name == 'default':
            raise ImproperlyConfigured("Reserved host name: %s" % name)
        hosts[name] = arg
    return hosts

class host(dict):
    def __init__(self, regex, urlconf, name, callback=None, prefix=''):
        if prefix:
            urlconf = prefix + '.' + urlconf
        if isinstance(callback, basestring):
            callback = get_callable(callback)
        elif callback is None:
            callback = lambda *args, **kwargs: None
        # Compile hosts. We add a literal fullstop to the end of every
        # pattern to avoid rather unwieldy escaping in every definition.
        compiled_regex = re.compile(r'%s(\.|$)' % regex)
        dict.__init__(self, regex=regex, urlconf=urlconf, name=name,
                      callback=callback, compiled_regex=compiled_regex)
