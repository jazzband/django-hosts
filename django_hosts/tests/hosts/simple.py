from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'www\.example\.com', 'django_hosts.tests.urls.simple', name='www'),
    host(r'static', 'django_hosts.tests.urls.simple', name='static'),
    host(r'^s(?P<subdomain>\w+)', 'django_hosts.tests.urls.complex',
         name='with_view_kwargs'),
    host(r'wiki\.(?P<domain>\w+)', 'django_hosts.tests.urls.simple',
         callback='django_hosts.callbacks.host_site', name='with_callback'),
    host(r'admin\.(?P<domain>\w+)', 'django_hosts.tests.urls.simple',
         callback='django_hosts.callbacks.cached_host_site',
         name='with_cached_callback'),
    host(r'(?P<username>\w+)', 'django_hosts.tests.urls.simple',
         name='with_kwargs'),
    host(r'(\w+)', 'django_hosts.tests.urls.simple', name='with_args'),
)
