from django.conf.urls import patterns, url, include
from message import views

urlpatterns = patterns('',
    url(r'^sendMessage$', views.sendMessage),
)
