from django.core.exceptions import ImproperlyConfigured
from django.utils.datastructures import SortedDict

def patterns(*args):
    subdomains = SortedDict()

    for x in args:
        name = x['name']

        if name in subdomains:
            raise ImproperlyConfigured("Duplicate subdomain name: %s" % name)
        if name == 'default':
            raise ImproperlyConfigured("Reserved subdomain name: %s" % name)

        subdomains[name] = x

    return subdomains

class subdomain(dict):
    def __init__(self, regex, urlconf, name, callback=None):
        self.update({
            'regex': regex,
            'urlconf': urlconf,
            'name': name,
        })

        if callback:
            self['callback'] = callback
