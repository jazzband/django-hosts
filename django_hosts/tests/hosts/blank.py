from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'', 'django_hosts.tests.urls.simple', name='blank'),
    host(r'|www', 'django_hosts.tests.urls.simple', name='blank_or_www'),
)
