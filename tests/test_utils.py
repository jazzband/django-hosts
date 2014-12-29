from __future__ import absolute_import, with_statement

from django.http import HttpResponse
from django.conf import settings
from django.test import RequestFactory
from django.test.utils import override_settings
from django.utils.cache import get_cache_key, learn_cache_key

from django_hosts.cache import _generate_cache_header_key
from django_hosts.utils import normalize_scheme, normalize_port

from .base import HostsTestCase


class UtilsTest(HostsTestCase):

    def test_normalize_scheme(self):
        self.assertEqual(normalize_scheme('http'), 'http://')
        self.assertEqual(normalize_scheme('http:'), 'http://')
        self.assertEqual(normalize_scheme(), '//')

    def test_normalize_port(self):
        self.assertEqual(normalize_port(None), '')
        self.assertEqual(normalize_port(':80:'), ':80')
        self.assertEqual(normalize_port('80'), ':80')
        self.assertEqual(normalize_port('80:'), ':80')
        self.assertEqual(normalize_port(), '')

    @override_settings(
        CACHE_MIDDLEWARE_KEY_PREFIX='settingsprefix',
        CACHE_MIDDLEWARE_SECONDS=1,
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            },
        },
        USE_I18N=False,
    )
    def test_generate_cache_header_key(self):
        """
        A test backported from Django stable/1.7.x to show that our patch to
        take the HOST header into account when generating cache middleware
        keys works.
        """
        host = 'www.example.com'
        path = '/cache/test/'
        factory = RequestFactory(HTTP_HOST=host)
        request = factory.get(path)

        response = HttpResponse()
        key_prefix = 'localprefix'
        # Expect None if no headers have been set yet.
        self.assertEqual(get_cache_key(request), None)
        # Set headers to an empty list.
        learn_cache_key(request, response)

        self.assertEqual(
            get_cache_key(request),
            'views.decorators.cache.cache_page.settingsprefix.GET.'
            '18a03f9c9649f7d684af5db3524f5c99.d41d8cd98f00b204e9800998ecf8427e'
        )

        # Verify that a specified key_prefix is taken into account.
        learn_cache_key(request, response, key_prefix=key_prefix)
        self.assertEqual(
            get_cache_key(request, key_prefix=key_prefix),
            'views.decorators.cache.cache_page.localprefix.GET.'
            '18a03f9c9649f7d684af5db3524f5c99.d41d8cd98f00b204e9800998ecf8427e'
        )
