from __future__ import absolute_import, with_statement

from django.core.exceptions import ImproperlyConfigured

from hosts.reverse import get_hostconf_module, get_host_patterns
from hosts.tests.base import override_settings, HostsTestCase

class ReverseTest(HostsTestCase):
    pass


class UtilityTests(HostsTestCase):

    @override_settings(ROOT_HOSTCONF='hosts.tests.hosts.simple')
    def test_get_hostconf_module(self):
        from hosts.tests.hosts import simple
        self.assertEqual(get_hostconf_module(), simple)

    def test_get_hostconf_module_no_default(self):
        from hosts.tests.hosts import simple
        self.assertEqual(get_hostconf_module('hosts.tests.hosts.simple'), simple)

    def test_get_host_patterns(self):
        self.assertRaisesWithMessage(ImproperlyConfigured,
            'Missing ROOT_HOSTCONF setting', get_host_patterns)

        with self.settings(ROOT_HOSTCONF='hosts.tests.hosts'):
            self.assertRaisesWithMessage(ImproperlyConfigured,
                "Missing host_patterns in 'hosts.tests.hosts'", get_host_patterns)

        with self.settings(ROOT_HOSTCONF='hosts.tests.hosts.simple'):
            from hosts.tests.hosts import simple
            self.assertEqual(get_host_patterns(), simple.host_patterns)
