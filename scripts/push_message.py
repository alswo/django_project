#!/usr/bin/python
# -*- coding: utf-8 -*-

from passenger.models import StudentInfo, PersonalInfo
from passenger.dateSchedule import timeToDate
from fcmdev.models import PropOfDevice
from fcm_django.models import FCMDevice
from schedule.models import Inventory, ScheduleTable

from collections import Counter
import sys
import requests
import simplejson
import ast
import chardet

reload(sys)
sys.setdefaultencoding('utf-8')

def getResponse(debug, code, msg):
	if (debug == 1):
		return HttpResponse(msg)
	else:
		return JsonResponse({'code': code, 'msg': msg})


def run():
    time = timeToDate()
    date = time.timeToD()

    scheduleTables = []
    schedules = []
    inventorys = Inventory.objects.filter(day = date).prefetch_related('scheduletables').reverse()
    for inventory in inventorys:
        scheduletables = ScheduleTable.objects.filter(iid = inventory.id)
        for scheduletable in scheduletables:
            schedules.extend(scheduletable.slist)

    for inventory in inventorys:
        scheduleTables.extend(inventory.scheduletables.all())

    count_slist = []

    for schTable in scheduleTables:
        if len(schTable.slist) >= 1:
            count_slist.extend(schTable.slist)

    dict_slist = dict(Counter(count_slist))

    push_content = []

    msg_count = 0
    error_count = 0
    for key, value in dict_slist.iteritems():
        for schTable in scheduleTables:
            if len(schTable.slist) >= 1:
                while(key in schTable.slist):
                    try:
                        sInfo = StudentInfo.objects.get(id=key)
                    except StudentInfo.DoesNotExist:
                        sInfo = None
                        break
                    else:

                        pin = PersonalInfo.objects.get(id = sInfo.personinfo_id)
                        module_push_content = {}
                        module_push_content['sname'] = sInfo.sname
                        module_push_content['time'] = schTable.time
                        module_push_content['addr'] = schTable.addr
			module_push_content['lflag'] = schTable.lflag
                        module_push_content['aname'] = sInfo.aid.name
                        module_push_content['pin'] = pin.pin_number
                        module_push_content['sid'] = key
                        module_push_content['count'] = value
                        push_content.append(module_push_content)
                        break

        count = module_push_content['count']-1
	lflag = module_push_content['lflag']
	sname = module_push_content['sname']

	if lflag == 0:
            flag = "하원을 위한"

	elif lflag == 1:
	    flag = "등원을 위한"
	else:
	    flag = "에 대한"
        if count == 0:
            msg = "오늘 " + sname + " 학생의 " + module_push_content['aname'] + " " + flag + " " + module_push_content['time'] + " [" + module_push_content['addr'] + "] 승차 스케줄이 있습니다"
            send_msg(module_push_content['sid'], module_push_content['pin'], msg)
        else:
            msg = "오늘 " + sname + " 학생의 " + module_push_content['aname'] + " 등원을 위한 " + module_push_content['time'] + " [" + module_push_content['addr'] + "]승차 외" + str(count) + "건의 스케줄이 있습니다."
            send_msg(module_push_content['sid'], module_push_content['pin'], msg)



def send_msg(sid, pin, msg):
    url = 'https://fcm.googleapis.com/fcm/send'
    header = {'authorization': 'key=AAAAWVvmwNU:APA91bH0IjidQtMmX6q9SRVekZqzNmWKRR15mdjOFFAt05v3E7PziYRb7sLMbtCtNXZYyKrz--fKvoZdDY94yjOrH9G6z-axN7qWS7H5VMBRUy8Z6-dysdj9ZaCYrESl2wnIfOoSnh7X','content-type': 'application/json'}
    result = {}

    prop = PropOfDevice.objects.filter(pin_number = pin)
    for p in prop:
        pushcheck = p.receivePush
        fcm = FCMDevice.objects.filter(device_id = p.device_id)
        for f in fcm:
            token = f.registration_id
            types = f.type

            if pushcheck == False:
                print ("he/she doesn't want to receive push message.")
            else:
                if types == 'android':
                    payload = '{\n    "to" : "' + str(token) + '","priority" : "high", "content-available" : "true","collapse_key" : "Updates Available" ,"notification": {\t  "body" : "'+str(msg)+'","title" : "셔틀타요", "sound":"default"},\t}'
                elif types == 'ios':
                    payload = '{\n    "to" : "' + str(token) + '","priority" : "high", "content-available" : "true","collapse_key" : "Updates Available" ,"notification": {\t  "body" : "'+str(msg)+'", "sound":"default"},\t}'
                try:
                    sid = str(sid)
                    response = requests.request('POST', url, data=payload, headers=header)
                    try:
                        result = ast.literal_eval(response.text)
                        status = str(result['success'])
                        pushurl = 'http://mj.edticket.com/fcmdev/pushConfirmInfo'
                        data = "pin="+pin+"&confirming="+response.text+"&status="+status+"&token="+token+"&sid="+sid
                        headers = {'content-type': "application/x-www-form-urlencoded"}
                        response = requests.request("POST", pushurl, data=data, headers=headers)
                    except:
                        print "msg check error"
                except:
                    print ("msg send error")
