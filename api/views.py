# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from schedule.models import RealtimeLocation, Inventory, ScheduleTable, Car
from passenger.models import StudentInfo, Academy, PersonalInfo
from passenger.dateSchedule import timeToDate
from api.models import Notice, Clauses
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

def getResponse(debug, code, msg, waittime=-1):
	#if (debug == 1):
		#return HttpResponse(msg)
	if (waittime >= 0):
		return JsonResponse({'code': code, 'msg': msg, 'waittime': waittime})
	else:
		return JsonResponse({'code': code, 'msg': msg})

# Create your views here.
def getRealtimeLocationDebug(request):
	if request.method == "GET":
		debug_id = request.GET.get('debug_id')
		if (debug_id == None):
			debug_id = '0'
		msg = ""
		waittime = -1
	
		if (debug_id == '401'):
			msg = "해당 사용자가 존재하지 않습니다."
		elif (debug_id == '400'):
 			msg = "파라미터가 유효하지 않습니다."
		elif (debug_id == '202'):
			msg = "0호차가 아직 출발 전입니다."
		elif (debug_id == '204'):
			msg = "홍유정님은 오늘 스케쥴이 없습니다."
		elif (debug_id == '203'):
			msg = "0호차 셔틀버스의 운행 스케쥴이 종료되었습니다."
		elif (debug_id == '201'):
			msg = "0호차가 출발했습니다."
		elif (debug_id == '200'):
			msg = "0호차가 30분 후 도착합니다."
			waittime = 30

		return getResponse(0, int(debug_id), msg, waittime)

def getRealtimeLocation(request):
    if request.method == "GET":
	max_diff = 10
        t = timeToDate()
        d = t.timeToD()
        today = t.timeToYmd()
        rawhm = int(t.timeToRawHM())
        hm = t.timeToHM()
        sid = request.GET.get('sid')
	inventory_id = request.GET.get('inventory_id')
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

        #today_inventories = Inventory.objects.filter(day=d)
        #today_inventory_ids = today_inventories.values('id')
	if (inventory_id == None):
 		msg = "파라미터가 유효하지 않습니다."
		return getResponse(debug, 400, msg)

	try:
		inventory = Inventory.objects.get(id=int(inventory_id))
	except Inventory.DoesNotExist:
 		msg = "파라미터가 유효하지 않습니다."
		return getResponse(debug, 400, msg)

	if (inventory.day != d):
		msg = str(inventory.carnum) + "호차가 아직 출발 전입니다."
		return getResponse(debug, 202, msg)

        scheduletables = ScheduleTable.objects.filter(iid_id = int(inventory_id)).filter(slist__contains = [sid]).order_by('-time')
        if (len(scheduletables) <= 0):
	    msg = sname + "님은 오늘 스케쥴이 없습니다."
	    return getResponse(debug, 204, msg)

        ## 마지막 스케쥴도 지났으면 (desc order 인 것 주의)
	inventory = Inventory.objects.get(id = scheduletables.first().iid_id)
        if (inventory.etime < rawhm):
	    carnum = inventory.carnum
	    msg = str(carnum) + "호차 셔틀버스의 운행 스케쥴이 종료되었습니다. "
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

		    msg = str(carnum) + "호차가 "  + str(waittime) + "분 후 도착합니다."
		    return getResponse(debug, 200, msg, waittime)
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

def makeHMstr(intTime):
	hr = int(intTime / 60)
	mn = intTime - (hr * 60)
	return "%02d:%02d" % (hr, mn)

def minusHM(strHM, intTime):
	return makeHMstr(int(strHM[:2]) * 60 + int(strHM[3:]) - intTime)

def plusHM(strHM, intTime):
	return makeHMstr(int(strHM[:2]) * 60 + int(strHM[3:]) + intTime)

def experienceGetSchedulesForStudent(request):
        t = timeToDate()
        d = t.timeToD()
	startdayOfWeek = t.timeToStartDayOfWeek()
	#current_time = str(timezone.now())[11:16]
	current_time = t.timeToHM()
	msg = {}
	msg['sid'] = '0000'
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

	# monday
	data = {}
	data['time'] = '15:38'
	data['addr'] = '풍덕천동 대우푸르지오 정거장'
	data['carnum'] = 32
	data['inventory_id'] = 0
	data['start_time'] = '15:25'
	data['end_time'] = '15:55'
	data['institute_name'] = 'ABCD학원'
	data['scheduletable_id'] = 0
	data['driver_telephone'] = '000-0000-0000'
	data['lflag'] = '등원'
	msg['schedules']['mon']['list'].append(data)

	data = {}
	data['time'] = '17:45'
	data['addr'] = '풍덕천동 대우푸르지오 정거장'
	data['carnum'] = 32
	data['inventory_id'] = 0
	data['start_time'] = '17:35'
	data['end_time'] = '18:00'
	data['institute_name'] = 'ABCD학원'
	data['scheduletable_id'] = 0
	data['driver_telephone'] = '000-0000-0000'
	data['lflag'] = '하원'
	msg['schedules']['mon']['list'].append(data)

	# tuesday
	data = {}
	data['time'] = '16:17'
	data['addr'] = '소만 1단지 버스정류장'
	data['carnum'] = 29
	data['inventory_id'] = 0
	data['start_time'] = '16:00'
	data['end_time'] = '16:26'
	data['institute_name'] = 'ABCD학원'
	data['scheduletable_id'] = 0
	data['driver_telephone'] = '000-0000-0000'
	data['lflag'] = '등원'
	msg['schedules']['tue']['list'].append(data)

	data = {}
	data['time'] = '19:18'
	data['addr'] = '소만 1단지 버스정류장'
	data['carnum'] = 29
	data['inventory_id'] = 0
	data['start_time'] = '19:00'
	data['end_time'] = '19:26'
	data['institute_name'] = 'ABCD학원'
	data['scheduletable_id'] = 0
	data['driver_telephone'] = '000-0000-0000'
	data['lflag'] = '하원'
	msg['schedules']['tue']['list'].append(data)

	# wednesday
	data = {}
	data['time'] = '14:00'
	data['addr'] = '서당초등학교 후문 앞'
	data['carnum'] = 20
	data['inventory_id'] = 0
	data['start_time'] = '15:40'
	data['end_time'] = '14:07'
	data['institute_name'] = 'ABCD학원'
	data['scheduletable_id'] = 0
	data['driver_telephone'] = '000-0000-0000'
	data['lflag'] = '등원'
	msg['schedules']['wed']['list'].append(data)

	data = {}
	data['time'] = '16:10'
	data['addr'] = '현대아파트 113동 앞'
	data['carnum'] = 20
	data['inventory_id'] = 0
	data['start_time'] = '16:05'
	data['end_time'] = '16:25'
	data['institute_name'] = 'ABCD학원'
	data['scheduletable_id'] = 0
	data['driver_telephone'] = '000-0000-0000'
	data['lflag'] = '하원'
	msg['schedules']['wed']['list'].append(data)

	# thursday
	data = {}
	data['time'] = '14:40'
	data['addr'] = '위례별초 맞은편'
	data['carnum'] = 13
	data['inventory_id'] = 0
	data['start_time'] = '14:35'
	data['end_time'] = '15:05'
	data['institute_name'] = 'ABCD학원'
	data['scheduletable_id'] = 0
	data['driver_telephone'] = '000-0000-0000'
	data['lflag'] = '등원'
	msg['schedules']['thu']['list'].append(data)

	data = {}
	data['time'] = '16:20'
	data['addr'] = '센트럴푸르지오 정문 새싹정류장'
	data['carnum'] = 32
	data['inventory_id'] = 0
	data['start_time'] = '16:05'
	data['end_time'] = '16:25'
	data['institute_name'] = 'ABCD학원'
	data['scheduletable_id'] = 0
	data['driver_telephone'] = '000-0000-0000'
	data['lflag'] = '하원'
	msg['schedules']['thu']['list'].append(data)

	# friday
	data = {}
	data['time'] = '15:40'
	data['addr'] = '한빛초 병설유치원'
	data['carnum'] = 4
	data['inventory_id'] = 0
	data['start_time'] = '15:25'
	data['end_time'] = '15:55'
	data['institute_name'] = 'ABCD학원'
	data['scheduletable_id'] = 0
	data['driver_telephone'] = '000-0000-0000'
	data['lflag'] = '등원'
	msg['schedules']['fri']['list'].append(data)

	data = {}
	data['time'] = '16:59'
	data['addr'] = '엠코센트로엘 정문'
	data['carnum'] = 4
	data['inventory_id'] = 0
	data['start_time'] = '16:55'
	data['end_time'] = '17:11'
	data['institute_name'] = 'ABCD학원'
	data['scheduletable_id'] = 0
	data['driver_telephone'] = '000-0000-0000'
	data['lflag'] = '하원'
	msg['schedules']['fri']['list'].append(data)

	# today
	msg['schedules'][daydictionary[unicode(d)]]['list'] = list()
	data = {}
	data['time'] = current_time
	data['addr'] = '위례초 정문'
	data['carnum'] = 4
	data['inventory_id'] = 0
	data['start_time'] = minusHM(current_time, 15)
	data['end_time'] = plusHM(current_time, 15)
	data['institute_name'] = 'ABCD학원'
	data['scheduletable_id'] = 0
	data['driver_telephone'] = '000-0000-0000'
	data['lflag'] = '등원'
	msg['schedules'][daydictionary[unicode(d)]]['list'].append(data)

	data = {}
	data['time'] = plusHM(current_time, 120)
	data['addr'] = '롯데캐슬 정문'
	data['carnum'] = 4
	data['inventory_id'] = 0
	data['start_time'] = plusHM(current_time, 105)
	data['end_time'] = plusHM(current_time, 135)
	data['institute_name'] = 'ABCD학원'
	data['scheduletable_id'] = 0
	data['driver_telephone'] = '000-0000-0000'
	data['lflag'] = '하원'
	msg['schedules'][daydictionary[unicode(d)]]['list'].append(data)

	return JsonResponse(msg)

def experienceGetRealtimeLocation(request):
	msg = "4호차가 7분 후 도착합니다."
	return getResponse(0, 200, msg, 7)

def experienceGetRouteMap(request):
        t = timeToDate()
	current_time = t.timeToHM()
	msg = {}
	msg['routemap'] = list()

	data = {}
	data['addr'] = '출발'
	data['sequence'] = 1
	data['time'] = minusHM(current_time, 15)
	msg['routemap'].append(data)

	data = {}
	data['addr'] = '강동자이 프라자아파트 정문'
	data['sequence'] = 2
	data['time'] = minusHM(current_time, 10)
	msg['routemap'].append(data)

	data = {}
	data['addr'] = '현대아파트 (현대중앙상가 앞)'
	data['sequence'] = 3
	data['time'] = minusHM(current_time, 7)
	msg['routemap'].append(data)

	data = {}
	data['addr'] = '위례초 정문'
	data['sequence'] = 4
	data['time'] = current_time
	msg['routemap'].append(data)

	data = {}
	data['addr'] = '도착'
	data['sequence'] = 5
	data['time'] = plusHM(current_time, 15)
	msg['routemap'].append(data)

	return JsonResponse(msg)

def getSchedulesForStudent(request):
    if request.method == "GET":
	max_diff = 10
	msg['schedules'][daydictionary[d]]['list'].append(data)
	return JsonResponse(msg)

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
	msg['sid'] = sid
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

		try :
			car = Car.objects.get(carname=scheduletable.iid.carnum)
			if car.passenger and len(str(car.passenger)) > 9 :
				data['driver_telephone'] = '0' + str(car.passenger)
			else :
				data['driver_telephone'] = "0" + str(car.driver)
		except Car.DoesNotExist:
			data['driver_telephone'] = ''

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
	rideSequence = 0
	for scheduletable in scheduletables:
		if int(sid) in scheduletable.slist:
			rideSequence = len(scheduletables) - sequence - 1
			break
		sequence += 1

	if (rideSequence == 0):
		msg = "해당 inventory 에 sid 의 탑승정보가 존재하지 않습니다."
		return getResponse(debug, 402, msg)

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

def getClauses(request):
	clauses = Clauses.objects.all().order_by('datetime').last()

	data = {}
	data['memberClauses'] = clauses.memberClauses
	data['personalInfoClauses'] = clauses.personalInfoClauses

	return JsonResponse(data)

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

            msg = 'PIN값을 다시 입력해주세요'

            return getResponse(debug,400,msg)

@csrf_exempt
def getStudentInfo2(request):
    if request.method == "POST":
        pin_number = request.POST.get('pin_number')

	debug = 0

        try:
            #sInfo = StudentInfo.objects.get(pin_number = pin_number)
            pInfos = PersonalInfo.objects.filter(pin_number = pin_number)
            if len(pInfos) <= 0:
                raise PersonalInfo.DoesNotExist
            studentInfos = list()
            for pInfo in pInfos:
	        sInfos = StudentInfo.objects.filter(personinfo = pInfo)
                for sInfo in sInfos:

                    studentInfo = {}
    
                    studentInfo['sid'] = sInfo.id
                    studentInfo['aid'] = sInfo.aid_id
                    studentInfo['name'] = sInfo.sname
                    studentInfo['parents_phonenumber'] = sInfo.parents_phonenumber
                    studentInfo['grandparents_phonenumber'] = sInfo.grandparents_phonenumber
                    studentInfo['self_phonenumber'] = sInfo.self_phonenumber
                    studentInfo['care_phonenumber'] = sInfo.care_phonenumber
                    studentInfo['pin'] = pin_number
	            studentInfo['birth_year'] = sInfo.birth_year
	            studentInfo['personinfo_id'] = sInfo.personinfo_id

                    studentInfos.append(studentInfo)

            msg = {}
            msg['students'] = studentInfos

            return JsonResponse(msg)

        except PersonalInfo.DoesNotExist:
            msg = 'PIN값을 다시 입력해주세요'
            return getResponse(debug,401,msg)
        except StudentInfo.DoesNotExist:
            msg = 'PIN값을 다시 입력해주세요'
            return getResponse(debug,402,msg)
        except:
            msg = 'PIN값을 다시 입력해주세요'
            return getResponse(debug,400,msg)

@csrf_exempt
def todayLoad(request):
    if request.method == "POST":
        sid = int(request.POST.get('sid'))
        sTableId = int(request.POST.get('scheduletable_id'))

        debug = 0
        try:
            stable = ScheduleTable.objects.get(id = sTableId)

        except ScheduleTable.DoesNotExist:
            msg = 'ScheduleTable이 존재하지 않습니다.'
            return getResponse(debug, 400, msg) 
        
        try:
            offset_list = stable.slist    
            temp_index = offset_list.index(sid)
        
        except ValueError:
            msg = 'sid가 ScheduleTable안에 존재하지 않습니다.'
            return getResponse(debug, 400, msg)
        
        temp_tflag = stable.tflag
        #load to unload
        if temp_tflag[temp_index] == 0:
            temp_tflag[temp_index] = 1
            button_flag = 0
        #unload to load
        elif temp_tflag[temp_index] == 1:
            temp_tflag[temp_index] = 0
            button_flag = 1

        stable.tflag = temp_tflag
        stable.save()

	msg = {} 
        if button_flag == 0:
            msg['state'] = 'load to unload'
            return getResponse(debug,201,msg)

        elif button_flag == 1:
            msg['state'] = 'unload to load' 
            return getResponse(debug,200,msg)


def checkLoadState(request):
    if request.method == "GET":
        sTableId = int(request.GET.get('scheduletable_id'))
        sid = int(request.GET.get('sid'))
	msg = {}
        try:
            sTable = ScheduleTable.objects.get(id = sTableId)
            slist = sTable.slist
            tflag = sTable.tflag
        except ScheduleTable.DoesNotExist:
            msg = 'ScheduleTable이 존재하지 않습니다.'
            return getResponse(debug, 400, msg)
         
        if len(sTable.slist) != len(sTable.tflag):
            msg['message'] = 'ScheduleTable의 slist와 tflag의 길이가 다릅니다.'
            return getResponse(debug, 400, msg) 
        try:
            sIndex = slist.index(sid)

        except ValueError:
            msg = 'sid가 ScheduleTable안에 존재하지 않습니다.'
            return getResponse(debug, 400, msg)

        debug = 0
        if tflag[sIndex] == 0:
            msg['state'] = 'load'
            return getResponse(debug,200,msg)
        elif tflag[sIndex] == 1:
            msg['state'] = 'unload'
            return getResponse(debug,201,msg)
        else:
            msg = 'schedule table의 tflag값에 오류가 있습니다.'
            return getResponse(debug, 401, msg)
