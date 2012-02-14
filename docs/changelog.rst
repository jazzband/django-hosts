Changelog
=========

0.4.2 (2012/02/14)
------------------

- Removed a unneeded installation time requirement for Django <= 1.4.

- Removed the use of versiontools due to unwanted installation time side
  effects.

- Refactored tests slightly.

0.4.1 (2011/12/23)
------------------

- Added :func:`~django_hosts.callbacks.cached_host_site` callback which
  stores the matching :class:`~django.contrib.sites.models.Site` instance
  in the default cache backend (also see new
  :attr:`~django.conf.settings.HOST_SITE_TIMEOUT` setting).

- Throw warning if django-debug-toolbar is used together with the
  ``django_hosts`` and the order of the ``MIDDLEWARE_CLASSES`` setting
  isn't correct.

- Added CI server at https://ci.enn.io/job/django-hosts/

0.4 (2011/11/04)
----------------

- Added ability to :ref:`save the result<asvar>` of
  :func:`~django_hosts.templatetags.hosts.host_url` template tag in a
  template context variable.

0.3 (2011/09/30)
----------------

- Consolidated reversal internals.

- Removed unfinished support for the Django Debug Toolbar.

- Added a custom callback which uses Django's sites_ app to retrieve
  a ``Site`` instance matching the current host, setting ``request.site``.

- Extended tests dramatically (100% coverage).

- Added docs at http://django-hosts.rtfd.org

- Stopped preventing the name 'default' for hosts.

.. _sites: https://docs.djangoproject.com/en/dev/ref/contrib/sites/

0.2.1 (2011/05/31)
------------------

- Fixed issue related to the ``PARENT_HOST`` setting when used with
  empty host patterns.

- Stopped automatically emulating hosts in debug mode.

0.2 (2011/05/31)
----------------

- **BACKWARDS INCOMPATIBLE** Renamed the package to ``django_hosts``

  Please change your import from::

    from hosts import patterns, hosts

  to::

    from django_hosts import patterns, hosts

- **BACKWARDS INCOMPATIBLE** Changed the data type that the
  ``django_hosts.patterns`` function returns to be a list instead of a
  SortedDict to follow conventions of Django's URL patterns.
  You can use that for easy extension of the patterns, e.g.::

    from django_hosts import patterns, host
    from mytemplateproject.hosts import host_patterns

    host_patterns += patterns('',
        host('www2', 'mysite.urls.www2', name='www2')
    )

- Extended tests to have full coverage.

- Fixed prefix handling.

0.1.1 (2011/05/30)
------------------

- Fixed docs issues.

- Use absolute imports where possible.

0.1 (2011/05/29)
----------------

- Initial release with middleware, reverse and templatetags.
