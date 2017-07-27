from django.conf.urls import patterns, url, include
from api import views

urlpatterns = patterns('',
    url(r'^getRealtimeLocation$', views.getRealtimeLocation),
    url(r'^getSchedulesForStudent$', views.getSchedulesForStudent),
    url(r'^getRouteMap$', views.getRouteMap),
    url(r'^listNotice$', views.listNotice),
    url(r'^getNotice$', views.getNotice),
    url(r'^getStudentInfo$', views.getStudentInfo),
)
