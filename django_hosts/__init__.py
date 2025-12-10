import importlib.metadata

try:  # pragma: no cover
    from django_hosts.defaults import host, patterns
    from django_hosts.resolvers import (
        reverse,
        reverse_host,
        reverse_host_lazy,
        reverse_lazy,
    )
except ImportError:  # pragma: no cover
    pass

__version__ = importlib.metadata.version("django-hosts")
__author__ = "Jazzband members (https://jazzband.co/)"
