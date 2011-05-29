import re
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import get_callable, get_mod_func
from django.utils.datastructures import SortedDict
from django.utils.encoding import smart_str

def patterns(prefix, *args):
    hosts = SortedDict()

    for arg in args:
        if isinstance(arg, (list, tuple)):
            arg = host(prefix=prefix, *arg)
        elif isinstance(arg, host):
            arg.add_prefix(prefix)
        name = arg.name
        if name in hosts:
            raise ImproperlyConfigured("Duplicate host name: %s" % name)
        if name == 'default':
            raise ImproperlyConfigured("Reserved host name: %s" % name)
        hosts[name] = arg
    return hosts

class host(object):

    def __init__(self, regex, urlconf, name, callback=None, prefix=''):
        # Compile hosts. We add a literal fullstop to the end of every
        # pattern to avoid rather unwieldy escaping in every definition.
        self.regex = regex
        self.compiled_regex = re.compile(r'%s(\.|$)' % regex)
        if prefix:
            urlconf = prefix + '.' + urlconf
        self.urlconf = urlconf
        self.name = name
        if callable(callback):
            self._callback = callback
        else:
            self._callback, self._callback_str = None, callback

    @property
    def callback(self):
        if self._callback is not None:
            return self._callback
        if self._callback_str is None:
            return lambda *args, **kwargs: None
        try:
            self._callback = get_callable(self._callback_str)
        except ImportError, e:
            mod_name, _ = get_mod_func(self._callback_str)
            raise ImproperlyConfigured(
                "Could not import %s. Error was: %s" % (mod_name, str(e)))
        except AttributeError, e:
            mod_name, func_name = get_mod_func(self._callback_str)
            raise ImproperlyConfigured(
                "Tried %s in module %s. Error was: %s" % (func_name, mod_name, str(e)))
        return self._callback

    def __repr__(self):
        return smart_str(u'<%s %s %s>'
                         % (self.__class__.__name__, self.name, self.regex))

    def add_prefix(self, prefix):
        """
        Adds the prefix string to a string-based callback.
        """
        if not prefix or not hasattr(self, '_callback_str'):
            return
        self._callback_str = prefix + '.' + self._callback_str
