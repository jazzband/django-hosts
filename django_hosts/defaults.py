import imp
import os
import re
import sys

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import get_mod_func
from django.utils.encoding import smart_str
from django.utils.functional import memoize
from django.utils.importlib import import_module

_callable_cache = {}  # Maps view and url pattern names to their view functions.


def module_has_submodule(package, module_name):
    """See if 'module' is in 'package'."""
    name = ".".join([package.__name__, module_name])
    try:
        # None indicates a cached miss; see mark_miss() in Python/import.c.
        return sys.modules[name] is not None
    except KeyError:
        pass
    try:
        package_path = package.__path__   # No __path__, then not a package.
    except AttributeError:
        # Since the remainder of this function assumes that we're dealing with
        # a package (module with a __path__), so if it's not, then bail here.
        return False
    for finder in sys.meta_path:
        if finder.find_module(name, package_path):
            return True
    for entry in package_path:
        try:
            # Try the cached finder.
            finder = sys.path_importer_cache[entry]
            if finder is None:
                # Implicit import machinery should be used.
                try:
                    file_, _, _ = imp.find_module(module_name, [entry])
                    if file_:
                        file_.close()
                    return True
                except ImportError:
                    continue
            # Else see if the finder knows of a loader.
            elif finder.find_module(name):
                return True
            else:
                continue
        except KeyError:
            # No cached finder, so try and make one.
            for hook in sys.path_hooks:
                try:
                    finder = hook(entry)
                    # XXX Could cache in sys.path_importer_cache
                    if finder.find_module(name):
                        return True
                    else:
                        # Once a finder is found, stop the search.
                        break
                except ImportError:
                    # Continue the search for a finder.
                    continue
            else:
                # No finder found.
                # Try the implicit import machinery if searching a directory.
                if os.path.isdir(entry):
                    try:
                        file_, _, _ = imp.find_module(module_name, [entry])
                        if file_:
                            file_.close()
                        return True
                    except ImportError:
                        pass
                # XXX Could insert None or NullImporter
    else:
        # Exhausted the search, so the module cannot be found.
        return False


def get_callable(lookup_view, can_fail=False):
    """
    Convert a string version of a function name to the callable object.

    If the lookup_view is not an import path, it is assumed to be a URL pattern
    label and the original string is returned.

    If can_fail is True, lookup_view might be a URL pattern label, so errors
    during the import fail and the string is returned.
    """
    if not callable(lookup_view):
        mod_name, func_name = get_mod_func(lookup_view)
        try:
            if func_name != '':
                lookup_view = getattr(import_module(mod_name), func_name)
                if not callable(lookup_view):
                    raise ImproperlyConfigured("Could not import %s.%s." %
                                               (mod_name, func_name))
        except AttributeError:
            if not can_fail:
                raise ImproperlyConfigured("Could not import %s. Callable "
                                           "does not exist in module %s." %
                                           (lookup_view, mod_name))
        except ImportError:
            parentmod, submod = get_mod_func(mod_name)
            if (not can_fail and submod != '' and
                    not module_has_submodule(import_module(parentmod), submod)):
                raise ImproperlyConfigured("Could not import %s. Parent "
                                           "module %s does not exist." %
                                           (lookup_view, mod_name))
            if not can_fail:
                raise
    return lookup_view
get_callable = memoize(get_callable, _callable_cache, 1)


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
