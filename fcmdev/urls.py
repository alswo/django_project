from django.conf.urls import patterns, url, include
from fcmdev import views

urlpatterns = patterns('',
    url(r'^addDeviceInfo/$', views.addDeviceInfo),
)
