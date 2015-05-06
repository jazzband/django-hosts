from django.http import HttpResponse
from django.test import RequestFactory
from django.test.utils import override_settings
from django.core.exceptions import ImproperlyConfigured

from django_hosts.middleware import (HostsRequestMiddleware,
                                     HostsResponseMiddleware)

from .base import HostsTestCase


class MiddlewareTests(HostsTestCase):

    def test_missing_hostconf_setting(self):
        self.assertRaisesMessage(ImproperlyConfigured,
            'Missing ROOT_HOSTCONF setting', HostsRequestMiddleware)

    @override_settings(ROOT_HOSTCONF='tests.hosts.simple')
    def test_missing_default_hosts(self):
        self.assertRaisesMessage(ImproperlyConfigured,
            'Missing DEFAULT_HOST setting', HostsRequestMiddleware)

    @override_settings(
        ROOT_HOSTCONF='tests.hosts.simple',
        DEFAULT_HOST='boo')
    def test_wrong_default_hosts(self):
        self.assertRaisesMessage(ImproperlyConfigured,
            "Invalid DEFAULT_HOST setting: No host called 'boo' exists",
            HostsRequestMiddleware)

    @override_settings(
        ROOT_HOSTCONF='tests.hosts.simple',
        DEFAULT_HOST='www')
    def test_request_urlconf_module(self):
        rf = RequestFactory(HTTP_HOST='other.example.com')
        request = rf.get('/simple/')
        middleware = HostsRequestMiddleware()
        middleware.process_request(request)
        self.assertEqual(request.urlconf, 'tests.urls.simple')

    @override_settings(
        ROOT_HOSTCONF='tests.hosts.simple',
        DEFAULT_HOST='www')
    def test_response_urlconf_module(self):
        rf = RequestFactory(HTTP_HOST='other.example.com')
        request = rf.get('/simple/')
        middleware = HostsResponseMiddleware()
        middleware.process_response(request, HttpResponse('test'))
        self.assertEqual(request.urlconf, 'tests.urls.simple')

    @override_settings(
        ROOT_HOSTCONF='tests.hosts.simple',
        DEFAULT_HOST='with_view_kwargs')
    def test_fallback_to_defaulthost(self):
        rf = RequestFactory(HTTP_HOST='ss.example.com')
        request = rf.get('/template/test/')
        middleware = HostsRequestMiddleware()
        middleware.process_request(request)
        self.assertEqual(request.urlconf, 'tests.urls.complex')
        host, kwargs = middleware.get_host('non-existing')
        self.assertEqual(host.name, 'with_view_kwargs')

    @override_settings(
        ROOT_HOSTCONF='tests.hosts.simple',
        DEFAULT_HOST='www',
        ALLOWED_HOSTS=['somehost.com'],
        DEBUG=False,
        MIDDLEWARE_CLASSES=[
            'django_hosts.middleware.HostsRequestMiddleware',
            'django_hosts.middleware.HostsResponseMiddleware',
        ])
    def test_fallback_with_evil_host(self):
        response = self.client.get('/', HTTP_HOST='evil.com')
        self.assertEqual(response.status_code, 400)

    @override_settings(
        ROOT_HOSTCONF='tests.hosts.multiple',
        DEFAULT_HOST='multiple')
    def test_multiple_subdomains(self):
        rf = RequestFactory(HTTP_HOST='spam.eggs.example.com')
        request = rf.get('/multiple/')
        middleware = HostsRequestMiddleware()
        middleware.process_request(request)
        self.assertEqual(request.urlconf, 'tests.urls.multiple')

    @override_settings(
        MIDDLEWARE_CLASSES=['debug_toolbar.middleware.DebugToolbarMiddleware',
                            'django_hosts.middleware.HostsRequestMiddleware'],
        ROOT_HOSTCONF='tests.hosts.multiple',
        DEFAULT_HOST='multiple')
    def test_debug_toolbar_new_warning(self):
        self.assertRaises(ImproperlyConfigured, HostsRequestMiddleware)

    @override_settings(
        MIDDLEWARE_CLASSES=['debug_toolbar.middleware.DebugToolbarMiddleware',
                            'django_hosts.middleware.HostsMiddleware'],
        ROOT_HOSTCONF='tests.hosts.multiple',
        DEFAULT_HOST='multiple')
    def test_debug_toolbar_old_warning(self):
        self.assertRaises(ImproperlyConfigured, HostsRequestMiddleware)
