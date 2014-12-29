"""
A monkey patching module to make sure the cache keys in Django < 1.7 also take
the host into account. This makes the full page cache middleware work.

Backported from Django stable/1.7.x (http://git.io/8Ieptg)
"""
import hashlib
from django.utils import cache
from django.utils.encoding import iri_to_uri, force_bytes


def _generate_cache_key(request, method, headerlist, key_prefix):  # pragma: no cover
    """Returns a cache key from the headers given in the header list."""
    ctx = hashlib.md5()
    for header in headerlist:
        value = request.META.get(header, None)
        if value is not None:
            ctx.update(force_bytes(value))
    url = hashlib.md5(force_bytes(iri_to_uri(request.build_absolute_uri())))
    cache_key = 'views.decorators.cache.cache_page.%s.%s.%s.%s' % (
        key_prefix, method, url.hexdigest(), ctx.hexdigest())
    return cache._i18n_cache_key_suffix(request, cache_key)


def _generate_cache_header_key(key_prefix, request):  # pragma: no cover
    """Returns a cache key for the header cache."""
    url = hashlib.md5(force_bytes(iri_to_uri(request.build_absolute_uri())))
    cache_key = 'views.decorators.cache.cache_header.%s.%s' % (
        key_prefix, url.hexdigest())
    return cache._i18n_cache_key_suffix(request, cache_key)


def patch_cache_key_funcs():  # pragma: no cover
    cache._generate_cache_key = _generate_cache_key
    cache._generate_cache_header_key = _generate_cache_header_key
