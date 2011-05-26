from django.conf.urls.defaults import patterns, include

import debug_toolbar.urls

from .urls import urlpatterns

debug_toolbar.urls.urlpatterns += patterns('',
    ('', include(urlpatterns)),
)
