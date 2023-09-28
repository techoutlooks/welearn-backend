import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.functions import Now
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db import models
from filer.fields.image import FilerImageField, FilerFileField
from graphene_subscriptions.events import SubscriptionEvent
from tess_core.helpers import get_or_create_filer_obj
from tess_core.models import ModelSubscriptionMixin

from books.settings import get_setting
from books.pdf import make_pdf_preview, make_preview_filename

# Custom GraphQL event subscriptions (graphene-subscriptions)
# match loan management status: (resp.) ONGOING, EXPIRED, CANCELLED,
# and Book management:  `book_edited` aka. created, updated or published,
#                       `book_deleted_or_unpublished`
from tess_core import models as tess_core_models

BOOK_BORROWED = 'loan_created_or_renewed'
LOAN_EXPIRED = 'loan_expired'
LOAN_CANCELLED = 'loan_cancelled'
BOOK_EDITED = 'book_created_updated_or_published'
BOOK_REMOVED = 'book_deleted_or_unpublished'


def get_default_cover_img():
    file, created = get_or_create_filer_obj(
        'Image', get_setting('COVER_PLACEHOLDER_IMG'), get_setting('COVERS_FOLDER')
    )
    return file.pk


class BookQuerySet(models.QuerySet):
    def published(self):
        return self.filter(published__isnull=False)


class Book(ModelSubscriptionMixin, tess_core_models.BaseMedium):

    # META ===================
    title = models.CharField(max_length=255)
    abstract = models.TextField()
    isbn = models.CharField(max_length=255)
    page_count = models.IntegerField()
    publication_date = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(now().year)],
        help_text="Use the following format: <YYYY>"
    )

    # FILES ==================
    # required fields have blank=False (same as not defined) for admin,
    # and null=True that enables fixtures to load without a fk file.
    file = FilerFileField(
        null=True, related_name="book_files", on_delete=models.CASCADE,
        help_text="File for borrowing. Requires valid subscription.")
    preview_pages = models.CharField(
        max_length=100, default='1-10',
        help_text="Preview's pages range within `file`. eg: 1, 3-10"
    )
    file_preview = FilerFileField(
        null=True, blank=True, related_name="book_preview_files", on_delete=models.SET_NULL,
        help_text='File for public preview. Generated automatically from `preview_pages`.')
    cover_img = FilerImageField(
        null=True, related_name="book_covers", on_delete=models.SET(get_default_cover_img),
        help_text='Front cover image.')
    back_img = FilerImageField(
        null=True, blank=True, related_name="book_backs", on_delete=models.SET_NULL,
        help_text='Back cover image.')

    objects = BookQuerySet.as_manager()

    def __str__(self):
        return 'ISDN #{} ({} pages) {}'.format(self.isbn, self.page_count, self.title)

    def get_title(self):
        return self.title

    def get_synopsis(self):
        return self.abstract[:get_setting('SYNOPSIS_LEN')]

    def get_img_url(self):
        return self.cover_img.canonical_url

    @property
    def kind_plural(self):
        return 'Books'

    @property
    def file_name_pretty(self):
        """ Pretty name to save file as """
        ext = self.file.rsplit('.')[-1]
        return "{0}.{1}".format(slugify(self.title), ext)

    @property
    def topics_pretty(self):
        """Creates a string for the topic. This is required to display topics in Admin."""
        return ', '.join([str(g) for g in self.topics.all()[:3]])

    @property
    def authors_pretty(self):
        return ', '.join([str(a) for a in self.authors.all()[:3]])

    def get_or_create_file_preview(self, force_create=False):
        """
        Create publicly accessible preview of `preview_pages` extracted
        from the file associated with this book, inside pre-configured folder.
        https://gist.github.com/stefanfoulis/715194
        """
        if not self.file_preview or force_create:
            filename = make_preview_filename(self.file.label)
            pdf, pages = make_pdf_preview(self.file.path, filename, self.preview_pages)
            if pdf:
                self.file_preview, created = get_or_create_filer_obj('File', pdf, get_setting('PREVIEW_FOLDER'))
                self.save()

        return self.file_preview


class LoanQuerySet(models.QuerySet):

    def active(self):
        active_query = models.Q(archived__isnull=True, ended__isnull=True)
        return self.filter(active_query, status=Loan.ONGOING)

    def ended(self):
        ended_query = models.Q(status=Loan.EXPIRED) | models.Q(status=Loan.CANCELLED)
        return self.exclude(ended_query).distinct()


class LoanManager(models.Manager):
    pass


class Loan(models.Model):
    """
    A Book loan by a given user.
    There must be only one active loan per unique book and user.
    Extending the loan period works by adding a new Lease to it,
     several leases of a the same book sharing the same loan id.
    """

    ONGOING = 'ongoing'
    EXPIRED = 'expired'
    CANCELLED = 'cancelled'
    LOAN_STATUS_CHOICES = [
        (ONGOING, 'Ongoing - Active user subscription'),
        (EXPIRED, 'Expired - Revoked after timed out'),
        (CANCELLED, 'Cancelled - Revoked prior termination')
    ]

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE, related_name='loans')
    ended = models.DateTimeField(null=True, blank=True, help_text=_("Time ended, with `cancelled`|`expired` status."))
    archived = models.DateTimeField(null=True, blank=True, help_text=_("No more avails to the user, since?"))
    status = models.CharField(max_length=10, choices=LOAN_STATUS_CHOICES, default=ONGOING)

    objects = LoanManager.from_queryset(LoanQuerySet)()

    @classmethod
    def borrow_book(cls, user, book_id: int, duration: int):
        """
        Borrowing a book covering two use cases:
         - first time loan or,
         - extending an existing loan's duration (ie. adding new leases to it).
        If no active loan exist for this book yet, create a new loan and first lease,
        otherwise extend the loan with a new lease.
        """
        book = get_object_or_404(Book, pk=book_id)
        loan = cls.objects.active().filter(user=user, book=book).first()
        if not loan:
            loan = cls.objects.create(user=user, book=book)
        Lease.objects.create(loan, duration)
        loan.create_subscription(operation=BOOK_BORROWED)
        return loan

    @property
    def started(self):
        """
        Lease start time.
        """
        return self.leases.by_loan(self).earliest('started').started

    @property
    def duration(self):
        """
        Total number of days this loan is initially valid for.
        This is the initial value of the loan expiry counting down.
        """
        return self.leases.duration(self)

    def expire_ended(self):
        """
        Expire all timed out leases on this loan,
        Also mark loan as expired if it has no more lease active.
        Eventually fires LOAN_EXPIRED signal (caught by graphene-subscriptions)
        """
        active = self.leases.active().count()
        expired = self.leases.expire(self, expired_only=True)
        if expired == active:
            self.status = Loan.EXPIRED
            self.ended = now()
            self.save()
            self.create_subscription(operation=LOAN_EXPIRED)

        lease_counts = dict(expired=expired, active=active)
        return lease_counts

    def cancel(self):
        """
        Cancel this loan, alongside associated active leases.
        """
        self.leases.cancel(self)
        self.status = Loan.CANCELLED
        self.save()
        self.create_subscription(operation=LOAN_CANCELLED)

    def create_subscription(self, operation):
        """
        Publish event (graphene-subscriptions)
        :param operation: LOAN_CREATED|LOAN_EXPIRED|LOAN_CANCELLED
        :return: None
        """
        event = SubscriptionEvent(operation=operation, instance=self)
        event.send()


class LeaseQuerySet(models.QuerySet):

    def active(self):
        return self.filter(status=Lease.ONGOING)

    def expired(self):
        return self.filter(status=Lease.EXPIRED)

    def cancelled(self):
        return self.filter(status=Lease.CANCELLED)


class LeaseManager(models.Manager):
    """
    Manage lease operation for an entire loan scope.
    """

    def by_loan(self, loan):
        return self.active().filter(loan=loan)

    def cancel(self, loan):
        return self._revoke(Lease.CANCELLED)

    def expire(self, loan, expired_only=True):
        """
        Expire ended leases for any given loan.
        ie. where (lease.started < now() - lease.duration) == True
        :param loan:
        :param expired_only: should revoke only ended leases (default)? or all of them?.
        :return: number of leases that have actually been expired
        """
        to_revoke = self.active().filter(loan=loan)

        if expired_only:
            db_expr = models.ExpressionWrapper(Now() - models.F('started'), output_field=models.DurationField())
            to_revoke = to_revoke.annotate(elapsed=db_expr) \
                .filter(elapsed__gt=models.F('duration'))

        return self._revoke(Lease.EXPIRED, to_revoke)

    def duration(self, loan):
        """
        Sum total of initial durations (days) of all associated leases.
        """
        return self.by_loan(loan) \
                   .aggregate(duration=models.Sum('duration')) \
                   .get('duration') or 0

    def create(self, loan, duration):
        """
        Manager method override
        Create a new loan with appropriate status.
        """
        return super().create(loan=loan, duration=duration, status=Lease.ONGOING)

    def _revoke(self, reason, queryset=None):
        """
        Revoke all leases in given queryset,
        ie. update their status (reason for revoking: expired|cancelled).
        """
        if not queryset:
            return
        return queryset.update(status=reason)


class Lease(models.Model):
    """
    Represents a single book lease/purchase by user for a given book
    Possible lease status: 'Active' (ongoing), 'Expired' (timed out), 'Cancelled' (related loan was cancelled)
    """

    ONGOING = 'ongoing'
    EXPIRED = 'expired'
    CANCELLED = 'cancelled'
    LEASE_STATUS_CHOICES = [
        (ONGOING, 'Ongoing - active user subscription'),
        (EXPIRED, 'Expired - Revoked after timed out'),
        (CANCELLED, 'Cancelled - Revoked prior termination')
    ]

    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='leases')
    started = models.DateTimeField(auto_now_add=True, blank=True)
    duration = models.PositiveIntegerField(help_text=_("Initial lease duration (days)"))
    status = models.CharField(
        max_length=32,
        choices=LEASE_STATUS_CHOICES,
        default=ONGOING
    )

    objects = LeaseManager.from_queryset(LeaseQuerySet)()


class Store(models.Model):
    """
    Book Store
    """
    name = models.CharField(max_length=300)
    books = models.ManyToManyField('books.Book')

    def __str__(self):
        return '{} ({} books)'.format(self.name, self.books.count())
