from __future__ import absolute_import, with_statement

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch

from django_hosts.reverse import get_hostconf_module, get_host_patterns, get_host
from django_hosts.tests.base import override_settings, HostsTestCase

class ReverseTest(HostsTestCase):
    pass


class UtilityTests(HostsTestCase):

    @override_settings(ROOT_HOSTCONF='django_hosts.tests.hosts.simple')
    def test_get_hostconf_module(self):
        from django_hosts.tests.hosts import simple
        self.assertEqual(get_hostconf_module(), simple)

    def test_get_hostconf_module_no_default(self):
        from django_hosts.tests.hosts import simple
        self.assertEqual(get_hostconf_module('django_hosts.tests.hosts.simple'), simple)

    def test_get_host_patterns(self):
        self.assertRaisesWithMessage(ImproperlyConfigured,
            'Missing ROOT_HOSTCONF setting', get_host_patterns)

        with self.settings(ROOT_HOSTCONF='django_hosts.tests.hosts'):
            self.assertRaisesWithMessage(ImproperlyConfigured,
                "Missing host_patterns in 'django_hosts.tests.hosts'", get_host_patterns)

        with self.settings(ROOT_HOSTCONF='django_hosts.tests.hosts.simple'):
            from django_hosts.tests.hosts import simple
            self.assertEqual(get_host_patterns(), simple.host_patterns)

    @override_settings(ROOT_HOSTCONF='django_hosts.tests.hosts.simple')
    def test_get_host(self):
        self.assertEqual(get_host('static').name, 'static')
        self.assertRaisesWithMessage(NoReverseMatch,
            "No host called 'non-existent' exists", get_host, 'non-existent')

    @override_settings(ROOT_HOSTCONF='django_hosts.tests.hosts.appended')
    def test_appended_patterns(self):
        self.assertEqual(get_host('special').name, 'special')
