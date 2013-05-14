from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('django.views.generic.simple',
    url(r'^simple/$', 'django.shortcuts.render', name='simple-direct'),
)
