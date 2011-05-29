from __future__ import absolute_import

from hosts.defaults import patterns, host

host_patterns = patterns('',
    host(r'www\.example\.com', 'hosts.tests.urls.simple', name='www'),
    host(r'static', 'hosts.tests.urls.simple', name='static'),
    host(r'(\w+)', 'hosts.tests.urls.simple', name='with_args'),
    host(r'(?P<username>\w+)', 'hosts.tests.urls.simple', name='with_kwargs'),
)
