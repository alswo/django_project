from django.conf.urls import patterns, url, include
from indicator import views

urlpatterns = patterns('',
    url(r'^shuttleIndicator$', views.shuttleIndicator),
)
