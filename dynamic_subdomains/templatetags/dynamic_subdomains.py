import urllib

from django import template
from django.conf import settings
from django.template import TemplateSyntaxError
from django.core.urlresolvers import set_urlconf, get_urlconf
from django.utils.regex_helper import normalize
from django.template.defaulttags import url, URLNode, kwarg_re

from ..reverse import reverse_subdomain

register = template.Library()

@register.tag
def domain_url(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least 4 arguments" % bits[0])

    view_name = bits[1]
    bits = bits[1:] # Strip off view

    try:
        pivot = bits.index('on')

        try:
            domain = bits[pivot + 1]
        except IndexError:
            raise TemplateSyntaxError(
                "'%s' arguments must include a domain after 'on'" % bits[0]
            )

        view_args, view_kwargs = parse_args_kwargs(parser, bits[1:pivot])
        domain_args, domain_kwargs = parse_args_kwargs(parser, bits[pivot+2:])

    except ValueError:
        # No "on <subdomain>" was specified so use the default domain
        domain = settings.SUBDOMAIN_DEFAULT
        view_args, view_kwargs = parse_args_kwargs(parser, bits[1:])
        domain_args, domain_kwargs = (), {}

    return DomainURLNode(
        domain, domain_args, domain_kwargs, view_name, view_args, view_kwargs,
    )

class DomainURLNode(URLNode):
    def __init__(self, domain, domain_args, domain_kwargs, view_name, view_args, view_kwargs):
        self.domain = domain
        self.domain_args = domain_args
        self.domain_kwargs = domain_kwargs

        super(DomainURLNode, self).__init__(view_name, view_args, view_kwargs, None)

    def render(self, context):
        domain_part = reverse_subdomain(
            self.domain,
            args=self.domain_args,
            kwargs=self.domain_kwargs,
        )

        try:
            subdomain = settings.SUBDOMAINS[self.domain]
        except KeyError:
            raise TemplateSyntaxError(
                "Subdomain name %r could not be found" % self.domain
            )

        prev = get_urlconf()
        try:
            set_urlconf(subdomain['urlconf'])
            path_part = super(DomainURLNode, self).render(context)
        finally:
            set_urlconf(prev)

        return '//%s%s' % (domain_part, path_part)

def parse_args_kwargs(parser, bits):
    args = []
    kwargs = {}

    for bit in bits:
        match = kwarg_re.match(bit)
        if not match:
            raise TemplateSyntaxError("Malformed arguments to domain_url tag")

        name, value = match.groups()
        if name:
            kwargs[name] = parser.compile_filter(value)
        else:
            args.append(parser.compile_filter(value))

    return args, kwargs
