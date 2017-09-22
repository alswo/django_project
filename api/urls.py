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
    url(r'^getStudentInfo$', views.getStudentInfo),
    url(r'^getStudentInfo2$', views.getStudentInfo2),
    url(r'^todayLoad$', views.todayLoad),
    url(r'^checkLoadState$', views.checkLoadState),
<<<<<<< HEAD
    url(r'^getDeviceInfo$', views.getDeviceInfo),
    url(r'^pushConfirmInfo$', views.pushConfirmInfo),
)
=======
    url(r'^experienceGetSchedulesForStudent$', views.experienceGetSchedulesForStudent),
    url(r'^experienceGetRealtimeLocation$', views.experienceGetRealtimeLocation),
    url(r'^experienceGetRouteMap$', views.experienceGetRouteMap),
]
>>>>>>> c70c00d3fe12bb407c572f4f2b2738759ab6d307
