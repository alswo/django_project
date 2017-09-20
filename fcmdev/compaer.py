#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse, JsonResponse
from fcmdev.models import PropOfDevice
from fcm_django.models import FCMDevice
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
        device_id = request.POST.get('device_id')
        model = request.POST.get('model')
        version = request.POST.get('version')
        serial = request.POST.get('serial')
        manufacture = request.POST.get('manufacture')
        pin_number = request.POST.get('pin_number')
        push = request.POST.get('recvpush')

        try:
            if push == 'false':
                push = False
            elif push = 'true':
                push = True
            else:
                push = push

            fcm_device = FCMDevice.objects.get(device_id=device_id)
            fcm_device.registration_id = registration_id
            fcm_device.save()
            prop_device = PropOfDevice.objects.get(device_id=device_id)
            prop_device.receivePush = push
            prop_device.save()

            return HttpResponse('updated')

        except FCMDevice.DoesNotExist:
            if push == 'false' :
                push = False
            elif push = 'true':
                push = True
            else:
                push = push

            fcmDevice = FCMDevice.objects.create(device_id=device_id,
                    name=name, registration_id=registration_id,
                    active=active, type=osType)
            fcmDevice.save()
            propofDevice = PropOfDevice.objects.create(
                device_id=device_id,
                pin_number=pin_number,
                model=model,
                version=version,
                serial=serial,
                manufacture=manufacture,
                receivePush=push
                )

            propofDevice.save()
            return HttpResponse('insert')
        except ValueError as e:
            return HttpResponse(e)
