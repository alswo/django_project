from django.conf.urls import patterns, url, include
from api import views

urlpatterns = patterns('',
    url(r'^getRealtimeLocation$', views.getRealtimeLocation),
    url(r'^getSchedulesForStudent$', views.getSchedulesForStudent),
)
