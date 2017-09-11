from fcm.models import AbstractDevice
from django.contrib.postgres.fields import ArrayField
from django.db import models

class MyDevice(AbstractDevice):
    sid = ArrayField(models.IntegerField())
    phone_num = models.CharField(max_length=20)
    uid = models.CharField(max_length=50)
    pin_num = models.CharField(max_length=20)

