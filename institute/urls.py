from django.conf.urls import url, include
from institute import views

urlpatterns = [
    url(r'^setSession$', views.setSession),
    url(r'^listStudents$', views.listStudents),
    url(r'^addStudentsForm$', views.addStudentsForm),
    url(r'^addStudent$', views.addStudent),
    url(r'^updateStudentsForm$', views.updateStudentsForm),
    url(r'^updateStudent$', views.updateStudent),
    url(r'^deleteStudent$', views.deleteStudent),
    url(r'^addClassForm$', views.addClassForm),
    url(r'^getHistory$', views.getHistory),
    url(r'^getMonthlyHistory$', views.getHistory),
    url(r'^addAcademyForm$', views.addAcademyForm),
    url(r'^updateAcademyForm$', views.updateAcademyForm),
    url(r'^addAcademy$', views.addAcademy),
    url(r'^updateAcademy$', views.updateAcademy),
    url(r'^listAcademies$', views.listAcademies),
    url(r'^saveBill$', views.saveBill),
    url(r'^listAcademiesBilling$', views.listAcademiesBilling),
    url(r'^saveBillingHistorySetting$', views.saveBillingHistorySetting),
]
