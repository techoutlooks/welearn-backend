from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.conf.urls import url
from django.urls import path

from graphene_subscriptions.consumers import GraphqlSubscriptionConsumer


application = ProtocolTypeRouter({

    "websocket": AuthMiddlewareStack(
        URLRouter([
            # identical to path expected by graphene in urls.py
            path('graphql/', GraphqlSubscriptionConsumer)
        ])
    ),
})


