from django.apps import AppConfig
from django.conf import settings
from django.core import checks
try:
    from django.template.base import add_to_builtins
except ImportError:  # Django < 1.8
    from django.template import add_to_builtins
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
            add_to_builtins('django_hosts.templatetags.hosts_override')
