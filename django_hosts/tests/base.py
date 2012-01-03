from __future__ import absolute_import, with_statement

from django.conf import settings, UserSettingsHolder
from django.core.handlers.wsgi import WSGIRequest
from django.core.handlers.base import BaseHandler
from django.test import TestCase, Client
from django.utils.functional import wraps

from ..reverse import clear_host_caches


class override_settings(object):
    """
    Acts as either a decorator, or a context manager.  If it's a decorator it
    takes a function and returns a wrapped function.  If it's a contextmanager
    it's used with the ``with`` statement.  In either event entering/exiting
    are called before and after, respectively, the function/block is executed.
    """
    def __init__(self, **kwargs):
        self.options = kwargs
        self.wrapped = settings._wrapped

    def __enter__(self):
        self.enable()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disable()

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return inner

    def enable(self):
        override = UserSettingsHolder(settings._wrapped)
        for key, new_value in self.options.items():
            setattr(override, key, new_value)
        settings._wrapped = override

    def disable(self):
        settings._wrapped = self.wrapped


# Adapted from Simon Willison's snippet:
# http://djangosnippets.org/snippets/963/.
class RequestFactory(Client):
    """
    Class that lets you create mock Request objects for use in testing.

    Usage:

    rf = RequestFactory()
    get_request = rf.get('/hello/')
    post_request = rf.post('/submit/', {'foo': 'bar'})

    This class re-uses the django.test.client.Client interface, docs here:
    http://www.djangoproject.com/documentation/testing/#the-test-client

    Once you have a request object you can pass it to any view function,
    just as if that view had been hooked up using a URLconf.

    """
    def request(self, **request):
        """
        Similar to parent class, but returns the request object as soon as it
        has created it.
        """
        environ = {
            'HTTP_COOKIE': self.cookies,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': 80,
            'SERVER_PROTOCOL': 'HTTP/1.1',
        }
        environ.update(self.defaults)
        environ.update(request)
        request = WSGIRequest(environ)

        handler = BaseHandler()
        handler.load_middleware()
        for middleware_method in handler._request_middleware:
            if middleware_method(request):
                raise Exception("Couldn't create request object - "
                                "request middleware returned a response")
        return request


class HostsTestCase(TestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.old_apps = settings.INSTALLED_APPS
        settings.INSTALLED_APPS = tuple(settings.INSTALLED_APPS) + ('django_hosts.tests',)

    def tearDown(self):
        clear_host_caches()
        settings.INSTALLED_APPS = self.old_apps

    def assertRaisesWithMessage(self, error,
                                message, callable, *args, **kwargs):
        self.assertRaises(error, callable, *args, **kwargs)
        try:
            callable(*args, **kwargs)
        except error, e:
            self.assertEqual(message, str(e))

    def assertNumQueries(self, num, callable, *args, **kwargs):
        from django.db import connection
        if hasattr(connection, 'use_debug_cursor'):
            old_use_debug_cursor = connection.use_debug_cursor
            connection.use_debug_cursor = True
            old_debug = None
        else:
            old_use_debug_cursor = None
            old_debug = settings.DEBUG
            settings.DEBUG = True
        starting_queries = len(connection.queries)
        try:
            callable(*args, **kwargs)
        finally:
            final_queries = len(connection.queries)
            if old_use_debug_cursor is not None:
                connection.use_debug_cursor = old_use_debug_cursor
            elif old_debug is not None:
                settings.DEBUG = old_debug
            executed = final_queries - starting_queries
            self.assertEqual(executed, num,
                             "%s queries executed, %s expected" %
                             (executed, num))

    def settings(self, **kwargs):
        """
        A context manager that temporarily sets a setting and reverts
        back to the original value when exiting the context.
        """
        return override_settings(**kwargs)
