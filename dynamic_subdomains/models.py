import debug_toolbar.urls

from django.conf.urls.defaults import patterns, include

from .urls import urlpatterns

debug_toolbar.urls.urlpatterns += patterns('',
    ('', include(urlpatterns)),
)
