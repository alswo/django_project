from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from passenger.models import Academy, Commute, Schedule, ShuttleSchedule, AcademySchedule, Group, PhoneList, ScheduleDate, StudentInfo,Community,Grade,Profile
from simple_history.admin import SimpleHistoryAdmin
from passenger.forms import StudentInfoForm, ProfileInfoForm, AcademyForm

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fields = ('academySelection','bid','aid','cid')
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    form = ProfileInfoForm

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 's_name', 'load','unload')

class AcademyAdmin(SimpleHistoryAdmin):
    model = Academy
    list_display = ('name','id',)

    form = AcademyForm

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

class GradeAdmin(admin.ModelAdmin):
    list_display = ('name',)

class CommunityAdmin(admin.ModelAdmin):
    list_display = ('aname','showdate')

class CommuteAdmin(SimpleHistoryAdmin):
    list_display = ('name','a_name')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
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
