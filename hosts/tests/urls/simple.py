from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('django.views.generic.simple',
    url(r'^simple/$', 'direct_to_template', name='simple-direct'),
)
