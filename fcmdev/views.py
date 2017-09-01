#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse, JsonResponse
from passenger.models import StudentInfo
from fcmdev.models import PropOfDevice
from fcm_django.models import FCMDevice
import firebase_admin
from firebase_admin import credentials
from jose import jwt
import Crypto.PublicKey.RSA as RSA
from jwt.contrib.algorithms.pycrypto import RSAAlgorithm
from django.views.decorators.csrf import csrf_exempt
import time
import sys


@csrf_exempt
def addDeviceInfo(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        registration_id = request.POST.get('registration_id')
        active = request.POST.get('active')
        osType = request.POST.get('type')
        device_id = request.POST.get('FCMDevice')
        slist = request.POST.getlist('slist')
        model = request.POST.get('Model')
        version = request.POST.get('Version')
        serial = request.POST.get('Serial')
        manufacture = request.POST.get('Manufacture')

        try:
            fcm_device = FCMDevice.objects.get(device_id=dev)
            fcm_device.registration_id = registration_id
            fcm_device.save(update_fields=['registration_id'])
            return HttpResponse('updated')
        except:
            fcmDevice = FCMDevice.objects.create(device_id=device_id, name= name, registration_id = registration_id, active = active, type = osType )
            fcmDevice.save()
            propofDevice = PropOfDevice.objects.create(
                device_id=device_id,
                slist=slist,
                model=model,
                version=version,
                serial=serial,
                manufacture=manufacture,
                )

            propofDevice.save()
            return HttpResponse('insert')
