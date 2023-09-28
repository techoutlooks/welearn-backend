from django.contrib import admin

from books.admin.actions import make_published, make_unpublished
from books.models import Book, Loan, Store


class LoanInline(admin.TabularInline):
    model = Loan
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False


class BookAdmin(admin.ModelAdmin):
    inlines = [LoanInline]
    list_display = (
        '_is_published', '_preview_created',
        'isbn', 'publication_date', 'feature', 'title', '_authors_pretty', '_topics_pretty')
    list_editable = ('feature',)
    actions = [make_published, make_unpublished]

    def _authors_pretty(self, obj):
        return obj.authors_pretty
    _authors_pretty.short_description = 'Author(s)'

    def _topics_pretty(self, obj):
        return obj.topics_pretty
    _topics_pretty.short_description = 'Topics(s)'

    def _is_published(self, obj):
        return bool(obj.published)
    _is_published.boolean = True
    _is_published.short_description = 'Published'

    def _preview_created(self, obj):
        return bool(obj.file_preview)
    _preview_created.boolean = True
    _preview_created.short_description = 'Preview ∃!'


admin.site.register(Book, BookAdmin)
admin.site.register(Store)

