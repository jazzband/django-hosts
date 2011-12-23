import re
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import get_callable, get_mod_func
from django.utils.encoding import smart_str


def patterns(prefix, *args):
    """
    The function to define the list of hosts (aka host confs), e.g.::

        from django_hosts import patterns

        host_patterns = patterns('path.to',
            (r'www', 'urls.default', 'default'),
            (r'api', 'urls.api', 'api'),
        )

    :param prefix: the URLconf prefix to pass to the host object
    :type prefix: str
    :param \*args: a list of :class:`~django_hosts.defaults.hosts` instances
                   or an iterable thereof
    """
    hosts = []
    for arg in args:
        if isinstance(arg, (list, tuple)):
            arg = host(prefix=prefix, *arg)
        else:
            arg.add_prefix(prefix)
        name = arg.name
        if name in [h.name for h in hosts]:
            raise ImproperlyConfigured("Duplicate host name: %s" % name)
        hosts.append(arg)
    return hosts


class host(object):
    """
    The host object used in host conf together with the
    :func:`django_hosts.defaults.patterns` function, e.g.::

        from django_hosts import patterns, host

        host_patterns = patterns('path.to',
            host(r'www', 'urls.default', name='default'),
            host(r'api', 'urls.api', name='api'),
        )

    :param regex: a regular expression to be used to match the request's
                  host.
    :type regex: str
    :param urlconf: the dotted path of a URLconf module of the host
    :type urlconf: str
    :param callback: a callable or the dotted path of a callable to be used
                     when matching has happened
    :type callback: callable or str
    :param prefix: the prefix to apply to the ``urlconf`` parameter
    :type prefix: str
    """
    def __init__(self, regex, urlconf, name, callback=None, prefix=''):
        """
        Compile hosts. We add a literal fullstop to the end of every
        pattern to avoid rather unwieldy escaping in every definition.
        """
        self.regex = regex
        self.compiled_regex = re.compile(r'%s(\.|$)' % regex)
        self.urlconf = urlconf
        self.name = name
        if callable(callback):
            self._callback = callback
        else:
            self._callback, self._callback_str = None, callback
        self.add_prefix(prefix)

    def __repr__(self):
        return smart_str(u'<%s %s: %s (%r)>' %
                         (self.__class__.__name__, self.name,
                          self.urlconf, self.regex))

    @property
    def callback(self):
        if self._callback is not None:
            return self._callback
        elif self._callback_str is None:
            return lambda *args, **kwargs: None
        try:
            self._callback = get_callable(self._callback_str)
        except ImportError, e:
            mod_name, _ = get_mod_func(self._callback_str)
            raise ImproperlyConfigured("Could not import '%s'. "
                                       "Error was: %s" %
                                       (mod_name, str(e)))
        except AttributeError, e:
            mod_name, func_name = get_mod_func(self._callback_str)
            raise ImproperlyConfigured("Tried '%s' in module '%s'. "
                                       "Error was: %s" %
                                       (func_name, mod_name, str(e)))
        return self._callback

    def add_prefix(self, prefix=''):
        """
        Adds the prefix string to a string-based urlconf.
        """
        if prefix:
            self.urlconf = prefix.rstrip('.') + '.' + self.urlconf
