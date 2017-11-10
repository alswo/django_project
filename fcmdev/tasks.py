#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tayo.celery import app
from passenger.models import StudentInfo, PersonalInfo
from passenger.dateSchedule import timeToDate
from fcmdev.models import PropOfDevice, PushConfirming, PushMonitoring
from fcm_django.models import FCMDevice
from schedule.models import Inventory, ScheduleTable
from collections import Counter
import sys
import requests
import simplejson
import ast
import datetime
import socket

reload(sys)
sys.setdefaultencoding('utf-8')

def getResponse(debug, code, msg):
	if (debug == 1):
		return HttpResponse(msg)
	else:
		return JsonResponse({'code': code, 'msg': msg})


@app.task
def today_schedule_notification():
    if socket.gethostbyname(socket.gethostname()) == '172.31.2.185':
        fcmdevice =  FCMDevice.objects.all()
        device_count=0
        day = datetime.datetime.now()
        today = day.strftime('%Y-%m-%d')
        msg_count= 0
        push_num = 0
        push_false_num = 0
        total_msg = 0
        refuse_user = 0

        time = timeToDate()
        date = time.timeToD()
        si = []
        scheduleTables = []
        schedules = []
        slist_list = []
        tflag_list = []
        dict_s ={}
        inventorys = Inventory.objects.filter(day = date).prefetch_related('scheduletables').reverse()
        for inventory in inventorys:
            scheduletables = ScheduleTable.objects.filter(iid = inventory.id)
            for scheduletable in scheduletables:
			    if len(scheduletable.slist) == len(scheduletable.tflag):
           		        schedules.extend(scheduletable.slist)
	    	 	        slist_list.extend(scheduletable.slist)
            		        tflag_list.extend(scheduletable.tflag)

        for s in slist_list:
            try:
                t =  slist_list.index(s)
            except:
                t = None
            else:
                if dict_s.has_key(s):
                    dict_s[s] += int(tflag_list[t])
                    slist_list[t] = []
                else:
                    dict_s[s] = int(tflag_list[t])
		    slist_list[t] = []

        for inventory in inventorys:
            scheduleTables.extend(inventory.scheduletables.all())

        count_slist = []

        for schTable in scheduleTables:
            if len(schTable.slist) >= 1:
                count_slist.extend(schTable.slist)

        dict_slist = dict(Counter(count_slist))

        push_content = []

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
			    try:
				    pin = PersonalInfo.objects.get(id = sInfo.personinfo_id)
	                            module_push_content = {}
				    module_push_content['personinfoid'] = sInfo.personinfo_id
	                            module_push_content['sname'] = sInfo.sname
	                            module_push_content['time'] = schTable.time
	                            module_push_content['addr'] = schTable.addr
		                    module_push_content['lflag'] = schTable.lflag
	                            module_push_content['aname'] = sInfo.aid.name
	                            module_push_content['pin'] = pin.pin_number
	                            module_push_content['sid'] = key
	                            module_push_content['count'] = value
				    module_push_content['sid'] = sInfo.id
	                            push_content.append(module_push_content)
	                            break
			    except PersonalInfo.DoesNotExist:
			            break
            if module_push_content['personinfoid'] != 'None':

                total_msg += 1
	        pin_prop = PropOfDevice.objects.filter(pin_number = module_push_content['pin'])

                for p in pin_prop:
                    msg_count+= 1
                    if p.receivePush == False:
                        refuse_user += 1

                count = module_push_content['count']-1
	        lflag = module_push_content['lflag']
	        sname = module_push_content['sname']
	        sid = module_push_content['sid']


	        if dict_s.has_key(sid):
		        tflag_count = dict_s[sid]
	        else:
		        tflag_count = 0

	        if lflag == 0:
                    flag = "하원을 위한"

	        elif lflag == 1:
	            flag = "등원을 위한"
	        else:
	            flag = "에 대한"
                if count == 0:
                    msg = "오늘 " + sname + " 학생의 " + module_push_content['aname'] + " " + flag + " " + module_push_content['time'] + " [" + module_push_content['addr'] + "] 승차 스케줄이 있습니다"
	            if tflag_count > 0:
		        cancel_msg=  "[승차취소]오늘 " + sname + " 학생의 " + module_push_content['aname'] + " " + flag + " " + module_push_content['time'] + " [" + module_push_content['addr'] + "] 승차 스케줄을 취소하셨습니다."
		        send_msg(module_push_content['sid'], module_push_content['pin'], cancel_msg)
                        module_push_content['personinfoid'] = 'None'
	            else:
		        send_msg(module_push_content['sid'], module_push_content['pin'], msg)
			module_push_content['personinfoid'] = 'None'
                else:
                    msg = "오늘 " + sname + " 학생의 " + module_push_content['aname'] + " " + flag + " " + module_push_content['time'] + " [" + module_push_content['addr'] + "]승차 외" + str(count) + "건의 스케줄이 있습니다."
	            if tflag_count > 0:
		        cancel_msg = "오늘 " + sname + " 학생의 " + module_push_content['aname'] + " " + flag + " " + module_push_content['time'] + " [" + module_push_content['addr'] + "]승차 외" + str(tflag_count) + "건의 취소된 스케줄이 있습니다."
		        send_msg(module_push_content['sid'], module_push_content['pin'], cancel_msg)
			module_push_content['personinfoid'] = 'None'
	            else:
		        send_msg(module_push_content['sid'], module_push_content['pin'], msg)
			module_push_content['personinfoid'] = 'None'
        for fcmdevices in fcmdevice:
		    device_count +=1
        pushconf = PushConfirming.objects.filter(date__icontains = today)
        for pushconfs in pushconf:
	    push_num += 1
            if pushconfs.status == False:
	        push_false_num += 1
        pm = PushMonitoring.objects.create(date= today, total_S= device_count,expec_push=total_msg, expec_push_s=msg_count, push_num=push_num, false_num= push_false_num, refuse_user =  refuse_user)
        pm.save()
    else:
        print "not this server"


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
                        pushurl = 'http://api.edticket.com/fcmdev/pushConfirmInfo'
                        data = "pin="+pin+"&confirming="+response.text+"&status="+status+"&token="+token+"&sid="+sid
                        headers = {'content-type': "application/x-www-form-urlencoded"}
                        response = requests.request("POST", pushurl, data=data, headers=headers)
		    except:
                        print "msg check error"
		except:
                    print "msg send error"
