import six
from django.views.generic import ListView
from django.views.generic.detail import DetailView


class PublisherViewMixin(object):

    class Meta:
        abstract = True

    def get_queryset(self):
        qs = self.model.objects.visible()

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, six.string_types):
                ordering = (ordering,)
            qs = qs.order_by(*ordering)

        return qs


class PublisherDetailView(PublisherViewMixin, DetailView):
    pass


class PublisherListView(PublisherViewMixin, ListView):
    pass
