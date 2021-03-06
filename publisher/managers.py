from django.db import models

from .signals import publisher_pre_delete
from .middleware import get_draft_status


class PublisherQuerySet(models.QuerySet):
    def drafts(self):
        from .models import PublisherModelBase
        return self.filter(publisher_is_draft=PublisherModelBase.STATE_DRAFT)

    def published(self):
        """
        Note: will ignore start/end date!
        Use self.visible() to get all publicly accessible entries.
        """
        from .models import PublisherModelBase
        return self.filter(
            publisher_is_draft=PublisherModelBase.STATE_PUBLISHED,
        )

    def visible(self):
        """
        Filter all publicly accessible entries.
        """
        from .models import PublisherModelBase
        return self.filter(
            publisher_is_draft=PublisherModelBase.STATE_PUBLISHED)


class BasePublisherManager(models.Manager):
    def get_queryset(self):
        return PublisherQuerySet(self.model, using=self._db)

    def contribute_to_class(self, model, name):
        # Stopped working in current versions of Django,
        # connect manually for all models you need
        # https://code.djangoproject.com/ticket/27350
        super(BasePublisherManager, self).contribute_to_class(model, name)
        models.signals.pre_delete.connect(publisher_pre_delete, model)

    def current(self):
        if get_draft_status():
            return self.drafts()
        return self.published()


PublisherManager = BasePublisherManager.from_queryset(PublisherQuerySet)

try:
    from parler.managers import TranslatableManager, TranslatableQuerySet
except ImportError:
    pass
else:
    class PublisherParlerQuerySet(PublisherQuerySet, TranslatableQuerySet):
        pass

    class BasePublisherParlerManager(PublisherManager, TranslatableManager):
        def get_queryset(self):
            return PublisherParlerQuerySet(self.model, using=self._db)

    PublisherParlerManager = BasePublisherParlerManager.from_queryset(PublisherParlerQuerySet)
