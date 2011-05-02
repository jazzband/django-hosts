from django import template
from django.conf import settings
from django.template import TemplateSyntaxError
from django.utils.encoding import smart_str
from django.template.defaulttags import kwarg_re

from ..reverse import reverse_crossdomain

register = template.Library()

@register.tag
def domain_url(parser, token, mangle=True):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least 1 argument" % bits[0])

    view = bits[1]
    bits = bits[1:] # Strip off view

    try:
        pivot = bits.index('on')

        try:
            domain = bits[pivot + 1]
        except IndexError:
            raise TemplateSyntaxError(
                "'%s' arguments must include a domain after 'on'" % bits[0])

        view_args, view_kwargs = parse_args_kwargs(parser, bits[1:pivot])
        domain_args, domain_kwargs = parse_args_kwargs(parser, bits[pivot+2:])

    except ValueError:
        # No "on <subdomain>" was specified so use the default domain
        domain = settings.SUBDOMAIN_DEFAULT
        view_args, view_kwargs = parse_args_kwargs(parser, bits[1:])
        domain_args, domain_kwargs = (), {}

    return DomainURLNode(domain, view,
        domain_args, domain_kwargs, view_args, view_kwargs, mangle)

@register.tag
def domain_url_no_mangle(parser, token):
    return domain_url(parser, token, mangle=False)

class DomainURLNode(template.Node):
    def __init__(self, subdomain, view, subdomain_args, subdomain_kwargs, view_args, view_kwargs, mangle):
        self.subdomain = subdomain
        self.view = view

        self.subdomain_args = subdomain_args
        self.subdomain_kwargs = subdomain_kwargs

        self.view_args = view_args
        self.view_kwargs = view_kwargs

        self.mangle = mangle

    def render(self, context):
        subdomain_args = [x.resolve(context) for x in self.subdomain_args]
        subdomain_kwargs = dict((smart_str(k, 'ascii'), v.resolve(context))
            for k, v in self.subdomain_kwargs.items())

        view_args = [x.resolve(context) for x in self.view_args]
        view_kwargs = dict((smart_str(k, 'ascii'), v.resolve(context))
            for k, v in self.view_kwargs.items())

        return reverse_crossdomain(
            self.subdomain,
            self.view,
            subdomain_args,
            subdomain_kwargs,
            view_args,
            view_kwargs,
            self.mangle,
        )

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
