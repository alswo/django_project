from __future__ import unicode_literals

from django.db import models
from schedule.models import Car
from passenger.models import Academy

# Create your models here.
class BaseIndicator(models.Model):
	date = models.CharField(max_length=10)
	# following means total number
	inventoryNum = models.IntegerField()
	scheduleTableNum = models.IntegerField()
	studentInfoNum = models.IntegerField()
	# following means today's number
	dayInventoryNum = models.IntegerField()
	dayScheduleTableNum = models.IntegerField()
	dayStudentInfoNum = models.IntegerField()

	class Meta:
		abstract = True

class ShuttleIndicator(BaseIndicator):
	car = models.ForeignKey(Car)
	
class InstituteIndicator(BaseIndicator):
	academy = models.ForeignKey(Academy)
