# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from schedule.models import RealtimeLocation, Inventory, ScheduleTable
from passenger.models import StudentInfo
from passenger.dateSchedule import timeToDate
import json

## time format : HH:MM
def get_difference(time1, time2):
    timevar1 = time1.split(':')
    timevar2 = time2.split(':')

    return int(timevar2[0]) * 60 + int(timevar2[1]) - (int(timevar1[0]) * 60 + int(timevar1[1]))

def format_hm(time):
    return (time[:2] + ':' + time[2:])

# Create your views here.
def getRealtimeLocation(request):
    if request.method == "GET":
	max_diff = 10
        t = timeToDate()
        d = t.timeToD()
        today = t.timeToYmd()
        rawhm = t.timeToRawHM()
        hm = t.timeToHM()
        sid = request.GET.get('sid')
        carnum = -1
        iid = ""
        siid = ""
	sname = ""
	msg = ""
	debug = request.GET.get('debug')
	if (debug):
		debug = 1
	else:
		debug = 0

        if (sid and len(sid) > 0):
	    try:
            	student = StudentInfo.objects.get(id = sid)
		sname = student.sname
	    except StudentInfo.DoesNotExist:
		msg = "해당 사용자가 존재하지 않습니다."
		if (debug == 1):
                	return HttpResponse(msg)
		else:
			return JsonResponse({'code': 401, 'msg': msg})
        else:
 		msg = "파라미터가 유효하지 않습니다."
		if (debug == 1):
                	return HttpResponse(msg)
		else:
			return JsonResponse({'code': 400, 'msg': msg})

	if (debug == 1):
        	rawhm = int(request.GET.get('rawhm'))
        	hm = request.GET.get('hm')
		today = request.GET.get('today')
		d = request.GET.get('d')

        today_inventories = Inventory.objects.filter(day=d)
        today_inventory_ids = today_inventories.values('id')
        scheduletables = ScheduleTable.objects.filter(iid_id__in = today_inventory_ids).filter(slist__contains = [sid]).order_by('-time')
        if (len(scheduletables) <= 0):
	    msg = sname + "님은 오늘 스케쥴이 없습니다."
	    if (debug == 1):
            	return HttpResponse(msg)
	    else:
            	return JsonResponse({'code': 204, 'msg': msg})

        ## 마지막 스케쥴도 지났으면 (desc order 인 것 주의)
	inventory = Inventory.objects.get(id = scheduletables.first().iid_id)
        if (inventory.etime < rawhm):
	    carnum = inventory.carnum
	    msg = str(carnum) + "호차 셔틀버스의 운행 스케쥴이 종료되었습니다."
	    if (debug == 1):
            	return HttpResponse(msg)
	    else:
		return JsonResponse({'code': 203, 'msg': msg})

        for scheduletable in scheduletables:
            inventory = Inventory.objects.get(id = scheduletable.iid_id)
            format_etime = format_hm(str(inventory.etime))
            if (inventory.etime > rawhm):
                ## inventory 중간에 있으면..
                if (inventory.stime <= rawhm):
                    carnum = inventory.carnum
                    expected_time = scheduletable.time
                    realtimelocations = RealtimeLocation.objects.filter(date=today, carnum=carnum, departure_time__lte=format_etime)
		    if (realtimelocations):
			realtimelocation = realtimelocations.order_by('schedule_time').last()
		    	diff = get_difference(realtimelocation.schedule_time, realtimelocation.departure_time)
		    	if (diff >= max_diff):
				diff = max_diff
                    	waittime = get_difference(hm, expected_time) + diff - 1
		    else:
			waittime = get_difference(hm, expected_time)

		    if (waittime < 0):
			msg = str(carnum) + "호차가 출발했습니다."
			if (debug == 1):
				return HttpResponse(msg)
			else:
				return JsonResponse({'code': 201, 'msg': msg})

		    msg = str(carnum) + "호차가"  + str(waittime) + "분 후 도착합니다."
		    if (debug == 1):
                    	return HttpResponse(msg)
		    else:
			return JsonResponse({'code': 200, 'msg': msg})
                ## 다음 inventory 로..
                else:
                    continue
            ## inventory 사이에..
            else:
		carnum = inventory.carnum
		if (rawhm - inventory.etime < 10):
		    msg = str(carnum) + "호차 셔틀버스의 운행 스케쥴이 종료되었습니다."
		    if (debug == 1):
                    	return HttpResponse(msg)
		    else:
			return JsonResponse({'code': 203, 'msg': msg})
		else:
		    msg = str(carnum) + "호차가 아직 출발 전입니다."
		    if (debug == 1):
                    	return HttpResponse(msg)
		    else:
			return JsonResponse({'code': 202, 'msg': msg})

	carnum = inventory.carnum
	msg = str(carnum) + "호차가 아직 출발 전입니다."
	if (debug == 1):
        	return HttpResponse(msg)
	else:
		return JsonResponse({'code': 202, 'msg': msg})


def getSchedulesForStudent(request):
    if request.method == "GET":
	max_diff = 10
        t = timeToDate()
        d = t.timeToD()
        today = t.timeToYmd()
        rawhm = t.timeToRawHM()
        hm = t.timeToHM()
        sid = request.GET.get('sid')
        carnum = -1
        iid = ""
        siid = ""
	sname = ""
	msg = ""
	debug = request.GET.get('debug')
	if (debug):
		debug = 1
	else:
		debug = 0

        if (sid and len(sid) > 0):
	    try:
            	student = StudentInfo.objects.get(id = sid)
		sname = student.sname
	    except StudentInfo.DoesNotExist:
		msg = "해당 사용자가 존재하지 않습니다."
		if (debug == 1):
                	return HttpResponse(msg)
		else:
			return JsonResponse({'code': 401, 'msg': msg})
        else:
 		msg = "파라미터가 유효하지 않습니다."
		if (debug == 1):
                	return HttpResponse(msg)
		else:
			return JsonResponse({'code': 400, 'msg': msg})

        scheduletables = ScheduleTable.objects.filter(slist__contains = [sid]).select_related()

	msg = {}
	msg['schedules'] = {} 
        for scheduletable in scheduletables:
		data = {}
		data['time'] = scheduletable.time
		data['addr'] = scheduletable.addr
		data['carnum'] = scheduletable.iid.carnum
		if scheduletable.lflag == 1:
			data['lflag'] = '등원'
		else:
			data['lflag'] = '하원'

		if scheduletable.iid.day in msg['schedules'].keys():
			pass
		else:
			msg['schedules'][scheduletable.iid.day] = list()

		msg['schedules'][scheduletable.iid.day].append(data)


	return JsonResponse(msg)
	#return JsonResponse(json.dumps(msg, ensure_ascii=False), safe=False)
		
