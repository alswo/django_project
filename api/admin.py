from django.contrib import admin
from api.models import Notice

# Register your models here.
class NoticeAdmin(admin.ModelAdmin):
	list_display = ('datetime', 'title')

admin.site.register(Notice, NoticeAdmin)
