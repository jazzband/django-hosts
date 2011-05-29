from __future__ import absolute_import, with_statement

from django.core.exceptions import MiddlewareNotUsed, ImproperlyConfigured
from django.template import Template, Context, TemplateSyntaxError

from django.utils.html import escape

from hosts.reverse import clear_host_caches, get_hostconf_module, get_host_patterns
from hosts.tests.base import override_settings, HostsTestCase


class TemplateTagsTest(HostsTestCase):

    def render(self, template, context=None):
        if context is None:
            context = Context({})
        return Template(template).render(context).strip()

    @override_settings(
        DEFAULT_HOST='www',
        ROOT_HOSTCONF='hosts.tests.hosts.simple')
    def test_host_url_tag_simple(self):
        rendered = self.render(
            "{% load hosts %}{% host_url simple-direct on www %}")
        self.assertEqual(rendered, '//www.example.com/simple/')

    @override_settings(
        DEFAULT_HOST='www',
        ROOT_HOSTCONF='hosts.tests.hosts.simple')
    def test_host_url_tag_with_args(self):
        rendered = self.render(
            "{% load hosts %}{% host_url simple-direct on with_args 'www.eggs.spam' %}")
        self.assertEqual(rendered, '//www.eggs.spam/simple/')

    @override_settings(
        DEFAULT_HOST='www',
        PARENT_HOST='eggs.spam',
        ROOT_HOSTCONF='hosts.tests.hosts.simple')
    def test_host_url_tag_with_kwargs(self):
        rendered = self.render(
            "{% load hosts %}{% host_url simple-direct on with_kwargs username='johndoe' %}")
        self.assertEqual(rendered, '//johndoe.eggs.spam/simple/')

    @override_settings(
        DEFAULT_HOST='www',
        ROOT_HOSTCONF='hosts.tests.hosts.simple',
        PARENT_HOST='eggs.spam')
    def test_host_url_tag_parent_host(self):
        rendered = self.render(
            "{% load hosts %}{% host_url simple-direct on static %}")
        self.assertEqual(rendered, '//static.eggs.spam/simple/')

    @override_settings(
        DEFAULT_HOST='www',
        ROOT_HOSTCONF='hosts.tests.hosts.simple')
    def test_raises_template_syntaxerror(self):
        self.assertRaises(TemplateSyntaxError, self.render, "{% load hosts %}{% host_url %}")
        self.assertRaises(TemplateSyntaxError, self.render, "{% load hosts %}{% host_url simple-direct on %}")
