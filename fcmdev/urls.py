from django.conf.urls import patterns, url, include
from fcmdev import views

urlpatterns = patterns('',
    url(r'^getDeviceInfo$', views.getDeviceInfo),
    url(r'^pushConfirmInfo$', views.pushConfirmInfo),
    url(r'^pushchecker$', views.pushchecker)
)
