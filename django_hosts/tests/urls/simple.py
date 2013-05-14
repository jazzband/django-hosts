from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('django.views.generic.simple',
    url(r'^simple/$', TemplateView.as_view(), name='simple-direct'),
)
