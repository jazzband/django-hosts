from django.conf.urls.defaults import patterns, url

from debug_toolbar.urls import _PREFIX

urlpatterns = patterns('dynamic_subdomains.views',
    url(r'^%s/subdomain/redirect/$' % _PREFIX, 'redirect',
        name='debug-subdomain-redirect'),
)
