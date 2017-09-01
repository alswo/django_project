#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.postgres.fields import ArrayField
from fcm_django.models import FCMDevice


class PropOfDevice(models.Model):

    device = models.ForeignKey(
        FCMDevice,
        related_name='propofdevice',
        to_field='device_id',
        db_column='device_id',
        null=True,
        unique=True,
        )
    slist = ArrayField(models.IntegerField(null=True, blank=True,
                       default=0))
    model = models.CharField(max_length=255, blank=True, null=True)
    version = models.CharField(max_length=255, blank=True, null=True)
    manufacture = models.CharField(max_length=255, blank=True,
                                   null=True)
    serial = models.CharField(max_length=255, blank=True, null=True)
