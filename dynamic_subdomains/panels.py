from debug_toolbar.panels import DebugPanel

from django.http.utils import fix_location_header
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.core.handlers.base import BaseHandler

class SubdomainPanel(DebugPanel):
    """
    Panel that allows you to alter the subdomain you are viewing the site
    without /etc/hosts hacks.
    """

    name = 'Subdomain'
    has_content = True

    def nav_title(self):
        return _("Subdomain")

    def nav_subtitle(self):
        return self.domain

    def url(self):
        return ''

    def title(self):
        return _("Subdomain navigation")

    def content(self):
        context = self.context.copy()
        context['domain'] = self.domain
        return render_to_string('subdomains/panel.html', context)

    def process_request(self, request):
        self.domain = request.COOKIES.get('_domain')

        request.META.pop('HTTP_HOST', '')
        if self.domain:
            request.META['HTTP_HOST'] = self.domain

            # django.http.utils.fix_location_header rewrites any relative
            # Location header to an absolute one. For example:
            #
            #    Location: /foo   ==>   Location: http://sub.example.com/foo
            #
            # This causes problems when testing subdomains locally so we remove
            # it here.

            try:
                BaseHandler.response_fixes.remove(fix_location_header)
            except ValueError:
                pass
