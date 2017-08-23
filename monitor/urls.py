from django.conf.urls import patterns, url, include
from monitor import views

urlpatterns = patterns('',
    url(r'^shuttles$', views.shuttles),
    url(r'^inventories$', views.inventories),
    url(r'^realtimeLocationHistory$', views.realtimeLocationHistory),
)
