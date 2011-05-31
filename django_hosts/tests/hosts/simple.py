from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'www\.example\.com', 'django_hosts.tests.urls.simple', name='www'),
    host(r'static', 'django_hosts.tests.urls.simple', name='static'),
    host(r'(\w+)', 'django_hosts.tests.urls.simple', name='with_args'),
    host(r'(?P<username>\w+)', 'django_hosts.tests.urls.simple', name='with_kwargs'),
)
