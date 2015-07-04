import pytest
from django.test import TestCase, RequestFactory


@pytest.mark.django_db()
class HostsTestCase(TestCase):

    def setUp(self):
        super(HostsTestCase, self).setUp()
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def assertRaisesMessageIn(self, error,
                              message, callable, *args, **kwargs):
        self.assertRaises(error, callable, *args, **kwargs)
        try:
            callable(*args, **kwargs)
        except error as exc:
            self.assertIn(message, str(exc))
