from django.conf.urls import patterns, url, include
from firebase import views

urlpatterns = patterns('',
    url(r'', views.getStudentInfo),
)
