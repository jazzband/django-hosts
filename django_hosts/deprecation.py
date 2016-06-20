from django import VERSION
from django.core.exceptions import ImproperlyConfigured, ViewDoesNotExist


if VERSION[0:2] >= (1, 10):
    from django.utils.deprecation import MiddlewareMixin

else:
    class MiddlewareMixin(object):
        pass


if VERSION[0:2] >= (1, 10):
    from django.urls.utils import get_callable as actual_get_callable
    
    def get_callable(lookup_view):
        try:
            return actual_get_callable(lookup_view)
        except ViewDoesNotExist as exc:
            raise ImproperlyConfigured(exc.args[0].replace('View', 'Callable'))

else:
    from django.core.urlresolvers import get_callable as actual_get_callable

    def get_callable(lookup_view, can_fail=False):
        """
        can_fail is DEPRECATED
        """
        try:
            return actual_get_callable(lookup_view, can_fail)
        except ViewDoesNotExist as exc:
            raise ImproperlyConfigured(exc.args[0].replace('View', 'Callable'))
