try:  # pragma: no cover
    from django_hosts.defaults import patterns, host
    from django_hosts.reverse import reverse_host, reverse_full
except ImportError:  # pragma: no cover
    pass

# following PEP 386
__version__ = "0.4.2"
