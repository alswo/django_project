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
    model = models.CharField(max_length=255, blank=True, null=True)
    version = models.CharField(max_length=255, blank=True, null=True)
    manufacture = models.CharField(max_length=255, blank=True,
                                   null=True)
    serial = models.CharField(max_length=255, blank=True, null=True)
    pin_number = models.CharField(max_length = 20, null = False, default = "-")
    receivePush = models.BooleanField(default=False)


class PushConfirming(models.Model):

    date = models.DateTimeField(auto_now_add=True, null=True)
    confirming = models.TextField()
    sid = models.IntegerField(blank=True, null=True)
    status = models.BooleanField(default=True)
    token = models.TextField(blank=True, null=True)
    pin = models.CharField(max_length=255, blank=True, null=True)

class PushMonitoring(models.Model):
    date = models.CharField(max_length=20, blank=True, null=True)
    total_S = models.CharField(max_length=10, blank=True, null=True)
    expec_push = models.CharField(max_length=10, blank=True, null=True)
    expec_push_s = models.CharField(max_length=10, blank=True, null=True)
    push_num = models.CharField(max_length=10, blank=True, null=True)
    false_num = models.CharField(max_length=10, blank=True, null=True)
    refuse_user = models.CharField(max_length=10, blank=True, null=True)
