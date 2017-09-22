from django.conf.urls import url, include
from schedule import views

urlpatterns = [
    url(r'^putSchedule', views.putSchedule),
    url(r'^getSchedule', views.getSchedule),
    url(r'^todayLoad', views.todayLoad),
    url(r'^updateSchedule', views.updateSchedule),
    url(r'^acaUpdateSchedule', views.acaUpdateSchedule),
    url(r'^updateArea', views.updateArea),
    url(r'^csmain', views.updateArea),
    url(r'^studentLoad', views.studentLoad),
    url(r'^getAcaPhone', views.getAcaPhone),
    url(r'^getCarPhone', views.getCarPhone),
    url(r'^getHistory', views.getHistory),
    url(r'^chart', views.chart),
    url(r'^analyze', views.analyze),
    url(r'^reqInventory', views.reqInventory),
    url(r'^setRealtimeLocation', views.setRealtimeLocation),
    url(r'^getRealtimeLocation', views.getRealtimeLocation),
    url(r'^moveCarInven', views.moveCarInven),
    url(r'^moveCarEditedInven', views.moveCarEditedInven),
    url(r'^busAcademy', views.busAcademy),
]
