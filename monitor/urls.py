from django.conf.urls import url, include
from monitor import views

urlpatterns = [
    url(r'^shuttles$', views.shuttles),
    url(r'^inventories$', views.inventories),
    url(r'^realtimeLocationHistory$', views.realtimeLocationHistory),
]
