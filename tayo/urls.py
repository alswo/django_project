from django.conf.urls import url, include
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('passenger.urls')),
    url(r'^inventory/',include('schedule.urls')),
    url(r'^optimizer/',include('optimizer.urls')),
    url(r'^api/',include('api.urls')),
    url(r'^getToken/',include('firebase.urls')),
    url(r'^fcm/', include('fcm.urls')),
    url(
        r'^accounts/login/',
        'django.contrib.auth.views.login',
        name='login',
        kwargs={
            'template_name': 'login.html'
        }
    ),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {
        'next_page': '/accounts/login',
        }, name='logout_url'
    ),
]
