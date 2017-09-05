from django.conf.urls import url, include
from optimizer import views

urlpatterns = [
    url(r'^getRoute$', views.getRoute),
    url(r'^getRouteSequential$', views.getRouteSequential),
]
