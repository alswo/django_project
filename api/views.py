# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from schedule.models import RealtimeLocation, Inventory, ScheduleTable
from passenger.models import StudentInfo, Academy
from passenger.dateSchedule import timeToDate
from api.models import Notice
import json
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta

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

def authPinNumber(sid, pin_number):
	if sid == None or pin_number == None:
		return False

	try:
		if (pin_number == StudentInfo.objects.get(id=sid).personinfo.pin_number):
			return True
	except:
		return False

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

def makeTimeStr(inttime):
        timestr = "%04d" % inttime
        return timestr[:2] + ":" + timestr[2:]

def getSchedulesForStudent(request):
    if request.method == "GET":
	max_diff = 10
        t = timeToDate()
        d = t.timeToD()
        today = t.timeToYmd()
        rawhm = t.timeToRawHM()
        hm = t.timeToHM()
	startdayOfWeek = t.timeToStartDayOfWeek()

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
	daydictionary = {u'월':'mon', u'화':'tue', u'수':'wed', u'목':'thu', u'금':'fri', u'토':'sat', u'일':'sun'}
	daylist = [u'월', u'화', u'수', u'목', u'금', u'토', u'일']

	for day in daylist:
		msg['schedules'][daydictionary[day]] = {}
		msg['schedules'][daydictionary[day]]['list'] = list()
		msg['schedules'][daydictionary[day]]['date'] = (startdayOfWeek + timedelta(days=daylist.index(day))).strftime("%Y.%m.%d")
		if d == day :
			msg['schedules'][daydictionary[day]]['today'] = True
		else:
			msg['schedules'][daydictionary[day]]['today'] = False

	for scheduletable in scheduletables:
		data = {}
		data['time'] = scheduletable.time
		data['addr'] = scheduletable.addr
		data['carnum'] = scheduletable.iid.carnum
		data['inventory_id'] = scheduletable.iid_id
		data['start_time'] = makeTimeStr(scheduletable.iid.stime)
		data['end_time'] = makeTimeStr(scheduletable.iid.etime)
		#data['institute_name'] = list(map(lambda x: (Academy.objects.get(id=x)).name, (set(scheduletable.iid.alist) & set(student.aid))))
		data['institute_name'] = Academy.objects.get(id=student.aid_id).name
		data['scheduletable_id'] = scheduletable.id
		if scheduletable.lflag == 1:
			data['lflag'] = '등원'
		elif scheduletable.lflag == 0:
			data['lflag'] = '하원'

		#if scheduletable.iid.day in msg['schedules'].keys():
			#pass
		#else:
			#msg['schedules'][daydictionary[scheduletable.iid.day]] = {}
			#msg['schedules'][daydictionary[scheduletable.iid.day]]['list'] = list()
			#msg['schedules'][daydictionary[scheduletable.iid.day]]['date'] = (startdayOfWeek + timedelta(days=daylist.index(scheduletable.iid.day))).strftime("%Y.%m.%d")
			#if d == scheduletable.iid.day :
				#msg['schedules'][daydictionary[scheduletable.iid.day]]['today'] = True
			#else:
				#msg['schedules'][daydictionary[scheduletable.iid.day]]['today'] = False

		msg['schedules'][daydictionary[scheduletable.iid.day]]['list'].append(data)

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

@csrf_exempt
def getStudentInfo(request):
    if request.method == "POST":
        pin_number = request.POST.get('pin_number')

	debug = 0

        try:
            sInfo = StudentInfo.objects.get(pin_number = pin_number)
            
            studentInfo = {}

            studentInfo['sid'] = sInfo.id
            studentInfo['aid'] = sInfo.aid_id
            studentInfo['phone'] = sInfo.phone1
            studentInfo['pin'] = sInfo.pin_number
	    studentInfo['grade'] = sInfo.grade

            return JsonResponse(studentInfo)

        except:

            msg = 'PIN does not exist'

            return getResponse(debug,400,msg)

def todayLoad(request):
    if request.method == "GET":
        sid = request.GET.get('sid')
        sTableId = request.GET.get('sTableId')
        iId = request.GET.get('iId')

        stable = ScheduleTable.objects.get(id = sTableId)

        offset_list = stable.slist
        offset = offset_list.index(sid)
        
        temp_tflag = stable.tflag
        temp_index = offset

        if temp_tflag[temp_index] == 0:
            temp_tflag[temp_index] = 1
            button_flag = 0

        elif temp_tflag[temp_index] == 1:
            temp_tflag[temp_index] = 0
            button_flag = 1

        stable.tflag = temp_tflag
        stable.save()

        return HttpResponse(button_flag)


