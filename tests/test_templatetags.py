from __future__ import absolute_import, with_statement

from django.template import Template, Context, TemplateSyntaxError
try:
    from django.template.base import Parser
except ImportError:  # Django < 1.8
    from django.template import Parser
from django.test.utils import override_settings

from django_hosts.templatetags.hosts import parse_params

from .base import HostsTestCase


class TemplateTagsTest(HostsTestCase):

    def render(self, template, context=None):
        if context is None:
            context = Context({})
        return Template('{% load hosts %}' + template).render(context)

    def assertRender(self, template, expected, context=None):
        rendered = self.render(template, context)
        self.assertEqual(expected, rendered.strip())

    @override_settings(
        DEFAULT_HOST='www',
        ROOT_HOSTCONF='tests.hosts.simple')
    def test_host_url_tag_simple(self):
        self.assertRender("{% host_url 'simple-direct' host 'www' %}",
                          '//www.example.com/simple/')
        self.assertRender("{% host_url 'simple-direct' host 'www' as "
                          "simple_direct_url %}{{ simple_direct_url }}",
                          '//www.example.com/simple/')

    @override_settings(
        DEFAULT_HOST='www',
        ROOT_HOSTCONF='tests.hosts.simple')
    def test_url_tag_override(self):
        # we should be setting HOST_OVERRIDE_URL_TAG to True
        # but that doesn't really work since that setting is read only
        # on import time for Django < 1.7 and on setup time for >= 1.7
        # so we have to fake it by manually setting the stage
        try:
            from django.template.base import add_to_builtins
        except ImportError:  # Django < 1.8
            from django.template import add_to_builtins
        add_to_builtins('django_hosts.templatetags.hosts_override')

        self.assertRender("{% url 'simple-direct' host 'www' %}",
                          '//www.example.com/simple/')
        self.assertRender("{% url 'simple-direct' host 'www' as "
                          "simple_direct_url %}{{ simple_direct_url }}",
                          '//www.example.com/simple/')

    @override_settings(
        ROOT_HOSTCONF='tests.hosts.simple',
        HOST_STICKY=False)
    def test_host_url_tag_loop(self):
        self.assertRender("{% host_url 'simple-direct' %}", '//example.com/simple/')
        self.assertRender("{% host_url 'multiple-direct' %}", '//loop/multiple/')

    @override_settings(
        DEFAULT_HOST='www',
        ROOT_HOSTCONF='tests.hosts.simple')
    def test_host_url_tag_without_host(self):
        self.assertRender("{% host_url 'simple-direct' %}",
                          '//www.example.com/simple/')

    @override_settings(
        DEFAULT_HOST='www',
        ROOT_HOSTCONF='tests.hosts.simple')
    def test_host_url_tag_with_scheme(self):
        self.assertRender("{% host_url 'simple-direct' scheme 'http' %}",
                          'http://www.example.com/simple/')
        self.assertRender("{% host_url 'simple-direct' scheme 'git' %}",
                          'git://www.example.com/simple/')

    @override_settings(
        DEFAULT_HOST='port-tag',
        ROOT_HOSTCONF='tests.hosts.simple',
        HOST_SCHEME='http',
        PARENT_HOST='example.com')
    def test_host_url_tag_with_port(self):
        self.assertRender("{% host_url 'simple-direct' port '8000' %}",
                          'http://port-tag.example.com:8000/simple/')

    @override_settings(
        DEFAULT_HOST='www',
        ROOT_HOSTCONF='tests.hosts.simple')
    def test_host_url_tag_with_args(self):
        self.assertRender(
            "{% host_url 'simple-direct' host 'with_args' 'www.eggs.spam' %}",
            '//www.eggs.spam/simple/')
        self.assertRender("{% host_url 'simple-direct' as yeah "
                          "host 'with_args' 'www.eggs.spam' %}{{ yeah }}",
                          '//www.eggs.spam/simple/')

    @override_settings(
        DEFAULT_HOST='www',
        PARENT_HOST='eggs.spam',
        ROOT_HOSTCONF='tests.hosts.simple')
    def test_host_url_tag_with_kwargs(self):
        self.assertRender(
            "{% host_url 'simple-direct' "
            "host 'with_kwargs' username='johndoe' %}",
            '//johndoe.eggs.spam/simple/')

    @override_settings(
        DEFAULT_HOST='www',
        PARENT_HOST='eggs.spam',
        ROOT_HOSTCONF='tests.hosts.simple')
    def test_host_url_tag_with_view_kwargs(self):
        self.assertRender(
            "{% host_url 'complex-direct' template='test' "
            "host 'with_view_kwargs' subdomain='test2000' %}",
            '//stest2000.eggs.spam/template/test/')

    @override_settings(
        DEFAULT_HOST='www',
        ROOT_HOSTCONF='tests.hosts.simple',
        PARENT_HOST='eggs.spam')
    def test_host_url_tag_parent_host(self):
        self.assertRender("{% host_url 'simple-direct' host 'static' %}",
                          '//static.eggs.spam/simple/')

    @override_settings(
        DEFAULT_HOST='without_www',
        ROOT_HOSTCONF='tests.hosts.simple',
        PARENT_HOST='example.com')
    def test_host_url_no_www(self):
        self.assertRender("{% host_url 'simple-direct' host 'without_www' %}",
                          '//example.com/simple/')

    @override_settings(
        DEFAULT_HOST='www',
        ROOT_HOSTCONF='tests.hosts.simple')
    def test_raises_template_syntaxerror(self):
        self.assertRaises(TemplateSyntaxError,
                          self.render, "{% host_url %}")
        self.assertRaises(TemplateSyntaxError, self.render,
                          "{% host_url 'simple-direct' host %}")
        self.assertRaises(TemplateSyntaxError, self.render,
                          "{% host_url 'simple-direct' as %}")
        self.assertRaises(TemplateSyntaxError, self.render,
                          "{% host_url simple-direct %}")
        self.assertRaises(TemplateSyntaxError, parse_params,
                          'host_url', Parser(['']), "username=='johndoe'")
        self.assertRaises(TemplateSyntaxError, parse_params,
                          'host_url', Parser(['']), "\n='johndoe'")
