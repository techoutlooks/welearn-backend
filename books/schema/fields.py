import graphene
from django.shortcuts import get_object_or_404
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required, superuser_required

from books.settings import get_setting
from books.models import Book, Loan
from tess_core.schema.fields import MediumType


class BookType(DjangoObjectType, MediumType):

    file_url = graphene.String()
    file_preview_url = graphene.String()
    cover_img_url = graphene.String()
    back_img_url = graphene.String()

    class Meta:
        model = Book
        exclude = ('file', 'file_preview', 'cover_img', 'back_img')

    @staticmethod
    def resolve_file_url(root, info, **kwargs):
        return root.file.canonical_url if root.file else None

    @staticmethod
    def resolve_file_preview_url(root, info, **kwargs):
        return root.file_preview.canonical_url if root.file_preview else None

    @staticmethod
    def resolve_cover_img_url(root, info, **kwargs):
        return root.get_img_url()

    @staticmethod
    def resolve_back_img_url(root, info, **kwargs):
        if root.back_img:
            return root.back_img.canonical_url if root.back_img else None


class LoanType(DjangoObjectType):

    duration = graphene.Int()
    started = graphene.DateTime()
    book = graphene.Field(BookType)

    class Meta:
        model = Loan

    @staticmethod
    def resolve_duration(root, info, **kwargs):
        return root.duration

    @staticmethod
    def resolve_started(root, info, **kwargs):
        return root.started


class CreateBookLoan(graphene.Mutation):

    loan = graphene.Field(LoanType)

    class Arguments:
        book_id = graphene.Int()
        duration = graphene.Int()

    @superuser_required
    def mutate(self, info, book_id: int, duration=get_setting('LEASE_DURATION')):
        loan = Loan.borrow_book(info.context.user, book_id, duration)
        return CreateBookLoan(loan)


class CancelBookLoan(graphene.Mutation):

    loan = graphene.Field(LoanType)

    class Arguments:
        loan_id = graphene.String()

    @login_required
    def mutate(self, info, loan_id: str):
        loan = get_object_or_404(Loan, user=info.context.user, id=loan_id)
        loan.cancel()
        return CancelBookLoan(loan=loan)

