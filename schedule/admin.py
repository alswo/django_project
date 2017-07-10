from django.contrib import admin
from schedule.models import Branch, Building, Inventory, ScheduleTable, Car,Area,EditedInven, EditedScheduleTable
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.
class BranchAdmin(SimpleHistoryAdmin):
    list_display = ('bname','id',)

class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name','id',)

class InventoryAdmin(SimpleHistoryAdmin):
    list_display = ('__unicode__',)

class ScheduleTableAdmin(admin.ModelAdmin):
    list_display = ('inventory_name', '__unicode__',)
    list_display_links = ('__unicode__',)
    #ordering = ('iid', 'time',)

    def inventory_name(self, obj):
        return obj.iid.__unicode__()

    inventory_name.admin_order_field = 'inventory'

class AreaAdmin(SimpleHistoryAdmin):
    list_display = ('name',)

class CarAdmin(admin.ModelAdmin):
    list_display = ('carname','branchid',)

class EditedInvenAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)

class EditedScheduleTableAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)

admin.site.register(Area,AreaAdmin)
admin.site.register(Car,CarAdmin)
admin.site.register(Branch, BranchAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(ScheduleTable, ScheduleTableAdmin)
admin.site.register(EditedInven, EditedInvenAdmin)
admin.site.register(EditedScheduleTable, EditedScheduleTableAdmin)
