import re
from django import template
from django.conf import settings
from django.template import TemplateSyntaxError
from django.utils.encoding import smart_str

from django_hosts.reverse import reverse_full

register = template.Library()

kwarg_re = re.compile(r"(?:(\w+)=)?(.+)")


class HostURLNode(template.Node):

    @classmethod
    def parse_params(cls, parser, bits):
        args, kwargs = [], {}
        for bit in bits:
            name, value = kwarg_re.match(bit).groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))
        return args, kwargs

    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()
        name = bits[0]
        if len(bits) < 2:
            raise TemplateSyntaxError("'%s' takes at least 1 argument" % name)
        view = bits[1]
        bits = bits[1:]  # Strip off view
        asvar = None
        if 'as' in bits:
            pivot = bits.index('as')
            try:
                asvar = bits[pivot + 1]
            except IndexError:
                raise TemplateSyntaxError("'%s' arguments must include "
                                          "a variable name after 'as'" % name)
            del bits[pivot:pivot + 2]
        try:
            pivot = bits.index('on')
            try:
                host = bits[pivot + 1]
            except IndexError:
                raise TemplateSyntaxError("'%s' arguments must include "
                                          "a host after 'on'" % name)
            view_args, view_kwargs = cls.parse_params(parser, bits[1:pivot])
            host_args, host_kwargs = cls.parse_params(parser, bits[pivot + 2:])
        except ValueError:
            # No host was given so use the default host
            host = settings.DEFAULT_HOST
            view_args, view_kwargs = cls.parse_params(parser, bits[1:])
            host_args, host_kwargs = (), {}
        return cls(host, view, host_args, host_kwargs, view_args, view_kwargs, asvar)

    def __init__(self, host, view,
                 host_args, host_kwargs, view_args, view_kwargs, asvar):
        self.host = host
        self.view = view
        self.host_args = host_args
        self.host_kwargs = host_kwargs
        self.view_args = view_args
        self.view_kwargs = view_kwargs
        self.asvar = asvar

    def render(self, context):
        host_args = [x.resolve(context) for x in self.host_args]
        host_kwargs = dict((smart_str(k, 'ascii'), v.resolve(context))
                            for k, v in self.host_kwargs.iteritems())
        view_args = [x.resolve(context) for x in self.view_args]
        view_kwargs = dict((smart_str(k, 'ascii'), v.resolve(context))
                            for k, v in self.view_kwargs.iteritems())
        url = reverse_full(self.host, self.view,
                            host_args, host_kwargs, view_args, view_kwargs)
        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            return url


@register.tag
def host_url(parser, token):
    """
    Simple tag to reverse the URL inclusing a host.

    {% host_url url-name on host-name  %}
    {% host_url url-name on host-name as url_on_host_variable %}
    {% host_url url-name on host-name 'spam' %}
    {% host_url url-name varg1=vvalue1 on host-name 'spam' 'hvalue1' %}
    {% host_url url-name vvalue2 on host-name 'spam' harg2=hvalue2 %}

    """
    return HostURLNode.handle_token(parser, token)
