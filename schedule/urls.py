from django.conf.urls import patterns, url, include
from schedule import views

urlpatterns = patterns('',
    url(r'^putSchedule', views.putSchedule),
    url(r'^getSchedule', views.getSchedule),
    url(r'^todayLoad', views.todayLoad),
)
