from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^simple/$', 'django.shortcuts.render', name='simple-direct'),
)
