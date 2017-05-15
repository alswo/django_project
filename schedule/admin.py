from django.contrib import admin
from schedule.models import Branch, Building, Inventory, ScheduleTable
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.
class BranchAdmin(SimpleHistoryAdmin):
    list_display = ('bname','id',)

class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name','id',)

class InventoryAdmin(SimpleHistoryAdmin):
    list_display = ('__unicode__',)

class ScheduleTableAdmin(SimpleHistoryAdmin):
    list_display = ('inventory_name', '__unicode__',)
    list_display_links = ('__unicode__',)
    #ordering = ('iid', 'time',)

    def inventory_name(self, obj):
        return obj.iid.__unicode__()
    inventory_name.admin_order_field = 'inventory'


admin.site.register(Branch, BranchAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(ScheduleTable, ScheduleTableAdmin)
