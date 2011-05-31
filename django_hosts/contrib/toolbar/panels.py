from django.http.utils import fix_location_header
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.core.handlers.base import BaseHandler

from debug_toolbar.panels import DebugPanel


class HostPanel(DebugPanel):
    """
    Panel that allows you to alter the host you are viewing the site
    without /etc/hosts hacks.
    """

    name = 'Host'
    has_content = True

    def nav_title(self):
        return _("Host")

    def nav_subtitle(self):
        return self.host

    def url(self):
        return ''

    def title(self):
        return _("Host navigation")

    def content(self):
        context = self.context.copy()
        context['host'] = self.host
        return render_to_string('django_hosts/panel.html', context)

    def process_request(self, request):
        self.host = request.COOKIES.get('_host')

        request.META.pop('HTTP_HOST', '')
        if self.host:
            request.META['HTTP_HOST'] = self.host

            # django.http.utils.fix_location_header rewrites any relative
            # Location header to an absolute one. For example:
            #
            #    Location: /foo   ==>   Location: http://sub.example.com/foo
            #
            # This causes problems when testing hosts locally so we remove
            # it here.

            try:
                BaseHandler.response_fixes.remove(fix_location_header)
            except ValueError:
                pass
