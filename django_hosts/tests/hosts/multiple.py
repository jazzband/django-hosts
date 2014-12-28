from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'spam\.eggs', 'django_hosts.tests.urls.multiple', name='multiple'),
)
