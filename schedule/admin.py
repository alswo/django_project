from django.contrib import admin
from schedule.models import Branch, Building, Inventory, ScheduleTable
# Register your models here.
class BranchAdmin(admin.ModelAdmin):
    list_display = ('bname','id',)

class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name','id',)

class InventoryAdmin(admin.ModelAdmin):
    list_display = ('id','carnum','bid',)

class ScheduleTableAdmin(admin.ModelAdmin):
    list_display = ('iid','time','sname',)

admin.site.register(Branch, BranchAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(ScheduleTable, ScheduleTableAdmin)
