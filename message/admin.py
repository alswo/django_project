from django.contrib import admin
from message.models import Report

class ReportAdmin(admin.ModelAdmin):
    list_display = ('mid','gid')

admin.site.register(Report, ReportAdmin)
