django-hosts
============

.. image:: https://img.shields.io/pypi/v/django-hosts.svg
   :target: https://pypi.org/project/django-hosts/

.. image:: https://img.shields.io/pypi/pyversions/django-hosts.svg
   :target: https://pypi.org/project/django-hosts/

.. image:: https://img.shields.io/pypi/djversions/django-hosts.svg
   :target: https://pypi.org/project/django-hosts/

.. image:: https://github.com/jazzband/django-hosts/workflows/Test/badge.svg
   :target: https://github.com/jazzband/django-hosts/actions

.. image:: https://codecov.io/gh/jazzband/django-hosts/branch/master/graph/badge.svg
   :target: https://app.codecov.io/gh/jazzband/django-hosts

.. image:: https://readthedocs.org/projects/django-hosts/badge/?version=latest&style=flat
   :target: https://django-hosts.readthedocs.io/en/latest/

.. image:: https://jazzband.co/static/img/badge.svg
   :target: https://jazzband.co/

This Django app routes requests for specific hosts to different URL schemes
defined in modules called "hostconfs".

For example, if you own ``example.com`` but want to serve specific content
at ``api.example.com`` and ``beta.example.com``, add the following to a
``hosts.py`` file:

.. code-block:: python

    from django_hosts import patterns, host

    host_patterns = patterns('path.to',
        host(r'api', 'api.urls', name='api'),
        host(r'beta', 'beta.urls', name='beta'),
    )

This causes requests to ``{api,beta}.example.com`` to be routed to their
corresponding host URL conf file. Host URL conf file should define all routes which going to be hendled on a certain subdomain and has a same format like your plain ``urls.py`` (you can use it as a tamplate for your host URL confs). For example, requests to ``api.example.com`` will be mapped to views acording to `/path/to/api/urls.py` file



Patterns are evaluated in order. If no pattern matches, the request is
processed in the usual way, ie. using the standard ``ROOT_URLCONF``.

The patterns on the left-hand side are regular expressions. For example,
the following ``ROOT_HOSTCONF`` setting will route ``foo.example.com``
and ``bar.example.com`` to the same URLconf.

.. code-block:: python

    from django_hosts import patterns, host

    host_patterns = patterns('',
        host(r'(foo|bar)', 'path.to.urls', name='foo-or-bar'),
    )

.. note:

  Remember:

  * Patterns are matched against the extreme left of the requested host

  * It is implied that all patterns end either with a literal full stop
    (ie. ".") or an end of line metacharacter.

  * As with all regular expressions, various metacharacters need quoting.

Installation
------------

First, install the app with your favorite package manager, e.g.:

.. code-block:: shell

    pip install django-hosts

Alternatively, use the `repository on Github`_.

You can find the full docs here: `django-hosts.rtfd.org`_

Then configure your Django site to use the app:

#. Add ``'django_hosts'`` to your ``INSTALLED_APPS`` setting.

#. Add ``'django_hosts.middleware.HostsRequestMiddleware'`` to the
   **beginning** of your ``MIDDLEWARE`` setting.

#. Add ``'django_hosts.middleware.HostsResponseMiddleware'`` to the **end** of
   your ``MIDDLEWARE`` setting.

#. Create a new module containing your default host patterns,
   e.g. in the ``hosts.py`` file next to your ``urls.py``.

#. Set the ``ROOT_HOSTCONF`` setting to the dotted Python
   import path of the module containing your host patterns, e.g.:

   .. code-block:: python

       ROOT_HOSTCONF = 'mysite.hosts'

#. Set the ``DEFAULT_HOST`` setting to the **name** of the host pattern you
   want to refer to as the default pattern. It'll be used if no other
   pattern matches or you don't give a name to the ``host_url`` template
   tag.

.. _`repository on Github`: https://github.com/jazzband/django-hosts
.. _`django-hosts.rtfd.org`: https://django-hosts.readthedocs.io/
