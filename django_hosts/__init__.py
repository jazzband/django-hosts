try:
    from django_hosts.defaults import patterns, host
except ImportError:
    pass

# following PEP 386, versiontools will pick it up
__version__ = (0, 3, 0, "final", 0)
