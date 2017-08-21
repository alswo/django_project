from django.conf.urls import patterns, url, include
from institute import views

urlpatterns = patterns('',
    url(r'^setSession$', views.setSession),
    url(r'^listStudents$', views.listStudents),
    url(r'^addStudentsForm$', views.addStudentsForm),
    url(r'^addStudent$', views.addStudent),
    url(r'^updateStudentsForm$', views.updateStudentsForm),
    url(r'^updateStudent$', views.updateStudent),
    url(r'^addClassForm$', views.addClassForm),
)
