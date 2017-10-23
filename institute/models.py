from __future__ import unicode_literals

from django.db import models
from passenger.models import Academy
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
import datetime

def set_current_date_time():
    return str(datetime.datetime.now())[:19]

# Create your models here.
class BillingHistorySetting(models.Model):
	academy = models.ForeignKey(Academy)
	carid = models.CharField(max_length=5)
	fix = models.CharField(max_length=10)
	monthpick = models.CharField(max_length=30)
	created_time = models.CharField(max_length=19, default = set_current_date_time)
	created_user = models.ForeignKey(User)
	setting = JSONField()
