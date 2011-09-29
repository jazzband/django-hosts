from __future__ import absolute_import, with_statement

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch

from django_hosts.tests.base import override_settings, HostsTestCase
from django_hosts.reverse import (get_hostconf_module, get_host_patterns,
    get_host, reverse_host, reverse_full)


class ReverseTest(HostsTestCase):

    @override_settings(ROOT_HOSTCONF='django_hosts.tests.hosts.simple')
    def test_reverse_host(self):
        self.assertRaises(ValueError,
            reverse_host, 'with_kwargs', ['spam'], dict(eggs='spam'))
        self.assertRaises(NoReverseMatch,
            reverse_host, 'with_kwargs', ['spam', 'eggs'])
        self.assertRaises(NoReverseMatch,
            reverse_host, 'with_kwargs', [], dict(eggs='spam', spam='eggs'))
        self.assertEqual('johndoe',
            reverse_host('with_kwargs', None, dict(username='johndoe')))
        self.assertEqual(reverse_host('with_args', ['johndoe']), 'johndoe')
        with self.settings(PARENT_HOST='spam.eggs'):
            self.assertEqual(reverse_host('with_args', ['johndoe']),
                             'johndoe.spam.eggs')

    @override_settings(
        ROOT_HOSTCONF='django_hosts.tests.hosts.simple',
        PARENT_HOST='spam.eggs')
    def test_reverse_full(self):
        self.assertEqual(reverse_full('static', 'simple-direct'),
                         '//static.spam.eggs/simple/')


class UtilityTests(HostsTestCase):

    @override_settings(ROOT_HOSTCONF='django_hosts.tests.hosts.simple')
    def test_get_hostconf_module(self):
        from django_hosts.tests.hosts import simple
        self.assertEqual(get_hostconf_module(), simple)

    def test_get_hostconf_module_no_default(self):
        from django_hosts.tests.hosts import simple
        self.assertEqual(
            get_hostconf_module('django_hosts.tests.hosts.simple'), simple)

    def test_missing_host_patterns(self):
        self.assertRaisesWithMessage(ImproperlyConfigured,
            'Missing ROOT_HOSTCONF setting', get_host_patterns)

    @override_settings(ROOT_HOSTCONF='django_hosts.tests.hosts')
    def test_missing_host_patterns_in_module(self):
        self.assertRaisesWithMessage(ImproperlyConfigured,
            "Missing host_patterns in 'django_hosts.tests.hosts'",
            get_host_patterns)

    @override_settings(ROOT_HOSTCONF='django_hosts.tests.hosts.simple')
    def test_get_working_host_patterns(self):
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
