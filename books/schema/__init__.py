import graphene
from django.shortcuts import get_object_or_404
from graphql_jwt.decorators import login_required, superuser_required

from books.schema.fields import CreateBookLoan, CancelBookLoan, LoanType, BookType
from books.models import (
    Book, Loan,
    BOOK_BORROWED, LOAN_EXPIRED, LOAN_CANCELLED,
    BOOK_EDITED, BOOK_REMOVED
)

__all__ = [
    'Query', 'Mutation', 'Subscription',
    'CreateBookLoan', 'CancelBookLoan', 'LoanType', 'BookType'
]

from tess_core.schema import SearchQuery


class Query(SearchQuery):

    books = graphene.List(BookType)
    loans = graphene.List(LoanType)

    book = graphene.Field(BookType, book_id=graphene.Int())
    loan = graphene.Field(LoanType, loan_id=graphene.String())

    def resolve_books(self, info, **kwargs):
        qs = Book.objects.published()
        return Query.search(qs, **kwargs)

    def resolve_book(self, info, book_id, **kwargs):
        return get_object_or_404(Book, id=book_id)

    @login_required
    def resolve_loans(self, info, **kwargs):
        qs = Loan.objects.active().filter(user=info.context.user)
        return Query.search(qs, **kwargs)

    @login_required
    def resolve_loan(self, info, loan_id, **kwargs):
        return get_object_or_404(Loan, user=info.context.user, id=loan_id)


class Mutation:
    borrow_book = CreateBookLoan.Field()
    cancel_book_loan = CancelBookLoan.Field()


class Subscription:
    """
    Using graphene-subscriptions to stitch together the async-based pattern that Django Channels uses
     with the Observable-based pattern used in graphene.
    Each subscription field resolver must return an observable which emits values matching the field's type.
    https://github.com/jaydenwindle/graphene-subscriptions
    """
    book_borrowed = graphene.Field(LoanType)
    loan_revoked = graphene.Field(LoanType)
    book_edited = graphene.Field(BookType)
    book_removed = graphene.Field(BookType)

    # FIXME: seems instance 'undefined' still pushed to client

    def resolve_book_borrowed(root, info):
        print('---- custom subscription: book_borrowed SUBSCRIBED  ----')

        return root \
            .filter(
                lambda ev:
                    ev.operation == BOOK_BORROWED and
                    isinstance(ev.instance, Loan)
        ) \
            .tap(lambda ev: print('---- custom subscription: book_borrowed EVENT :', ev.operation, ev.instance)) \
            .map(lambda event: event.instance)

    def resolve_loan_revoked(root, info):
        print('---- custom subscription: loan_revoked SUBSCRIBED  ----')

        return root \
            .filter(
                lambda ev:
                   ev.operation == LOAN_EXPIRED or
                   ev.operation == LOAN_CANCELLED and
                   isinstance(ev.instance, Loan)
        ) \
            .tap(lambda ev: print('---- custom subscription: loan_revoked EVENT :', ev.operation, ev.instance)) \
            .map(lambda event: event.instance)

    def resolve_book_edited(root, info):
        print('---- model subscription: book_edited SUBSCRIBED  ----')

        return root.filter(
            lambda ev: ev.operation == BOOK_EDITED and isinstance(ev.instance, Book)) \
            .tap(lambda ev: print('---- custom subscription: book_edited EVENT :', ev.operation, ev.instance)) \
            .map(lambda ev: ev.instance)

    def resolve_book_removed(root, info):
        print('---- model subscription: book_removed SUBSCRIBED  ----')

        return root.filter(
            lambda ev: ev.operation == BOOK_REMOVED and isinstance(ev.instance, Book)) \
            .tap(lambda ev: print('---- custom subscription: book_removed EVENT :', ev.operation, ev.instance)) \
            .map(lambda ev: ev.instance)
