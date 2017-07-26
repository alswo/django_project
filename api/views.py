# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from schedule.models import RealtimeLocation, Inventory, ScheduleTable
from passenger.models import StudentInfo
from passenger.dateSchedule import timeToDate
from api.models import Notice
import json

## time format : HH:MM
def get_difference(time1, time2):
    timevar1 = time1.split(':')
    timevar2 = time2.split(':')

    return int(timevar2[0]) * 60 + int(timevar2[1]) - (int(timevar1[0]) * 60 + int(timevar1[1]))

def format_hm(time):
    return (time[:2] + ':' + time[2:])

def getResponse(debug, code, msg):
	if (debug == 1):
		return HttpResponse(msg)
	else:
		return JsonResponse({'code': code, 'msg': msg})

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
		return getResponse(debug, 401, msg)
        else:
 		msg = "파라미터가 유효하지 않습니다."
		return getResponse(debug, 400, msg)

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
	    return getResponse(debug, 204, msg)

        ## 마지막 스케쥴도 지났으면 (desc order 인 것 주의)
	inventory = Inventory.objects.get(id = scheduletables.first().iid_id)
        if (inventory.etime < rawhm):
	    carnum = inventory.carnum
	    msg = str(carnum) + "호차 셔틀버스의 운행 스케쥴이 종료되었습니다."
	    return getResponse(debug, 203, msg)

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
			return getResponse(debug, 201, msg)

		    msg = str(carnum) + "호차가"  + str(waittime) + "분 후 도착합니다."
		    return getResponse(debug, 200, msg)
                ## 다음 inventory 로..
                else:
                    continue
            ## inventory 사이에..
            else:
		carnum = inventory.carnum
		if (rawhm - inventory.etime < 10):
		    msg = str(carnum) + "호차 셔틀버스의 운행 스케쥴이 종료되었습니다."
		    return getResponse(debug, 203, msg)
		else:
		    msg = str(carnum) + "호차가 아직 출발 전입니다."
		    return getResponse(debug, 202, msg)

	carnum = inventory.carnum
	msg = str(carnum) + "호차가 아직 출발 전입니다."
	return getResponse(debug, 202, msg)


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
		return getResponse(debug, 401, msg)
        else:
 		msg = "파라미터가 유효하지 않습니다."
		return getResponse(debug, 400, msg)

        scheduletables = ScheduleTable.objects.filter(slist__contains = [sid]).select_related()

	msg = {}
	msg['schedules'] = {}
        for scheduletable in scheduletables:
		data = {}
		data['time'] = scheduletable.time
		data['addr'] = scheduletable.addr
		data['carnum'] = scheduletable.iid.carnum
		data['inventory_id'] = scheduletable.iid_id
		if scheduletable.lflag == 1:
			data['lflag'] = '등원'
		elif scheduletable.lflag == 0:
			data['lflag'] = '하원'

		if scheduletable.iid.day in msg['schedules'].keys():
			pass
		else:
			msg['schedules'][scheduletable.iid.day] = list()

		msg['schedules'][scheduletable.iid.day].append(data)


	return JsonResponse(msg)
	#return JsonResponse(json.dumps(msg, ensure_ascii=False), safe=False)

def setScheduleTableToRouteMap(scheduletable, msg, sequence, sid):
	data = {}
	if (scheduletable.lflag == 3):
		data['addr'] = '도착'
	elif (scheduletable.lflag == 2):
		data['addr'] = '출발'
	else:
		data['addr'] = scheduletable.addr
	data['time'] = scheduletable.time
	data['sequence'] = sequence
	if int(sid) in scheduletable.slist:
		data['poi'] = 'ride'
	msg['routemap'].append(data)

def getRouteMap(request):
	sid = request.GET.get('sid')
	inventory_id = request.GET.get('inventory_id')
	debug = request.GET.get('debug')
	if (debug):
		debug = 1
	else:
		debug = 0

	if (sid and len(sid) > 0 and inventory_id and len(inventory_id)):
		try:
			student = StudentInfo.objects.get(id = sid)
		except StudentInfo.DoesNotExist:
			msg = "해당 사용자가 존재하지 않습니다."
			return getResponse(debug, 401, msg)

		try:
			inventory = Inventory.objects.get(id = inventory_id)
		except Inventory.DoesNotExist:
			msg = "해당 inventory가 존재하지 않습니다."
			return getResponse(debug, 401, msg)
	else:
		msg = "파라미터가 유효하지 않습니다."
		return getResponse(debug, 400, msg)

	scheduletables = ScheduleTable.objects.filter(iid_id = inventory_id).order_by('-time')
	msg = {}
	msg['routemap'] = list()

	sequence = 0
	for scheduletable in scheduletables:
		if int(sid) in scheduletable.slist:
			rideSequence = len(scheduletables) - sequence - 1
			break
		sequence += 1

	sequence = 0
	viewsequence = 0
	for scheduletable in scheduletables.order_by('time'):
		if (scheduletable.lflag == 3 or scheduletable.lflag == 2):
			setScheduleTableToRouteMap(scheduletable, msg, viewsequence, sid)
			viewsequence += 1
		elif (sequence > rideSequence - 3 and sequence <= rideSequence):
			setScheduleTableToRouteMap(scheduletable, msg, viewsequence, sid)
			viewsequence += 1
		sequence += 1

	return JsonResponse(msg)

def listNotice(request):
	notices = Notice.objects.all().order_by('datetime')

	msg = {}
	msg['noticelist'] = list()
	for notice in notices:
		data = {}
		data['id'] = notice.id
		data['title'] = notice.title
		#data['date'] = date(timezone.localtime(notice.datetime)).strftime("%Y.%m.%d")
		data['date'] = timezone.localtime(notice.datetime).strftime("%Y.%m.%d")

		msg['noticelist'].append(data)

	return JsonResponse(msg)

def getNotice(request):
    if request.method == "GET":
	id = request.GET.get('id')
	debug = request.GET.get('debug')
	if (debug):
		debug = 1
	else:
		debug = 0

	if (id and len(id) > 0):
		pass
	else:
		msg = "파라미터가 유효하지 않습니다."
		return getResponse(debug, 400, msg)


	try:
		notice = Notice.objects.get(id = id)
	except Notice.DoesNotExist:
		msg = "해당 게시글이 존재하지 않습니다."
		return getResponse(debug, 401, msg)

	msg = {}
	msg['notice'] = {}
	msg['notice']['title'] = notice.title
	msg['notice']['date'] = timezone.localtime(notice.datetime).strftime("%Y.%m.%d")
	msg['notice']['content'] = notice.content

	return JsonResponse(msg)

def getStudentInfo(request):
    if request.method == "POST":
        pin = request.POST.get('pin')
	
        if (debug):
                debug = 1
        else:
                debug = 0
        
        try:
            sInfo = StudentInfo.objects.get(pin_number = pin)

            studentInfo = {}

            studentInfo['sid'] = sInfo.id
            studentInfo['aid'] = sInfo.aid
            studentInfo['phone'] = sInfo.phone1
            studentInfo['pin'] = sInfo.pin_number
	    studentInfo['grade'] = sInfo.grade
	
	    if sInfo.id == None:
		msg = 'Sid does not exist'
        
	        return getResponse(debug, 401, msg)

	    elif sInfo.aid == None:
                msg = 'Aid does not exist'

		return getResponse(debug, 401, msg)

	    elif sInfo.phone == None:
		msg = 'Phone does not exist'

		return getResponse(debug, 401, msg)
	
	    elif sInfo.grade == None:
                msg = 'Grade does not exist'

		return getRespone(debug, 401, msg)

            return JsonResponse(studentInfo)

        except Exception as e:
            
            msg = 'PIN does not register' 
	    return HttpResponse(debug,400,msg)
