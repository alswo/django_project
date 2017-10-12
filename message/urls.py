from django.conf.urls import patterns, url, include
from message import views

urlpatterns = [
    url(r'^sendMessage$', views.sendMessage),
    url(r'^biztalkreport$', views.getReport),
]
