from django.contrib import admin
from passenger.models import Commute, Academy, Schedule, ShuttleSchedule, AcademySchedule, Group, PhoneList, ScheduleDate, Branch, StudentInfo,Community
from simple_history.admin import SimpleHistoryAdmin

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

class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'location')

class StudentInfoAdmin(SimpleHistoryAdmin):
    list_display = ('bname', 'aname', 'sname', 'id')

class CommunityAdmin(admin.ModelAdmin):
    list_display = ('aname','showdate')

class CommuteAdmin(SimpleHistoryAdmin):
    list_display = ('name','a_name')


admin.site.register(Branch, BranchAdmin)
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
