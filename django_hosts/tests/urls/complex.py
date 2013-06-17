from django.conf.urls import patterns, url

urlpatterns = patterns('django_hosts.tests.views',
    url(r'^template/(?P<template>\w+)/$', 'test_view', name='complex-direct'),
)
