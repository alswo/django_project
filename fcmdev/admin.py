from django.contrib import admin
from fcmdev.models import PropOfDevice, PushConfirming

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('id','device', 'model','version','serial','manufacture')
    search_fields = ['pin_number']
class PushConfirmAdmin(admin.ModelAdmin):
    list_display = ('date','pin', 'status', 'sid')
    search_fields = ['date','pin','status','sid']

admin.site.register(PropOfDevice, DeviceAdmin)
admin.site.register(PushConfirming, PushConfirmAdmin)
