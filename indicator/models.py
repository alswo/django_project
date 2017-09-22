from __future__ import unicode_literals

from django.db import models
from schedule.models import Car
from passenger.models import Academy

# Create your models here.
class BaseIndicator(models.Model):
	date = models.CharField(max_length=10)
	# following means total number
	inventorynum = models.IntegerField()
	scheduletablenum = models.IntegerField()
	studentinfonum = models.IntegerField()
	# following means today's number
	dayinventorynum = models.IntegerField()
	dayscheduletablenum = models.IntegerField()
	daystudentinfonum = models.IntegerField()

	class Meta:
		abstract = True

class ShuttleIndicator(BaseIndicator):
	car = models.ForeignKey(Car)
	
class InstituteIndicator(BaseIndicator):
	academy = models.ForeignKey(Academy)
