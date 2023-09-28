import graphene
import graphql_jwt

import books.schema
import tess_auth.schema
import tess_core.schema


class Query(
    books.schema.Query,
    tess_auth.schema.Query, tess_core.schema.Query,
    graphene.ObjectType
):
    pass


class Mutation(
    books.schema.Mutation,
    tess_auth.schema.Mutation,
    tess_core.schema.Mutation,
    graphene.ObjectType
):
    token_auth = tess_auth.schema.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


class Subscription(
    books.schema.Subscription,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
