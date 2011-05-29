from __future__ import absolute_import, with_statement

from django.core.exceptions import ImproperlyConfigured

from hosts import patterns, host
from hosts.reverse import get_host_patterns
from hosts.tests.base import HostsTestCase


class PatternsTests(HostsTestCase):

    def test_pattern(self):
        host_patterns = patterns('',
            host(r'api', 'api.urls', name='api'),
        )
        self.assertEqual(len(host_patterns), 1)
        self.assertTrue(isinstance(host_patterns['api'], host))

    def test_pattern_as_tuple(self):
        host_patterns = patterns('',
            (r'api', 'api.urls', 'api'),
        )
        self.assertEqual(len(host_patterns), 1)
        self.assertTrue(isinstance(host_patterns['api'], host))

    def test_pattern_with_duplicate(self):
        api_host = host(r'api', 'api.urls', name='api')
        self.assertRaises(ImproperlyConfigured, patterns, '', api_host, api_host)

    def test_pattern_with_default(self):
        default_host = host(r'www', 'mysite.urls', name='default')
        self.assertRaises(ImproperlyConfigured, patterns, '', default_host)


class HostTests(HostsTestCase):

    def test_host(self):
        api_host = host(r'api', 'api.urls', name='api')
        self.assertTrue(isinstance(api_host, host))

    def test_host_prefix(self):
        api_host = host(r'api', 'api.urls', name='api', prefix='spam.eggs')
        self.assertEqual(api_host.urlconf, 'spam.eggs.api.urls')

    def test_host_string_callback(self):
        api_host = host(r'api', 'api.urls', name='api', callback='hosts.reverse.get_host_patterns')
        self.assertEqual(api_host.callback, get_host_patterns)
