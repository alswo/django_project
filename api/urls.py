from django.conf.urls import patterns, url, include
from api import views

urlpatterns = patterns('',
    url(r'^getRealtimeLocation$', views.getRealtimeLocation),
    url(r'^getRealtimeLocationDebug$', views.getRealtimeLocationDebug),
    url(r'^getSchedulesForStudent$', views.getSchedulesForStudent),
    url(r'^getRouteMap$', views.getRouteMap),
    url(r'^listNotice$', views.listNotice),
    url(r'^getNotice$', views.getNotice),
    url(r'^getClauses$', views.getClauses),
    url(r'^getStudentInfo$', views.getStudentInfo),
    url(r'^getStudentInfo2$', views.getStudentInfo2),
    url(r'^todayLoad$', views.todayLoad),
    url(r'^checkLoadState$', views.checkLoadState),
    url(r'^addDeviceInfo$', views.getDeviceInfo),
    url(r'^pushConfirmInfo$', views.pushConfirmInfo),
)
