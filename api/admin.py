from django.contrib import admin
from api.models import Notice, Clauses

# Register your models here.
class NoticeAdmin(admin.ModelAdmin):
	list_display = ('datetime', 'title')

class ClausesAdmin(admin.ModelAdmin):
	list_display = ('memberClauses',)

admin.site.register(Notice, NoticeAdmin)
admin.site.register(Clauses, ClausesAdmin)
