"""
Signals defined here perform two things, further enhancing Book management:

a) `*_subscription` handlers here triggers a subscription event when a book/loan changed.
    Using subscriptions with graphene-django thru channels and graphene-subscriptions.
    This is connecting signals for any models we want to create subscriptions for.
b) `create_file_preview_callback` creates previews from books

"""
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from graphene_subscriptions.events import ModelSubscriptionEvent

from books.models import Book, BOOK_EDITED, BOOK_REMOVED


# whether property x.y is in dict z
updated_value = lambda x, y, z: (getattr(x, y), True) if z and y in z else (None, False)


@receiver(post_save, sender=Book, dispatch_uid="book_post_save")
def book_edited_subscription(sender, instance, created, update_fields, **kwargs):
    """
    Send subscription event to websocket,
    as given book was just created, updated or made public.
    """
    published, updated = updated_value(instance, 'published', update_fields)
    op = BOOK_REMOVED if updated and not published else BOOK_EDITED
    event = ModelSubscriptionEvent(operation=op, instance=instance)
    event.send()


@receiver(post_delete, sender=Book, dispatch_uid="book_post_delete")
def book_removed_subscription(sender, instance, **kwargs):
    """
    Send subscription event to websocket,
    as given book has just been deleted.
    """
    event = ModelSubscriptionEvent(operation=BOOK_REMOVED, instance=instance)
    event.send()


@receiver(post_save, sender=Book, dispatch_uid='book_create_preview')
def create_book_preview_callback(sender, instance, created, update_fields, **kwargs):
    """
    Create `instance.file_preview` from `instance.file`,
    if the user edited the preview page ranges,
    """
    if instance.file:
        preview_pages, preview_pages_updated = updated_value(instance, 'preview_pages', update_fields)
        if created or not instance.file_preview or preview_pages_updated:
            print(f'*** (re)creating book preview from pages {preview_pages} of {instance.page_count}')
            instance.get_or_create_file_preview(preview_pages_updated)
