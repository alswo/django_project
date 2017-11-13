from __future__ import unicode_literals
from django.contrib.postgres.fields import JSONField
from django.db import models

class Report(models.Model):
    gid = models.CharField(max_length = 28) 
    mid = models.CharField(max_length = 35)
    report = JSONField()

