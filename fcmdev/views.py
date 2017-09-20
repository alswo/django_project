#!/usr/bin/python

# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse, JsonResponse
from fcmdev.models import PropOfDevice, PushConfirming
from fcm_django.models import FCMDevice
from django.views.decorators.csrf import csrf_exempt


def getResponse(debug, code, msg):
	if (debug == 1):
		return HttpResponse(msg)
	else:
		return JsonResponse({'code': code, 'msg': msg})

# @csrf_exempt
# def add(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         registration_id = request.POST.get('registration_id')
#         active = True
#         osType = request.POST.get('type')
#         device_id = request.POST.get('device_id')
#         model = request.POST.get('model')
#         version = request.POST.get('version')
#         serial = request.POST.get('serial')
#         manufacture = request.POST.get('manufacture')
#         pin_number = request.POST.get('pin_number')
#         push = request.POST.get('recvpush')
#         debug = request.POST.get('debug')
#
#         if (debug):
#             debug = 1
#         else:
#             debug = 0
#
#         if push == 'false':
#             push = False
#         elif push == 'true':
#             push = True
#         else:
#             push = push
#
#         if (registration_id == None):
#             msg = "there is no registration_id"
#             return getResponse(debug, 400, msg)
#
#         elif (device_id == None):
#             msg = "there is no device_id"
#             return getResponse(debug, 400, msg)
#         elif (osType == None):
#             msg = "there is no osType"
#             return getResponse(debug, 400, msg)
#         elif (push == None):
#             msg = "there is no recvpush"
#             return getResponse(debug, 400, msg)
#
#         try:
#             fcm_device = FCMDevice.objects.get(device_id=device_id)
#             fcm_device.registration_id = registration_id
#             fcm_device.save()
#             prop_device = PropOfDevice.objects.get(device_id=device_id)
#             prop_device.pin_number = pin_number
#             prop_device.receivePush = push
#             prop_device.save()
#
#             msg = 'update'
#             return getResponse(debug, 200, msg)
#
#         except FCMDevice.DoesNotExist:
#
#             fcmDevice = FCMDevice.objects.create(device_id=device_id,
#                     name=name, registration_id=registration_id,
#                     active=active, type=osType)
#             fcmDevice.save()
#             propofDevice = PropOfDevice.objects.create(
#                 device_id=device_id,
#                 pin_number=pin_number,
#                 model=model,
#                 version=version,
#                 serial=serial,
#                 manufacture=manufacture,
#                 receivePush=push
#                 )
#
#             propofDevice.save()
#             msg = 'insert'
#             return getResponse(debug, 201, msg)
#
#         except:
#             msg = "error."
#             return getResponse(debug, 400, msg)





@csrf_exempt
def addDeviceInfo(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        registration_id = request.POST.get('registration_id')
        active = True
        osType = request.POST.get('type')
        device_id = request.POST.get('device_id')
        model = request.POST.get('model')
        version = request.POST.get('version')
        serial = request.POST.get('serial')
        manufacture = request.POST.get('manufacture')
        pin_number = request.POST.get('pin_number')
        push = request.POST.get('recvpush')
        debug = request.POST.get('debug')

        if (debug):
            debug = 1
        else:
            debug = 0

        if push == 'false':
            push = False
        elif push == 'true':
            push = True
        else:
            push = push

        if (registration_id == None):
            msg = "there is no registration_id"
            return getResponse(debug, 400, msg)
        elif (device_id == None):
            msg = "there is no device_id"
            return getResponse(debug, 400, msg)

	elif (push == None):
            msg = "there is no recvpush"
            return getResponse(debug, 400, msg)


        try:
            fcm_device = FCMDevice.objects.get(device_id=device_id)
            fcm_device.registration_id = registration_id
            fcm_device.save()
            prop_device = PropOfDevice.objects.get(device_id=device_id)
            prop_device.pin_number = pin_number
            prop_device.receivePush = push
            prop_device.save()

            msg = 'update'
            return getResponse(debug, 200, msg)

        except FCMDevice.DoesNotExist:


			fcmDevice = FCMDevice.objects.create(device_id=device_id,name=name, registration_id=registration_id,active=active, type=osType)
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
			msg = 'insert'
			return getResponse(debug, 201, msg)
	except:
			msg = "error."
			return getResponse(debug, 400, msg)





@csrf_exempt
def pushConfirmInfo(request):
    if request.method == 'POST':
        pin = request.POST.get('pin')
        confirming = request.POST.get('confirming')
        status = request.POST.get('status')
        token = request.POST.get('token')
        debug = request.POST.get('debug')

        if (debug):
            debug = 1
        else:
            debug = 0

        if status == '1':
            status = True
        elif status == '0':
            status = False
        else:
            status = True
        try:
            pushConfirm = PushConfirming.objects.create(pin=pin, confirming=confirming, status=status, token=token)
            pushConfirm.save()
            msg = "confirm"
            return getResponse(debug, 200, msg)

        except:
            msg = "error"
            return getResponse(debug, 400, msg)
