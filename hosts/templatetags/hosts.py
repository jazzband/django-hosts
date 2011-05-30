from __future__ import absolute_import

import re
from django import template
from django.conf import settings
from django.template import TemplateSyntaxError
from django.utils.encoding import smart_str

from hosts.reverse import reverse_crossdomain

register = template.Library()

kwarg_re = re.compile(r"(?:(\w+)=)?(.+)")

class HostURLNode(template.Node):

    @staticmethod
    def parse_args_kwargs(parser, bits):
        args, kwargs = [], {}
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError('Malformed arguments to host_url tag')
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))
        return args, kwargs

    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()
        if len(bits) < 2:
            raise TemplateSyntaxError("'%s' takes at least 1 argument" % bits[0])
        view = bits[1]
        bits = bits[1:] # Strip off view
        try:
            pivot = bits.index('on')
            try:
                host = bits[pivot+1]
            except IndexError:
                raise TemplateSyntaxError(
                    "'%s' arguments must include a host after 'on'" % bits[0])
            view_args, view_kwargs = cls.parse_args_kwargs(parser, bits[1:pivot])
            host_args, host_kwargs = cls.parse_args_kwargs(parser, bits[pivot+2:])

        except ValueError:
            # No "on <host>" was specified so use the default host
            host = settings.DEFAULT_HOST
            view_args, view_kwargs = cls.parse_args_kwargs(parser, bits[1:])
            host_args, host_kwargs = (), {}

        return cls(host, view, host_args, host_kwargs, view_args, view_kwargs)

    def __init__(self, host, view, host_args, host_kwargs, view_args, view_kwargs):
        self.host = host
        self.view = view
        self.host_args = host_args
        self.host_kwargs = host_kwargs
        self.view_args = view_args
        self.view_kwargs = view_kwargs

    def render(self, context):
        host_args = [x.resolve(context) for x in self.host_args]
        host_kwargs = dict((smart_str(k, 'ascii'), v.resolve(context))
                            for k, v in self.host_kwargs.iteritems())
        view_args = [x.resolve(context) for x in self.view_args]
        view_kwargs = dict((smart_str(k, 'ascii'), v.resolve(context))
                            for k, v in self.view_kwargs.iteritems())
        return reverse_crossdomain(self.host, self.view,
            host_args, host_kwargs, view_args, view_kwargs)


@register.tag
def host_url(parser, token):
    """
    Simple tag to reverse the URL inclusing a host.

    {% host_url url-name on host-name  %}
    {% host_url url-name on host-name 'spam' %}

    """
    return HostURLNode.handle_token(parser, token)
