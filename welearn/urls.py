"""welearn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView


urlpatterns = [

    # django-filer's canonical URLs for public files
    path('filer/', include('filer.urls')),

    path('admin/', admin.site.urls),
    path("graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True))),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#adminsite-objects
admin.site.site_header = "weLearn v0.1 [TESS v0.1]"
admin.site.site_title = "weLearn"
admin.site.index_title = "Index"

