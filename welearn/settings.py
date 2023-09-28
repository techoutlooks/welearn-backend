from .settings_default import *


# Core settings

AUTH_USER_MODEL = 'tess_auth.User'
INSTALLED_APPS += [

    'corsheaders',

    # django-filer & deps
    'easy_thumbnails',
    'filer',
    'mptt',
    'polymorphic',

    # django-cities-light & deps
    'cities_light',

    # tess_pay & deps
    'djmoney',
    'djmoney.contrib.exchange',
    'jsonfield',
    'tess_pay',

    # tess_core & deps
    'tess_auth',
    'tess_core',

    # graphql over ws using channels
    # 'channels' also installs a ws-capable drop in replacement for runserver
    'channels',
    'graphene_django',
    'graphene_subscriptions',

    # welearn apps
    'books',
]



# Secure settings

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
] + MIDDLEWARE
CORS_ORIGIN_WHITELIST = [
    "http://localhost:3000",
    "http://localhost:8100",
    "http://192.168.43.1:8100",
]
ALLOWED_HOSTS = [
    "localhost",
    "192.168.43.230",
    "192.168.43.1",
]


# File Management using django-filer
# MEDIA_URL = Base url to serve media files
# MEDIA_ROOT = Path where media is stored

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
STATIC_ROOT = os.path.join(BASE_DIR, "static")


# Configure Graphene for Django
# with JWT authentication from `tess-auth`

AUTHENTICATION_BACKENDS = [
    'graphql_jwt.backends.JSONWebTokenBackend',
    'django.contrib.auth.backends.ModelBackend',
]

GRAPHENE = {
    'SCHEMA': 'welearn.schema.schema',
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
    ],
}

# Configure Graphene support for graphql-ws on django-channels
# https://github.com/graphql-python/graphql-ws
# pip install channels graphene-subscriptions
# pip install -U channels_redis
ASGI_APPLICATION = 'welearn.routing.application'
CHANNELS_WS_PROTOCOLS = ["graphql-ws", ]
CHANNEL_LAYERS = {
    # "default": {
    #     "BACKEND": "channels_redis.tess_core.RedisChannelLayer",
    #     "CONFIG": {
    #         "hosts": [("127.0.0.1", 6379)],
    #     },
    # },
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    },
}

# TESS CORE
# =========

TESS_CORE = {
    'MEDIUM_MODELS': ['books.Book']
}
