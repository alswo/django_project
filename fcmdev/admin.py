from django.contrib import admin
from fcmdev.models import PropOfDevice, PushConfirming

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('id','device', 'model','version','serial','manufacture')

class PushConfirmAdmin(admin.ModelAdmin):
    list_display = ('date','pin', 'status')


admin.site.register(PropOfDevice, DeviceAdmin)
admin.site.register(PushConfirming, PushConfirmAdmin)
