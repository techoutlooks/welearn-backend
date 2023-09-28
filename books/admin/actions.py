# Admin actions
# https://docs.djangoproject.com/en/3.0/ref/contrib/admin/actions/
from django.utils.timezone import now


def make_published(modeladmin, request, queryset):
    return queryset.filter(published=None).update(published=now())


def make_unpublished(modeladmin, request, queryset):
    return queryset.update(published=None)


make_published.short_description = 'Publish selected books'
make_unpublished.short_description = 'Un-publish selected books'
