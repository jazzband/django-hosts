from django import VERSION


if VERSION[0:2] >= (1, 10):
    from django.utils.deprecation import MiddlewareMixin

else:
    class MiddlewareMixin(object):
        pass
