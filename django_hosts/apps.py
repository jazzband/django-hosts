from django.apps import AppConfig
from django.conf import settings
from django.core import checks
from django.core.exceptions import ImproperlyConfigured
try:
    from django.template.base import add_to_builtins
except ImportError:  # Django 1.9+
    add_to_builtins = None
from django.utils.translation import ugettext_lazy as _

from .checks import check_default_host, check_root_hostconf


class HostsConfig(AppConfig):  # pragma: no cover
    """
    The django-hosts app config that conditionally adds its url to the
    built-ins of Django if the HOST_OVERRIDE_URL_TAG setting is set.
    """
    name = 'django_hosts'
    verbose_name = _('Hosts')

    def ready(self):
        checks.register(check_root_hostconf)
        checks.register(check_default_host)

        if getattr(settings, 'HOST_OVERRIDE_URL_TAG', False):
            if add_to_builtins:
                add_to_builtins('django_hosts.templatetags.hosts_override')
            else:
                raise ImproperlyConfigured(
                    "On Django 1.9+, you must add "
                    "'django_hosts.templatetags.hosts_override' to the "
                    "TEMPLATES['OPTIONS']['builtins'] list instead of using "
                    "the HOST_OVERRIDE_URL_TAG setting."
                )
