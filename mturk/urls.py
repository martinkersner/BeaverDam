from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.views.generic.base import RedirectView

from mturk import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'^(\d+)/$', views.status, name='status'),
    url(r'^(\d+)/create$', views.create_fvt, name='create_fvt'),
    url(r'^publish/$', views.publish_task, name='publish_task'),
]
