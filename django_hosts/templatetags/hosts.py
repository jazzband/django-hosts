import re
import warnings

from django import template
from django.template import TemplateSyntaxError
from django.utils import six
from django.template.base import FilterExpression
from django.template.defaulttags import URLNode
from django.utils.encoding import smart_str

from ..resolvers import reverse

register = template.Library()

kwarg_re = re.compile(r"(?:(\w+)=)?(.+)")


class HostURLNode(URLNode):

    def __init__(self, *args, **kwargs):
        self.host = kwargs.pop('host')
        self.host_args = kwargs.pop('host_args')
        self.host_kwargs = kwargs.pop('host_kwargs')
        self.scheme = kwargs.pop('scheme')
        self.port = kwargs.pop('port')
        super(HostURLNode, self).__init__(*args, **kwargs)

    def maybe_resolve(self, var, context):
        """
        Variable may have already been resolved
        in e.g. a LoopNode, so we only resolve()
        if needed.
        """
        if isinstance(var, FilterExpression):
            return var.resolve(context)
        return var

    def render(self, context):
        view_name = self.view_name.resolve(context)

        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict((smart_str(k, 'ascii'), v.resolve(context))
                              for k, v in self.kwargs.items())

        host = self.maybe_resolve(self.host, context)
        host_args = [self.maybe_resolve(x, context) for x in self.host_args]

        host_kwargs = dict((smart_str(k, 'ascii'),
                            self.maybe_resolve(v, context))
                           for k, v in six.iteritems(self.host_kwargs))

        scheme = self.maybe_resolve(self.scheme, context)
        port = self.maybe_resolve(self.port, context)

        uri = reverse(view_name, args, kwargs, None, context.current_app,
                      host, host_args, host_kwargs, scheme, port)

        if self.asvar:
            context[self.asvar] = uri
            return ''
        else:
            return uri


def parse_params(name, parser, bits):
    args = []
    kwargs = {}
    for bit in bits:
        match = kwarg_re.match(bit)
        if not match:
            raise TemplateSyntaxError("Malformed arguments to %s tag" % name)
        name, value = match.groups()
        if name:
            kwargs[name] = parser.compile_filter(value)
        else:
            args.append(parser.compile_filter(value))
    return args, kwargs


def fetch_arg(name, arg, bits, consume=True):
    try:
        pivot = bits.index(arg)
        try:
            value = bits[pivot + 1]
        except IndexError:
            raise TemplateSyntaxError("'%s' arguments must include "
                                      "a variable name after '%s'" %
                                      (name, arg))
        else:
            if consume:
                del bits[pivot:pivot + 2]
            return value, pivot, bits
    except ValueError:
        return None, None, bits


@register.tag
def host_url(parser, token):
    """
    Simple tag to reverse the URL inclusing a host.

    {% host_url 'view-name' host 'host-name'  %}
    {% host_url 'view-name' host 'host-name' 'spam' %}
    {% host_url 'view-name' host 'host-name' scheme 'https' %}
    {% host_url 'view-name' host 'host-name' as url_on_host_variable %}
    {% host_url 'view-name' varg1=vvalue1 host 'host-name' 'spam' 'hvalue1' %}
    {% host_url 'view-name' vvalue2 host 'host-name' 'spam' harg2=hvalue2 %}
    """
    bits = token.split_contents()
    name = bits[0]
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % name)

    try:
        view_name = parser.compile_filter(bits[1])
    except TemplateSyntaxError as exc:
        exc.args = (exc.args[0] + ". "
                    "The syntax of the 'url' template tag has changed in "
                    "Django 1.5, see the docs. The view name is now "
                    "quoted unless it's meant as a variable."),
        raise

    asvar, pivot, bits = fetch_arg(name, 'as', bits[1:])  # Strip off viewname
    scheme, pivot, bits = fetch_arg(name, 'scheme', bits)
    if scheme:
        scheme = parser.compile_filter(scheme)
    port, pivot, bits = fetch_arg(name, 'port', bits)
    if port:
        port = parser.compile_filter(port)

    host, pivot, bits = fetch_arg(name, 'host', bits, consume=False)

    if host is None:
        host, pivot, bits = fetch_arg(name, 'on', bits, consume=False)
        warnings.warn("The 'on' keyword of the '%s' template tag is pending "
                      "deprecation in favor of the 'host' keyword. Please "
                      "upgrade your templates accordingly.",
                      PendingDeprecationWarning)

    if host:
        host = parser.compile_filter(host)
        view_args, view_kwargs = parse_params(name, parser, bits[1:pivot])
        host_args, host_kwargs = parse_params(name, parser, bits[pivot + 2:])
    else:
        host = None
        view_args, view_kwargs = parse_params(name, parser, bits[1:])
        host_args, host_kwargs = (), {}

    return HostURLNode(view_name=view_name, args=view_args, kwargs=view_kwargs,
                       asvar=asvar, host=host, host_args=host_args,
                       host_kwargs=host_kwargs, scheme=scheme, port=port)
