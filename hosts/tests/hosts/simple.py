from __future__ import absolute_import

from hosts.defaults import patterns, host

host_patterns = patterns('',
    host('www', 'whatever', name='www'),
)
