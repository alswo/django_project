from django.conf.urls import patterns, url, include
from optimizer import views

urlpatterns = patterns('',
    url(r'^getRoute', views.getRoute),
)
