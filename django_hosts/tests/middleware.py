# -*- encoding: utf-8 -*-
from __future__ import absolute_import

from django.core.exceptions import ImproperlyConfigured

from django_hosts.middleware import HostsMiddleware
from django_hosts.tests.base import (override_settings, HostsTestCase,
                                     RequestFactory)


class MiddlewareTests(HostsTestCase):

    def test_missing_hostconf_setting(self):
        self.assertRaisesWithMessage(ImproperlyConfigured,
            'Missing ROOT_HOSTCONF setting', HostsMiddleware)

    @override_settings(ROOT_HOSTCONF='django_hosts.tests.hosts.simple')
    def test_missing_default_hosts(self):
        self.assertRaisesWithMessage(ImproperlyConfigured,
            'Missing DEFAULT_HOST setting', HostsMiddleware)

    @override_settings(
        ROOT_HOSTCONF='django_hosts.tests.hosts.simple',
        DEFAULT_HOST='boo')
    def test_wrong_default_hosts(self):
        self.assertRaisesWithMessage(ImproperlyConfigured,
            "Invalid DEFAULT_HOST setting: No host called 'boo' exists",
            HostsMiddleware)

    @override_settings(
        ROOT_HOSTCONF='django_hosts.tests.hosts.simple',
        DEFAULT_HOST='www')
    def test_request_urlconf_module(self):
        rf = RequestFactory(HTTP_HOST='other.example.com')
        request = rf.get('/simple/')
        middleware = HostsMiddleware()
        middleware.process_request(request)
        self.assertEqual(request.urlconf, 'django_hosts.tests.urls.simple')

    @override_settings(
        ROOT_HOSTCONF='django_hosts.tests.hosts.simple',
        DEFAULT_HOST='with_view_kwargs')
    def test_fallback_to_defaulthost(self):
        rf = RequestFactory(HTTP_HOST=u'ß.example.com')
        request = rf.get('/template/test/')
        middleware = HostsMiddleware()
        middleware.process_request(request)
        self.assertEqual(request.urlconf, 'django_hosts.tests.urls.complex')
