from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^multiple/$', 'django.shortcuts.render', name='multiple-direct'),
)
