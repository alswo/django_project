from django.conf.urls import patterns, url, include
from schedule import views

urlpatterns = patterns('',
    url(r'^putSchedule', views.putSchedule),
    url(r'^getSchedule', views.getSchedule),
    url(r'^todayLoad', views.todayLoad),
    url(r'^updateSchedule', views.updateSchedule),
    url(r'^updateArea', views.updateArea),
    url(r'^csmain', views.csmain),
    url(r'^studentLoad', views.studentLoad),
    url(r'^getAcaPhone', views.getAcaPhone),
)
