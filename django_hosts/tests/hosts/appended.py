from django_hosts import patterns, host
from django_hosts.tests.hosts.simple import host_patterns

host_patterns += patterns('',
    host(r'special', 'django_hosts.tests.urls.simple', name='special'),
)
