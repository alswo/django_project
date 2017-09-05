from django.conf.urls import url, include
from indicator import views

urlpatterns = [
    url(r'^shuttleIndicator$', views.shuttleIndicator),
]
