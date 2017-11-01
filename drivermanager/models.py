from django.db import models
from schedule.models import Car

# Create your models here.
class Salary(models.Model):
    carnum = models.ForeignKey(Car, related_name='car') 
    payment_date = models.CharField(max_length = 20)
    p_salary = models.CharField(max_length = 8)
    d_salary = models.CharField(max_length = 8)
    etc = models.CharField(max_length = 8,null=True)
    etc_content = models.TextField(null=True)
    
    def __unicode__(self):
        return self.carnum
