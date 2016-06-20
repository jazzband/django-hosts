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

if VERSION[0:2] >= (1, 10):
    def get_all_field_names(meta):
        names = set()
        fields = meta.get_fields()
        for field in fields:
            # For backwards compatibility GenericForeignKey should not be
            # included in the results.
            if field.is_relation and field.many_to_one and field.related_model is None:
                continue
            # Relations to child proxy models should not be included.
            if (field.model != meta.model and
                    field.model._meta.concrete_model == meta.concrete_model):
                continue

            names.add(field.name)
            if hasattr(field, 'attname'):
                names.add(field.attname)
        return list(names)

else:
    def get_all_field_names(meta):
        return meta.get_all_field_names()
