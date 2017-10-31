from django.contrib import admin
from drivermanager.models import Salary

class SalaryAdmin(admin.ModelAdmin):
    list_display = ('payment_date','p_salary','carnum',)

admin.site.register(Salary, SalaryAdmin)
