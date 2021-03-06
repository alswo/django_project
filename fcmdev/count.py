#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tayo.celery import app
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

def getResponse(debug, code, msg):
	if (debug == 1):
		return HttpResponse(msg)
	else:
		return JsonResponse({'code': code, 'msg': msg})


@app.task
def today_schedule_notification():
   msg_count= 0
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

        pin_prop = PropOfDevice.objects.filter(pin_number = module_push_content['pin'])
        for p in pin_prop:
           msg_count+= 1
            if p.receivePush == False:
                print p.pin_number

    print msg_count
