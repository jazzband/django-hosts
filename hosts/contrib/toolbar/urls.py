from django.conf.urls.defaults import patterns, url

from debug_toolbar.urls import _PREFIX

urlpatterns = patterns('hosts.contrib.toolbar.views',
    url(r'^%s/host/redirect/$' % _PREFIX, 'redirect', name='hosts-debug-redirect'),
)
