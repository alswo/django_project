from django.conf.urls import include, url
from drivermanager import views

urlpatterns = [
    url(r'^main', views.get_drivermanager_page),
    url(r'^getSchedule', views.get_schedule),
    url(r'^getCarSchedule', views.get_car_schedule),
    url(r'^carSalesStatus', views.car_sales_status),
    url(r'^salaryManagement', views.salary_management),
]


