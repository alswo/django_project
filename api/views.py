# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from schedule.models import RealtimeLocation, Inventory, ScheduleTable, Car
from passenger.models import StudentInfo, Academy, PersonalInfo
from passenger.dateSchedule import timeToDate
from fcmdev.models import PropOfDevice
from fcm_django.models import FCMDevice
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

def getResponse(debug, code, msg):
	if (debug == 1):
		return HttpResponse(msg)
	else:
		return JsonResponse({'code': code, 'msg': msg})

# Create your views here.
def getRealtimeLocationDebug(request):
	if request.method == "GET":
		debug_id = request.GET.get('debug_id')
		if (debug_id == None):
			debug_id = '0'
		msg = ""

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

		return getResponse(0, int(debug_id), msg)

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

@csrf_exempt
def getDeviceInfo(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        registration_id = request.POST.get('registration_id')
        active = True
        osType = request.POST.get('type')
        device_id = request.POST.get('device_id')
        model = request.POST.get('model')
        version = request.POST.get('version')
        serial = request.POST.get('serial')
        manufacture = request.POST.get('manufacture')
        pin_number = request.POST.get('pin_number')
        push = request.POST.get('recvpush')
        debug = request.POST.get('debug')

        if (debug):
            debug = 1
        else:
            debug = 0

        if push == 'false':
            push = False
        elif push == 'true':
            push = True
        else:
            push = push

        if (registration_id == None):
            msg = "there is no registration_id"
            return getResponse(debug, 400, msg)
        elif (device_id == None):
            msg = "there is no device_id"
            return getResponse(debug, 400, msg)

	elif (push == None):
            msg = "there is no recvpush"
            return getResponse(debug, 400, msg)


        try:
            fcm_device = FCMDevice.objects.get(device_id=device_id)
            fcm_device.registration_id = registration_id
            fcm_device.save()
            prop_device = PropOfDevice.objects.get(device_id=device_id)
            prop_device.pin_number = pin_number
            prop_device.receivePush = push
            prop_device.save()

            msg = 'update'
            return getResponse(debug, 200, msg)

        except FCMDevice.DoesNotExist:


			fcmDevice = FCMDevice.objects.create(device_id=device_id,name=name, registration_id=registration_id,active=active, type=osType)
			fcmDevice.save()
			propofDevice = PropOfDevice.objects.create(
                device_id=device_id,
                pin_number=pin_number,
                model=model,
                version=version,
                serial=serial,
                manufacture=manufacture,
                receivePush=push
                )
			propofDevice.save()
			msg = 'insert'
			return getResponse(debug, 201, msg)
	except:
			msg = "error."
			return getResponse(debug, 400, msg)





@csrf_exempt
def pushConfirmInfo(request):
    if request.method == 'POST':
        pin = request.POST.get('pin')
        confirming = request.POST.get('confirming')
        status = request.POST.get('status')
        token = request.POST.get('token')
        debug = request.POST.get('debug')

        if (debug):
            debug = 1
        else:
            debug = 0

        if status == '1':
            status = True
        elif status == '0':
            status = False
        else:
            status = True
        try:
            pushConfirm = PushConfirming.objects.create(pin=pin, confirming=confirming, status=status, token=token)
            pushConfirm.save()
            msg = "confirm"
            return getResponse(debug, 200, msg)

        except:
            msg = "error"
            return getResponse(debug, 400, msg)
