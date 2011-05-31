from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'', 'django_hosts.tests.urls.simple', name='blank'),
)
