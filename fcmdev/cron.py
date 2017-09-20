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

reload(sys)
sys.setdefaultencoding('utf-8')

def today_schedule():
    time = timeToDate()
    date = time.timeToD()

    scheduleTables = []

    inventorys = Inventory.objects.filter(day = date).prefetch_related('scheduletables').reverse()

    for inven in inventorys:
        scheduleTables.extend(inven.scheduletables.all()) #금일 에 해당하는 모든 인벤토리 객체를 scheduleTables 로..

    count_slist = []
    for schTable in scheduleTables:
        if len(schTable.slist) >= 1:
            count_slist.extend(schTable.slist)

    dict_slist = dict(Counter(count_slist))

    push_content = []

    i = 0
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
                    module_push_content['sname'] = s.sname
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

def push_msg(sid, pin, msg):
    url = 'https://fcm.googleapis.com/fcm/send'
    badgeCount = 0
    badgeCount += 1
    stuinfo = StudentInfo.objects.get(id = sid)
    sname = stuinfo.sname

    headers = {'authorization': 'key=AAAAWVvmwNU:APA91bH0IjidQtMmX6q9SRVekZqzNmWKRR15mdjOFFAt05v3E7PziYRb7sLMbtCtNXZYyKrz--fKvoZdDY94yjOrH9G6z-axN7qWS7H5VMBRUy8Z6-dysdj9ZaCYrESl2wnIfOoSnh7X','content-type': 'application/json'}
    prop = PropOfDevice.objects.filter(pin_number = pin)
    for p in prop:
        fcm = FCMDevice.objects.filter(device_id = p.device_id)
        for f in fcm:
            token = f.registration_id
            types = f.type
            if types == 'android':
                payload = '{\n    "to" : "' + token + '","priority" : "high", "content-available" : "true","collapse_key" : "Updates Available" ,"notification": {\t  "body" : "'+msg+'","title" : "shuttle tayo", "sound":"default", "color":"#0066ff"},\t}'
            elif types == 'ios':

                payload = '{\n    "to" : "' + token + '","badge" : "'+badgeCount.toString()+'","priority" : "high", "content-available" : "true","collapse_key" : "Updates Available" ,"notification": {\t  "body" : "'+msg+'","title" : "shuttle tayo", "sound":"default", "color":"#0066ff"},\t}'

            try:
                response = requests.request('POST', url, data=payload,headers=headers)
                msg = response.text
            except:
                msg = ''
                return getResponse(debug, 400, msg)


def getResponse(debug, code, msg):
	if (debug == 1):
		return HttpResponse(msg)
	else:
		return JsonResponse({'code': code, 'msg': msg})


# 90% 완성?
def test():
    time = timeToDate()
    date = time.timeToD()

    scheduleTables = []
    schedules = []
    inventorys = Inventory.objects.filter(day = '화').prefetch_related('scheduletables').reverse()
    for inventory in inventorys:
        scheduletables = ScheduleTable.objects.filter(iid = inventory.id)
        for scheduletable in scheduletables:
            schedules.extend(scheduletable.slist)
    #print (len(set(schedules)))
    for inventory in inventorys:
        scheduleTables.extend(inventory.scheduletables.all()) #금일 에 해당하는 모든 인벤토리 객체를 scheduleTables 로..

    #print ("++++"+str(len(set(scheduleTables))))
    count_slist = []

    for schTable in scheduleTables:
        if len(schTable.slist) >= 1:
            count_slist.extend(schTable.slist) #

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
                        print ("-------------------"+str(sInfo.id))
                        error_count += 1
                        sInfo = None
                        break
                    else:

                        pin = PersonalInfo.objects.get(id = sInfo.personinfo_id)
                        module_push_content = {}
                        module_push_content['time'] = schTable.time
                        module_push_content['addr'] = schTable.addr
                        module_push_content['aname'] = sInfo.aname
                        module_push_content['pin'] = pin.pin_number
                        module_push_content['sid'] = key
                        module_push_content['count'] = value
                        push_content.append(module_push_content)
                        break

        count = module_push_content['count']-1
        if count == 0:
            msg_count += 1
            msg = "오늘 " + module_push_content['aname'] + " 등원을 위한 " + module_push_content['time'] + " [" + module_push_content['addr'] + "] 승차 스케줄이 있습니다"
            #msg = msg.decode('utf-8').encode('utf-8')
            msg_test(module_push_content['pin'], msg)
        else:
            msg_count += 1
            msg = "오늘 " + module_push_content['aname'] + " 등원을 위한 " + module_push_content['time'] + " [" + module_push_content['addr'] + "]승차 외" + str(count) + "건의 스케줄이 있습니다."
            #msg = msg.decode('utf-8').encode('utf-8')
            msg_test(module_push_content['pin'], msg)
    print ("call"+ str(msg_count) +"error"+ str(error_count))



def msg_test(pin, msg):
    prop = PropOfDevice.objects.filter(pin_number = pin)
    for p in prop:
        pushcheck = p.receivePush
        fcm = FCMDevice.objects.filter(device_id = p.device_id)
        for f in fcm:
            token = f.registration_id
            types = f.type
            send(pushcheck, pin, token, msg, types)


# def send(True, 'tUP3Ebh', 'dHKukmKTKsA:APA91bEpQzGdZA5xMAKV5rraIruTGfkmKd9tHfJzBWcZIvUjAt2ZVQcJ76ywlvrpsMpt8ghqh3llGhkiJxccXBAib4qRccJVp7JJs4Wj1HLPGH3kKAdO00SzibptgCrscXu9WD5s73TI', 'testest', 'ios'):
def send(pushcheck, pin, token, msg, types):
    print ("send"+msg)
    url = 'https://fcm.googleapis.com/fcm/send'
    header = {'authorization': 'key=AAAAWVvmwNU:APA91bH0IjidQtMmX6q9SRVekZqzNmWKRR15mdjOFFAt05v3E7PziYRb7sLMbtCtNXZYyKrz--fKvoZdDY94yjOrH9G6z-axN7qWS7H5VMBRUy8Z6-dysdj9ZaCYrESl2wnIfOoSnh7X','content-type': 'application/json'}
    result = {}
    if pushcheck == False:
        print ("he/she doesn't want to receive push message.")
    else:
        if types == 'android':
            payload = '{\n    "to" : "' + token + '","priority" : "high", "content-available" : "true","collapse_key" : "Updates Available" ,"notification": {\t  "body" : "'+msg+'","title" : "shuttle tayo", "sound":"default", "color":"#0066ff"},\t}'
        elif types == 'ios':
            payload = '{\n    "to" : "' + token + '","priority" : "high", "content-available" : "true","collapse_key" : "Updates Available" ,"notification": {\t  "body" : "'+msg+'", "sound":"default", "color":"#0066ff"},\t}'
        try:
            response = requests.request('POST', url, data=payload, headers=header)
            print reponse.text
            # try:
            #     result = ast.literal_eval(response.text)
            #     status = str(result['success'])
            #     pushurl = 'http://mj.edticket.com/fcmdev/pushConfirmInfo'
            #     data = "pin="+pin+"&confirming="+result+"&status="+status+"&token="+token
            #     headers = {'content-type': "application/x-www-form-urlencoded"}
            #     response = requests.request("POST", pushurl, data=data, headers=headers)
            # except:
            #     print "msg check error"
        except:
            print ("msg send error")


def notice_to_slack(sid, msg):
    studentinfo = StudentInfo.objects.get(id = sid)
    name = studentinfo.sname
    name = ""
    print (name)
    try:
        studentinfo = StudentInfo.objects.get(id = sid)
        name = studentinfo.sname
        data = {
        'text': name + "\n" + msg ,
        }
        r = requests.post("https://hooks.slack.com/services/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", json=data)
    except StudentInfo.DoesNotExist:
        name = "none"
