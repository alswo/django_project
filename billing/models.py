from __future__ import unicode_literals

from django.db import models
from passenger.models import Academy


class BillingManagement(models.Model):
    #academy = models.ForeignKey(Academy, related_name='billingmanagement', to_field='academy_id', db_column='academy_id', null=True, unique=True,)
    aid = models.ForeignKey(Academy, related_name='billingmanagement', null = True)
    billing_cost = models.IntegerField()
    trbegin = models.CharField(max_length=8)
    trend = models.CharField(max_length=8)
