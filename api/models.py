from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

# Create your models here.

def getNow():
	return timezone.localtime(timezone.now())

class Notice(models.Model):
	title = models.CharField(max_length=50)
	datetime = models.DateTimeField(default=timezone.now)
	content = models.TextField()

class Clauses(models.Model):
	datetime = models.DateTimeField(default=timezone.now)
	memberClauses = models.TextField()
	personalInfoClauses = models.TextField()
