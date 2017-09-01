#!/usr/bin/python
# -*- coding: utf-8 -*-

from schedule.models import Inventory, ScheduleTable, \
    HistoryScheduleTable, EditedInven, EditedScheduleTable
from passenger.models import StudentInfo, Academy, ShuttleSchedule, \
    ScheduleDate
from passenger.dateSchedule import timeToDate
from fcmdev.models import PropOfDevice
from fcm_django.models import FCMDevice
from schedule.models import Inventory, ScheduleTable, EditedInven, \
    EditedScheduleTable
import sys
import requests
import simplejson
reload(sys)
sys.setdefaultencoding('utf-8')

def nts(sid, msg):
    url = 'https://fcm.googleapis.com/fcm/send'

    devProp = []
    fcmDevice = []

    devProp = PropOfDevice.objects.filter(slist__contains=sid) # PropOfDevice models 에서 파라미타값 sid 에 해당하는 row
    # for x in devProp:
    #     x = devProp
    #     print("1111")
    #     print (x)
    print (devProp)

    for dp in devProp:
        devid = dp.device_id
        print (devid)
        fcmDevice = FCMDevice.objects.filter(device_id=devid)# FCMDevice models 에서 해당하는 device_id 값을 갖고있는 row
        for dod in fcmDevice:
            token = dod.registration_id
            print (token)
            #if type == android
            #else:
            push_msg(token, msg)

            # try:
            #     push_msg(token, msg)
            # except:
            #     msg = 'SID does not exist'
            #     return getResponse(debug, 400, msg)

            # try:
            #     payload = '{\n    "to" : "' + token + '","priority" : "high","notification": {\t  "body" : "'+msg+'","title" : "frfrf", "sound":"default", "color":"#0066ff"},\t"time_to_live": 4}'
            #     headers = {'authorization': 'key=AAAAFt1BOGQ:APA91bEHypaznqDJeVzBcRuyBcqjtNDbIK-POYriP5w4_uW9exqHf9zKyS-nZJkNIFQbVvcceLx6JK1gQcXOY8NqjvGqIwZXhe2kaNq4Qq4l2rTOA-r9fYggMImvwKHEPiEfytrfwboy','content-type': 'application/json'}
            #     response = requests.request('POST', url, data=payload,headers=headers)
            #     msg = response.text
            #     print(idx, response)
            #
            # except StudentInfo.DoesNotExist:
            #
            #     msg = 'SID does not exist'
            #     return getResponse(debug, 400, msg)

def push_msg_android(token, msg):
    url = 'https://fcm.googleapis.com/fcm/send'
    payload = '{\n    "to" : "' + token + '","priority" : "high","notification": {\t  "body" : "'+msg+'","title" : "shuttle tayo", "sound":"default", "color":"#0066ff"},\t"time_to_live": 4}'
    headers = {'authorization': 'key=AAAAFt1BOGQ:APA91bEHypaznqDJeVzBcRuyBcqjtNDbIK-POYriP5w4_uW9exqHf9zKyS-nZJkNIFQbVvcceLx6JK1gQcXOY8NqjvGqIwZXhe2kaNq4Qq4l2rTOA-r9fYggMImvwKHEPiEfytrfwboy','content-type': 'application/json'}
    try:
        response = requests.request('POST', url, data=payload,headers=headers)
        msg = response.text
    except StudentInfo.DoesNotExist:
        msg = 'SID does not exist'
        return getResponse(debug, 400, msg)

def push_msg_ios(token, msg):
    url = 'https://fcm.googleapis.com/fcm/send'
    payload = '{\n    "to" : "' + token + '","priority" : "high","notification": {\t  "body" : "'+msg+'","title" : "shuttle tayo", "sound":"default", "color":"#0066ff"},\t"time_to_live": 4}'
    headers = {'authorization': 'key=AAAAFt1BOGQ:APA91bEHypaznqDJeVzBcRuyBcqjtNDbIK-POYriP5w4_uW9exqHf9zKyS-nZJkNIFQbVvcceLx6JK1gQcXOY8NqjvGqIwZXhe2kaNq4Qq4l2rTOA-r9fYggMImvwKHEPiEfytrfwboy','content-type': 'application/json'}
    try:
        response = requests.request('POST', url, data=payload,headers=headers)
        msg = response.text
    except StudentInfo.DoesNotExist:
        msg = 'SID does not exist'
        return getResponse(debug, 400, msg)



def find_update():
    t = timeToDate()
    d = t.timeToD()
    studentset = set()
    scheduletables = list()

    # lastweek = ''
    # lastweekt = timeToDate()
    # lastweekt.setLastWeekDay()
    # lastweek = lastweekt.timeToYmd()

    inventory_ids = list()

    inventories = Inventory.objects.filter(day=d).select_related()
    for inventory in inventories:
        inventory_ids.append(inventory.id)
        scheduletables = \
            ScheduleTable.objects.filter(iid_id=inventory.id).order_by('time'
                )
        for scheduletable in scheduletables:
            if scheduletable.slist != None or len(scheduletable.slist) \
                != 0:
                for sid in scheduletable.slist:
                    studentset.add(str(sid))

    # print "lastweek = " + lastweek

    print 'len = ' + str(len(studentset))

    # print "inv_len = " + str(len(inventory_ids))

    for sid in studentset:

        # for inventory in inventories:

        try:
            studentinfo = StudentInfo.objects.get(id=sid)
        except StudentInfo.DoesNotExist:
            continue
        scheduletables = \
            ScheduleTable.objects.filter(iid_id__in=inventory_ids).filter(slist__contains=[sid]).order_by('time'
                )
        # old_scheduletables = \
        #     HistoryScheduleTable.objects.filter(date=lastweek).filter(iid_id__in=inventory_ids).filter(members__in=[studentinfo]).order_by('time'
        #         )

        msg = ''
        for scheduletable in scheduletables:
            found = False
            same_inventory = False
            # for old_scheduletable in old_scheduletables:
            #     if scheduletable.iid_id == old_scheduletable.iid_id:
            #         same_inventory = True
            #         if scheduletable.time == old_scheduletable.time \
            #             and scheduletable.addr \
            #             == old_scheduletable.addr:
            #             found = True
            print 'found True : ' + str(sid)
            inventory = Inventory.objects.get(id=scheduletable.iid_id)
            msg += "{" + inventory.day + '} [' + scheduletable.time + '] : ' + scheduletable.addr + '\n'
            print(" sid : " + sid + " msg : "+ msg)

        if msg != '':

            nts(sid, msg)

    nts(0, 'end')


# def notice_to_student(sid, msg):
#
# ....propOfDevice = PropOfDevice.objects.filter(slist__contains = sid)
#
# ....url = "https://fcm.googleapis.com/fcm/send"
#
#         for p in propOfDevice:
#             token = p.token
#
# ....    try:
# ....        payload = "{\n    \"to\" : \"" + token + "\",\n    \"priority\" : \"high\",\n    \"notification\": {\n\t  \"body\" : \"" + msg + "\",\n      \"title\" : \"frfrf\",\n      \"sound\":\"default\",\n      \"color\":\"#0066ff\"\n      \n  },\n\t\"time_to_live\": 4\n  }"
#
#                 headers = {
# ........    'authorization': "key=AAAAFt1BOGQ:APA91bEHypaznqDJeVzBcRuyBcqjtNDbIK-POYriP5w4_uW9exqHf9zKyS-nZJkNIFQbVvcceLx6JK1gQcXOY8NqjvGqIwZXhe2kaNq4Qq4l2rTOA-r9fYggMImvwKHEPiEfytrfwboy",
# ........    'content-type': "application/json",
#                 }
#
#                 response = requests.request("POST", url, data=payload, headers=headers)
#
# ........print(response.text)
#
#                 return HttpResponse(0)
#
# ....    except StudentInfo.DoesNotExist:
# ....        name = "none"
#
# ....        return HttpResponse(1)
