from django.conf.urls import patterns, url, include
from passenger import views

urlpatterns = patterns('',
    url(r'^$', views.main),
    url(r'^schedule', views.schedule),
    url(r'^safetyTayo', views.safetyTayo),
    url(r'^opti$', views.opti),
    url(r'^opti2$', views.opti2),
    url(r'^opti_0613$', views.opti_0613),
    url(r'^opti_0428$', views.opti_0428),
    url(r'^addSchedule', views.addSchedule),
    url(r'^day', views.day),
    url(r'^driverday', views.driverday),
    url(r'^academySchedule', views.academySchedule),
    url(r'^driverSchedule', views.driverSchedule),
    url(r'^updateDay', views.updateDay),
    url(r'^uDay', views.updateDayAca),
    url(r'^updateSchedule', views.updateSchedule),
    url(r'^uAca', views.uAca),
    url(r'^saveSchedule', views.saveSchedule),
    url(r'^deleteSchedule', views.deleteSchedule),
    url(r'^uSchedule', views.uSchedule),
    url(r'^sturegi', views.sturegi),
    url(r'^acaphone', views.acaphone),
    url(r'^studata', views.studata),
    url(r'^dateSchedule', views.dateSchedule),
    url(r'^community',views.community),
    url(r'^getAcaButton', views.getAcaButton),
    url(r'^getDriButton', views.getDriButton),
    url(r'^studentInfo', views.studentInfo),
    url(r'^robots.txt$', views.robots),
)
