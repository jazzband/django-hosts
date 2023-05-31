from importlib.metadata import version

try:  # pragma: no cover
    from django_hosts.defaults import patterns, host
    from django_hosts.resolvers import (reverse, reverse_lazy,
                                        reverse_host, reverse_host_lazy)
except ImportError:  # pragma: no cover
    pass

__version__ = version('django-hosts')
__author__ = 'Jazzband members (https://jazzband.co/)'
