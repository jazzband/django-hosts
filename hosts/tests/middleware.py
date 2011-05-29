from __future__ import absolute_import

from django.conf import settings
from django.test import TestCase, RequestFactory
from django.core.exceptions import MiddlewareNotUsed, ImproperlyConfigured

from hosts.defaults import patterns, host
from hosts.middleware import HostsMiddleware
from hosts.tests.base import override_settings, HostsTestCase

class MiddlewareTests(HostsTestCase):

    def test_missing_hostconf_setting(self):
        self.assertRaisesWithMessage(ImproperlyConfigured,
            'Missing ROOT_HOSTCONF setting', HostsMiddleware)

    @override_settings(ROOT_HOSTCONF='hosts.tests.hosts.simple')
    def test_missing_default_hosts(self):
        self.assertRaisesWithMessage(ImproperlyConfigured,
            'Missing DEFAULT_HOST setting', HostsMiddleware)

    @override_settings(
        ROOT_HOSTCONF='hosts.tests.hosts.simple',
        DEFAULT_HOST='boo')
    def test_wrong_default_hosts(self):
        self.assertRaisesWithMessage(ImproperlyConfigured,
            'Invalid DEFAULT_HOST setting', HostsMiddleware)

    @override_settings(
        ROOT_HOSTCONF='hosts.tests.hosts.simple',
        DEFAULT_HOST='www')
    def test_request_urlconf_module(self):
        rf = RequestFactory(HTTP_HOST='other.example.com')
        request = rf.get('/simple/')
        middleware = HostsMiddleware()
        middleware.process_request(request)
        self.assertEqual(request.urlconf, 'hosts.tests.urls.simple')