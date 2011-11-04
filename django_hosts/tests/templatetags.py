from __future__ import absolute_import, with_statement

from django.template import Template, Context, TemplateSyntaxError, Parser

from django_hosts.templatetags.hosts import HostURLNode
from django_hosts.tests.base import override_settings, HostsTestCase


class TemplateTagsTest(HostsTestCase):

    def render(self, template, context=None):
        if context is None:
            context = Context({})
        return Template(template).render(context).strip()

    @override_settings(
        DEFAULT_HOST='www',
        ROOT_HOSTCONF='django_hosts.tests.hosts.simple')
    def test_host_url_tag_simple(self):
        rendered = self.render(
            "{% load hosts %}{% host_url simple-direct on www %}")
        self.assertEqual(rendered, '//www.example.com/simple/')
        rendered = self.render(
            "{% load hosts %}{% host_url simple-direct on www as "
            "simple_direct_url %}{{ simple_direct_url }} ")
        self.assertEqual(rendered, '//www.example.com/simple/')

    @override_settings(
        DEFAULT_HOST='www',
        ROOT_HOSTCONF='django_hosts.tests.hosts.simple')
    def test_host_url_tag_without_on(self):
        rendered = self.render(
            "{% load hosts %}{% host_url simple-direct %}")
        self.assertEqual(rendered, '//www.example.com/simple/')

    @override_settings(
        DEFAULT_HOST='www',
        ROOT_HOSTCONF='django_hosts.tests.hosts.simple')
    def test_host_url_tag_with_args(self):
        rendered = self.render("{% load hosts %}"
            "{% host_url simple-direct on with_args 'www.eggs.spam' %}")
        self.assertEqual(rendered, '//www.eggs.spam/simple/')
        rendered = self.render("{% load hosts %}"
            "{% host_url simple-direct as yeah on with_args "
            "'www.eggs.spam' %}{{ yeah }}")
        self.assertEqual(rendered, '//www.eggs.spam/simple/')

    @override_settings(
        DEFAULT_HOST='www',
        PARENT_HOST='eggs.spam',
        ROOT_HOSTCONF='django_hosts.tests.hosts.simple')
    def test_host_url_tag_with_kwargs(self):
        rendered = self.render("{% load hosts %}"
            "{% host_url simple-direct on with_kwargs username='johndoe' %}")
        self.assertEqual(rendered, '//johndoe.eggs.spam/simple/')

    @override_settings(
        DEFAULT_HOST='www',
        PARENT_HOST='eggs.spam',
        ROOT_HOSTCONF='django_hosts.tests.hosts.simple')
    def test_host_url_tag_with_view_kwargs(self):
        rendered = self.render("{% load hosts %}"
            "{% host_url complex-direct template='test' on with_view_kwargs "
            "subdomain='test2000' %}")
        self.assertEqual(rendered, '//stest2000.eggs.spam/template/test/')

    @override_settings(
        DEFAULT_HOST='www',
        ROOT_HOSTCONF='django_hosts.tests.hosts.simple',
        PARENT_HOST='eggs.spam')
    def test_host_url_tag_parent_host(self):
        rendered = self.render(
            "{% load hosts %}{% host_url simple-direct on static %}")
        self.assertEqual(rendered, '//static.eggs.spam/simple/')

    @override_settings(
        DEFAULT_HOST='www',
        ROOT_HOSTCONF='django_hosts.tests.hosts.simple')
    def test_raises_template_syntaxerror(self):
        self.assertRaises(TemplateSyntaxError,
                          self.render, "{% load hosts %}{% host_url %}")
        self.assertRaises(TemplateSyntaxError,
                          self.render,
                          "{% load hosts %}{% host_url simple-direct on %}")
        self.assertRaises(TemplateSyntaxError,
                          self.render,
                          "{% load hosts %}{% host_url simple-direct as %}")
        self.assertRaises(TemplateSyntaxError, HostURLNode.parse_params,
                          Parser(['']), "username=='johndoe'")
