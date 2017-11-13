from django.conf.urls import url, include
from django.contrib import admin
from fcm_django.api.rest_framework import FCMDeviceViewSet, FCMDeviceAuthorizedViewSet
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
from django.contrib.auth import views as auth_views

router = DefaultRouter()
router.register(r'devices', FCMDeviceViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('passenger.urls')),
    url(r'^inventory/',include('schedule.urls')),
    url(r'^optimizer/',include('optimizer.urls')),
    url(r'^api/',include('api.urls')),
    url(r'^institute/',include('institute.urls')),
    url(r'^indicator/',include('indicator.urls')),
    url(r'^message/',include('message.urls')),
    url(r'^monitor/',include('monitor.urls')),
    url(r'^fcm/', include('fcm.urls')),
    url(r'^fcmdev/',include('fcmdev.urls')),
    url(r'^dm/',include('drivermanager.urls')),
    url(r'^', include(router.urls)),
    url(
        r'^accounts/login/',
        auth_views.login,
        name='login',
        kwargs={
            'template_name': 'login.html'
        }
    ),
    url(r'^logout/$', auth_views.logout, {
        'next_page': '/accounts/login',
        }, name='logout_url'
    ),
]
