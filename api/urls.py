from django.conf.urls import url, include
from api import views

urlpatterns = [
    url(r'^getRealtimeLocation$', views.getRealtimeLocation),
    url(r'^getRealtimeLocationDebug$', views.getRealtimeLocationDebug),
    url(r'^getSchedulesForStudent$', views.getSchedulesForStudent),
    url(r'^getRouteMap$', views.getRouteMap),
    url(r'^listNotice$', views.listNotice),
    url(r'^getNotice$', views.getNotice),
    url(r'^getClauses$', views.getClauses),
    url(r'^getStudentInfo$', views.getStudentInfo2),
    url(r'^getStudentInfo2$', views.getStudentInfo2),
    url(r'^todayLoad$', views.todayLoad),
    url(r'^checkLoadState$', views.checkLoadState),
    url(r'^experienceGetSchedulesForStudent$', views.experienceGetSchedulesForStudent),
    url(r'^experienceGetRealtimeLocation$', views.experienceGetRealtimeLocation),
    url(r'^experienceGetRouteMap$', views.experienceGetRouteMap),
]
