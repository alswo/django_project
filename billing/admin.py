from django.contrib import admin
from billing.models import BillingManagement

# Register your models here.
class BillingManagementAdmin(admin.ModelAdmin):
    list_display = ('aid', 'billing_cost')
    search_fields = ['aid']


admin.site.register(BillingManagement, BillingManagementAdmin)
