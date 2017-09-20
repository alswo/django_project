#!/usr/bin/python
# -*- coding: utf-8 -*-

from schedule.models import Inventory, ScheduleTable, \
    HistoryScheduleTable, EditedInven, EditedScheduleTable
from passenger.models import StudentInfo, Academy, ShuttleSchedule, \
    ScheduleDate, PersonalInfo
from passenger.dateSchedule import timeToDate
from fcmdev.models import PropOfDevice
from fcm_django.models import FCMDevice
from schedule.models import Inventory, ScheduleTable, EditedInven, \
    EditedScheduleTable

from collections import Counter
import sys
import requests
import simplejson
import datetime
reload(sys)
sys.setdefaultencoding('utf-8')

def test():
    time = timeToDate()
    date = time.timeToD()

    scheduleTables = []
    sl = []
    inventorys = Inventory.objects.filter(day = date).prefetch_related('scheduletables').reverse()
    for inv in inventorys:
        sch = ScheduleTable.objects.filter(iid = inv.id)
        for sc in sch:
            sl.extend(sc.slist)

    print (len(set(sl)))

    for inven in inventorys:
        scheduleTables.extend(inven.scheduletables.all()) #금일 에 해당하는 모든 인벤토리 객체를 scheduleTables 로..

    print ("++++"+str(len(set(scheduleTables))))
    count_slist = []
    for schTable in scheduleTables:
        if len(schTable.slist) >= 1:
            count_slist.extend(schTable.slist) #

    dict_slist = dict(Counter(count_slist))

    push_content = []

    i = 0
    x = 0
    for key, value in dict_slist.iteritems():
        for s in scheduleTables:
            if len(s.slist) >= 1:
                while(key in s.slist):
                    try:
                        sInfo = StudentInfo.objects.get(id=key)
                    except StudentInfo.DoesNotExist:
                        print ("-------------------"+str(sInfo.id))
                        x += 1
                        sInfo = None
                        break
                    else:
                        pin = PersonalInfo.objects.get(id = sInfo.personinfo_id)
                        module_push_content = {}
                        module_push_content['time'] = s.time
                        module_push_content['addr'] = s.addr
                        module_push_content['aname'] = sInfo.aname
                        module_push_content['pin'] = pin.pin_number
                        module_push_content['sid'] = key
                        module_push_content['count'] = value
                        push_content.append(module_push_content)
                        break

        count = module_push_content['count']-1
        if count == 0:
            i += 1
            msg = "\t\t오늘 " + module_push_content['aname'] + " 등원을 위한 " + module_push_content['time'] + " [" + module_push_content['addr'] + "] 승차 스케줄이 있습니다\n"
            msg = msg.decode('utf-8').encode('utf-8')
            push_msg_test(module_push_content['sid'], module_push_content['pin'], msg)
            #notice_to_slack(module_push_content['sid'], msg)
            #push_msg_test(module_push_content['sid'], module_push_content['pin'], msg)
        else:
            i += 1
            msg = "\t\t오늘 " + module_push_content['aname'] + " 등원을 위한 " + module_push_content['time'] + " [" + module_push_content['addr'] + "]승차 외" + str(count) + "건의 스케줄이 있습니다.\n"
            msg = msg.decode('utf-8').encode('utf-8')
            push_msg_test(module_push_content['sid'], module_push_content['pin'], msg)
            #notice_to_slack(module_push_content['sid'], msg)
            #push_msg_test(module_push_content['sid'], module_push_content['pin'], msg)
    print ("call"+ str(i) +"error"+ str(x))

def push_msg_test(sid, pin, msg):
    stuinfo = StudentInfo.objects.get(id = sid)
    sname = stuinfo.sname
    print (sname)
    print (sid)
    print (pin)
    print (msg)


def push_msg(token, msg):
    url = 'https://fcm.googleapis.com/fcm/send'
    payload = '{\n    "to" : "' + token + '","priority" : "high","notification": {\t  "body" : "'+msg+'","title" : "shuttle tayo", "sound":"default", "color":"#0066ff"},\t"time_to_live": 4}'
    headers = {'authorization': 'key=AAAAFt1BOGQ:APA91bEHypaznqDJeVzBcRuyBcqjtNDbIK-POYriP5w4_uW9exqHf9zKyS-nZJkNIFQbVvcceLx6JK1gQcXOY8NqjvGqIwZXhe2kaNq4Qq4l2rTOA-r9fYggMImvwKHEPiEfytrfwboy','content-type': 'application/json'}
    try:
        response = requests.request('POST', url, data=payload,headers=headers)
        msg = response.text
    except StudentInfo.DoesNotExist:
        msg = ''
        return getResponse(debug, 400, msg)

def push_msg_android(token, msg):
    url = 'https://fcm.googleapis.com/fcm/send'
    payload = '{\n    "to" : "' + token + '","priority" : "high","notification": {\t  "body" : "'+msg+'","title" : "shuttle tayo", "sound":"default", "color":"#0066ff"},\t"time_to_live": 4}'
    headers = {'authorization': 'key=AAAAFt1BOGQ:APA91bEHypaznqDJeVzBcRuyBcqjtNDbIK-POYriP5w4_uW9exqHf9zKyS-nZJkNIFQbVvcceLx6JK1gQcXOY8NqjvGqIwZXhe2kaNq4Qq4l2rTOA-r9fYggMImvwKHEPiEfytrfwboy','content-type': 'application/json'}
    try:
        response = requests.request('POST', url, data=payload,headers=headers)
        msg = response.text
    except StudentInfo.DoesNotExist:
        msg = ''
        return getResponse(debug, 400, msg)

def push_msg_ios(token, msg):
    url = 'https://fcm.googleapis.com/fcm/send'
    payload = '{\n    "to" : "' + token + '","priority" : "high","notification": {\t  "body" : "'+msg+'","title" : "shuttle tayo", "sound":"default", "color":"#0066ff"},\t"time_to_live": 4}'
    headers = {'authorization': 'key=AAAAFt1BOGQ:APA91bEHypaznqDJeVzBcRuyBcqjtNDbIK-POYriP5w4_uW9exqHf9zKyS-nZJkNIFQbVvcceLx6JK1gQcXOY8NqjvGqIwZXhe2kaNq4Qq4l2rTOA-r9fYggMImvwKHEPiEfytrfwboy','content-type': 'application/json'}
    try:
        response = requests.request('POST', url, data=payload,headers=headers)
        msg = response.text
    except StudentInfo.DoesNotExist:
        msg = ''
        return getResponse(debug, 400, msg)


# def find():
# 	t = timeToDate()
# 	d = t.timeToD()
# 	studentset = set()
# 	scheduletables = list()
# 	inventory_ids = list()
#
# 	inventories = Inventory.objects.filter(day=d) #금일에 해당하는 inventory object
# 	for inventory in inventories:
# 		inventory_ids.append(inventory.id) # inventory id 를 inventory_ids 에 추가
#         # print("inven")
#         # print (inventory_ids)
#         scheduletables = ScheduleTable.objects.filter(iid_id = inventory.id).order_by('time')
#         for scheduletable in scheduletables:
#
#             if len(scheduletable.slist) > 0:
#                 for sid in scheduletable.slist:
#                     stuInfo = StudentInfo.objects.get(id = sid)
#                     stuInfo.personinfo.pin_number
#                     person = PersonalInfo.objects.get(id = stuInfo.personinfo_id)
#                     pin = person.pin_number
#                     print (pin)
#                     check(pin)

def oper_today_schedule():
    t = timeToDate()
    d = t.timeToD()
    msg = ""
    scheduleTables = []

    inven = Inventory.objects.filter(day = d).prefetch_related('scheduletables')
    for i in inven:
        scheduleTables.extend(i.scheduletables.all())

    count_slist = []
    for s in scheduleTables:
        if len(s.slist) >= 1:
            count_slist.extend(s.slist)

    dict_slist = dict(Counter(count_slist))

    push_content = []


    for key, value in dict_slist.iteritems():
        for s in scheduleTables:
            if len(s.slist) >= 1:
                while(key in s.slist):
                    sInfo = StudentInfo.objects.get(id=key)
                    pin = PersonalInfo.objects.get(id = sInfo.personinfo_id)
                    module_push_content = {}

                    module_push_content['time'] = s.time
                    module_push_content['addr'] = s.addr
                    module_push_content['aname'] = sInfo.aname
                    module_push_content['pin'] = pin.pin_number
                    module_push_content['sid'] = key
                    module_push_content['count'] = value

                    push_content.append(module_push_content)


                    if module_push_content['count'] == '1':
                        msg += "오늘 " + module_push_content['aname'] + "등원을 위한 " + module_push_content['time'] + "[" + module_push_content['addr'] + "] 스케줄이 있습니다"
                        nn(module_push_content['pin'], msg)

                    else:
                        msg += "오늘 " + module_push_content['aname'] + "등원을 위한 " + module_push_content['time'] + "[" + module_push_content['addr'] + "] 승차 외 "+module_push_content['count']+" 스케줄이 있습니다"
                        nn(module_push_content['pin'], msg)







                    break

def nn(pin, msg):
    print (pin+":")
    print msg.decode('utf-8').encode('utf-8')

def nts(pin, msg):
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
