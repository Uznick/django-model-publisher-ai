import six
from django.http import Http404
from django.views.generic import ListView
from django.views.generic.detail import DetailView


class PublisherViewMixin(object):

    class Meta:
        abstract = True

    def __has_perms(self):
        if not self.request.user:
            return False
        if not self.request.user.is_authenticated():
            return False
        if not self.request.user.is_active:
            return False

        if self.request.user.is_superuser:
            return True

        if hasattr(self, 'perm') and self.perm:
            if self.request.user.has_perm(self.perm):
                return True

        return False

    def get_queryset(self):
        if self.__has_perms():
            qs = self.model.objects.current()
        else:
            qs = self.model.objects.visible()

        if hasattr(self, 'get_ordering'):
            ordering = self.get_ordering()
            if ordering:
                if isinstance(ordering, six.string_types):
                    ordering = (ordering,)
                qs = qs.order_by(*ordering)

        return qs


class PublisherDetailView(PublisherViewMixin, DetailView):
    pass


class PublisherByOriginalPKDetailView(PublisherViewMixin, DetailView):
    def _has_perms(self):
        return True

    def get_object(self, queryset=None):
        _obj = self.model.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))

        if 'edit' in self.request.GET and self._has_perms():
            if _obj.publisher_draft:
                self.kwargs[self.pk_url_kwarg] = _obj.publisher_draft.pk
            else:
                self.kwargs[self.pk_url_kwarg] = _obj.pk
        else:
            if not _obj.publisher_linked:
                raise Http404
            self.kwargs[self.pk_url_kwarg] = _obj.publisher_linked.pk

        obj = super().get_object(queryset)

        return obj


class PublisherListView(PublisherViewMixin, ListView):
    pass
