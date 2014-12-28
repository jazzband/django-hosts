import warnings

from .resolvers import reverse, reverse_host as actual_reverse_host


def reverse_host(host, args=None, kwargs=None):  # pragma: no cover
    warnings.warn(
        "The function 'django_hosts.reverse.reverse_host' is pending "
        "deprecation and will be removed in the next version. Please "
        "use the function 'django_hosts.resolvers.reverse_host' instead.",
        PendingDeprecationWarning)
    return actual_reverse_host(host, args=None, kwargs=None)


def reverse_full(host, view,
                 host_args=None, host_kwargs=None,
                 view_args=None, view_kwargs=None):  # pragma: no cover
    warnings.warn(
        "The function 'django_hosts.reverse.reverse_full' is pending "
        "deprecation and will be removed in the next version. Please "
        "use the function 'django_hosts.resolvers.reverse' instead.",
        PendingDeprecationWarning)

    return reverse(view, host=host,
                   view_args=view_args, view_kwargs=view_kwargs)
