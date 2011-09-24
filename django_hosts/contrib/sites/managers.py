from django.conf import settings
from django.db import models
from django.db.models.fields import FieldDoesNotExist


class HostSiteManager(models.Manager):
    """
    Use this to limit objects to those associated with a site.

    Usage::

        on_site = HostSiteManager()
        on_site = HostSiteManager("package__site")
        on_site = HostSiteManager("release__package__site")
        on_site = HostSiteManager("release__package__site", select_related=False)

    """
    def __init__(self, field_name=None, select_related=True):
        super(HostSiteManager, self).__init__()
        self.__field_name = field_name
        self.__select_related = select_related
        self.__is_validated = False

    def _validate_field_name(self):
        field_names = self.model._meta.get_all_field_names()

        # If a custom name is provided, make sure the field exists on the model
        if self.__field_name is not None:
            field_name = self.__field_name.split("__", 1)[0]
            if field_name not in field_names:
                raise ValueError("%s couldn't find a field named %s in %s." %
                                 (self.__class__.__name__, field_name,
                                  self.model._meta.object_name))

        # Otherwise, see if there is a field called either 'site' or 'sites'
        else:
            for potential_name in ['site', 'sites']:
                if potential_name in field_names:
                    self.__field_name = field_name = potential_name
                    self.__is_validated = True
                    break

        # Now do a type check on the field (FK or M2M only)
        try:
            field = self.model._meta.get_field(field_name)
            if not isinstance(field, (models.ForeignKey,
                                      models.ManyToManyField)):
                raise TypeError("%s must be a ForeignKey or "
                                "ManyToManyField." % field_name)
        except FieldDoesNotExist:
            raise ValueError("%s couldn't find a field named %s in %s." %
                             (self.__class__.__name__, field_name,
                              self.model._meta.object_name))
        self.__is_validated = True

    def get_query_set(self, site_id=None):
        if site_id is None:
            site_id = settings.SITE_ID
        if not self.__is_validated:
            self._validate_field_name()
        qs = super(HostSiteManager, self).get_query_set()
        if self.__select_related:
            qs = qs.select_related(depth=1)
        return qs.filter(**{self.__field_name + '__id__exact': site_id})
    by_id = get_query_set

    def by_request(self, request):
        if not hasattr(request, "site") or request.site is None:
            return self.none()
        return self.by_id(request.site.id)
