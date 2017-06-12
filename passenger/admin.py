from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from passenger.models import Profile
from passenger.models import Academy, Commute, Schedule, ShuttleSchedule, AcademySchedule, Group, PhoneList, ScheduleDate, StudentInfo,Community,Grade
from simple_history.admin import SimpleHistoryAdmin
from passenger.forms import StudentInfoForm

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )

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
    search_fields = ['aname','sname']
    fields = ('academySelection','aid','aname','bid','bname','sname','grade','phone1','phonelist')
    list_display = ('__unicode__',)
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

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
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
