try:  # pragma: no cover
    from django_hosts.defaults import patterns, host
    from django_hosts.reverse import reverse_host, reverse_full
except ImportError:  # pragma: no cover
    pass

# following PEP 386, versiontools will pick it up
__version__ = (0, 3, 0, "final", 0)
