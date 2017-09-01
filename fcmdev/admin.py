from django.contrib import admin
from fcmdev.models import PropOfDevice

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device', 'model','version','serial','manufacture')

admin.site.register(PropOfDevice, DeviceAdmin)
