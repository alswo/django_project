from django.conf.urls import patterns, url, include
from schedule import views

urlpatterns = patterns('',
    url(r'^putSchedule', views.putSchedule),
    url(r'^getSchedule', views.getSchedule),
    url(r'^todayLoad', views.todayLoad),
    url(r'^updateSchedule', views.updateSchedule),
    url(r'^updateArea', views.updateArea),
    url(r'^csmain', views.updateArea),
    url(r'^studentLoad', views.studentLoad),
    url(r'^getAcaPhone', views.getAcaPhone),
    url(r'^getCarPhone', views.getCarPhone),
    url(r'^getHistory', views.getHistory),
    url(r'^chart', views.chart),
    url(r'^analyze', views.analyze),
    url(r'^reqInventory', views.reqInventory)
)
