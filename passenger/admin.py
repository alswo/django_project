from django.contrib import admin
from passenger.models import Academy, Commute, Schedule, ShuttleSchedule, AcademySchedule, Group, PhoneList, ScheduleDate, StudentInfo,Community,Grade
from simple_history.admin import SimpleHistoryAdmin
from passenger.forms import StudentInfoForm

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 's_name', 'load','unload')

class AcademyAdmin(SimpleHistoryAdmin):
    list_display = ('name','id')

class ShuttleScheduleAdmin(admin.ModelAdmin):
    list_display = ('a_name','day','time','alist','aid')

class AcademyScheduleAdmin(admin.ModelAdmin):
    list_display = ('gid','aname')

class GroupAdmin(admin.ModelAdmin):
    list_display = ('gname','gid')

class PhoneListAdmin(admin.ModelAdmin):
    list_display = ('name', 'aname')

class ScheduleDateAdmin(admin.ModelAdmin):
    list_display = ('a_name', 'day', 'time')

class StudentInfoAdmin(SimpleHistoryAdmin):
    fields = ('academySelection','aid','aname','bid','bname','sname','grade','phone1','phonelist')
    list_display = ('bname', 'aname', 'sname', 'id')
    form = StudentInfoForm

    class Media:
        js = (
            'js/jquery-1.11.1.min.js',
            'js/changedAid.js'
        )

class GradeAdmin(admin.ModelAdmin):
    list_display = ('name',)

class CommunityAdmin(admin.ModelAdmin):
    list_display = ('aname','showdate')

class CommuteAdmin(SimpleHistoryAdmin):
    list_display = ('name','a_name')


admin.site.register(Group, GroupAdmin)
admin.site.register(Schedule,ScheduleAdmin)
admin.site.register(Academy,AcademyAdmin)
admin.site.register(ShuttleSchedule,ShuttleScheduleAdmin)
admin.site.register(AcademySchedule,AcademyScheduleAdmin)
admin.site.register(PhoneList,PhoneListAdmin)
admin.site.register(ScheduleDate, ScheduleDateAdmin)
admin.site.register(StudentInfo, StudentInfoAdmin)
admin.site.register(Community, CommunityAdmin)
admin.site.register(Commute, CommuteAdmin)
admin.site.register(Grade,GradeAdmin)
