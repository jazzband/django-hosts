from __future__ import absolute_import, with_statement

from .base import HostsTestCase
from ..utils import normalize_scheme


class UtilsTest(HostsTestCase):

    def test_normalize_scheme(self):
        self.assertEqual(normalize_scheme('http'), 'http://')
        self.assertEqual(normalize_scheme('http:'), 'http://')
        self.assertEqual(normalize_scheme(), '//')
