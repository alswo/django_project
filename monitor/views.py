# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from schedule.models import Inventory, ScheduleTable, HistoryScheduleTable, RealtimeLocation, Car
from schedule.views import get_difference
from passenger.dateSchedule import timeToDate
from passenger.models import Academy
from datetime import datetime
from django.db import connection

# Create your views here.

class CrowdedBus:
	def __init__(self):
		self.carnum = 0
		self.stime_hr = ''
		self.stime_min = ''
		self.etime_hr = ''
		self.etime_min = ''
		self.numofstudent = 0
		self.numofschedule = 0
		self.alist = None

def makeTimeStr(inttime):
	timestr = "%04d" % inttime
	return [timestr[:2], timestr[2:]]

@login_required
def inventories(request):
	t = timeToDate()
	today = t.timeToD()

	green_numofstudent = 2
	orange_numofstudent = 5

	if request.GET.get('green_numofstudent'):
		green_numofstudent = int(request.GET.get('green_numofstudent'))
	if request.GET.get('orange_numofstudent'):
		orange_numofstudent = int(request.GET.get('orange_numofstudent'))

	if request.GET.get('aid') :
		aid = int(request.GET.get('aid'))
	else :
		aid = 0

	if (request.GET.get('bid')) :
		bid = int(request.GET.get('bid'))
	else :
		bid = 1

	if (request.GET.get('day')) :
		day = request.GET.get('day')
	else :
		day = today


	crowdedbuses = []
	shuttles = {}
	

	inventories = Inventory.objects.filter(day = day, bid = bid)
	for inventory in inventories:
		crowdedbus = CrowdedBus()
		crowdedbus.carnum = inventory.carnum
		(crowdedbus.stime_hr, crowdedbus.stime_min) = makeTimeStr(inventory.stime)
		(crowdedbus.etime_hr, crowdedbus.etime_min) = makeTimeStr(inventory.etime)
		crowdedbus.numofstudent = len(inventory.slist)
		crowdedbus.alist = inventory.alist

		crowdedbuses.append(crowdedbus)
		shuttles[inventory.carnum] = 1

	academies = Academy.objects.filter(bid = bid).order_by('name')

	try:
		aname = academies.get(id = aid).name
	except Academy.DoesNotExist:
		aname = ""
		aid = 0

	return render(request, 'crowdedbus.html', {'crowdedbuses': crowdedbuses, 'shuttles': shuttles.keys(), 'green_numofstudent': green_numofstudent, 'orange_numofstudent': orange_numofstudent, 'range': range(10), 'dayrange': ['월', '화', '수', '목', '금', '토'], 'academies': academies, 'aid': aid, 'aname': aname, 'bid': bid, 'day': day})


def setTimeDelta(time1, timedelta):
	timevar1 = time1.split(':')
	totalmin = int(timevar1[0]) * 60 + int(timevar1[1]) + timedelta

	return str(int(totalmin / 60)) + ':' + str(totalmin - int(totalmin / 60) * 60)

def shuttles(request):
	# filter inventories 
	t = timeToDate()
	today = t.timeToYmd()
	hm = t.timeToHM()
	rawhm = t.timeToRawHM()
	d = t.timeToD()

	msg = ""
	inventories = Inventory.objects.filter(day = d, stime__lte = int(rawhm) + 30, etime__gte = int(rawhm) - 30)
	invens = list()
	for inventory in inventories:
		diff1 = -1
		diff2 = -1
		inven = {}
		inven['schedules'] = list()
		inven['shuttle'] = {}
		inven['id'] = inventory.id
		scheduletables = ScheduleTable.objects.filter(iid = inventory.id).order_by('time')

		inven['shuttle']['carnum'] = inventory.carnum
		lastlocation = RealtimeLocation.objects.filter(date=today, carnum=inventory.carnum, schedule_time__lte=str(inventory.etime)[:2]+':'+str(inventory.etime)[2:], schedule_time__gte=str(inventory.stime)[:2]+':'+str(inventory.stime)[2:]).order_by('schedule_time').last()
		if (lastlocation):
			diff1 = get_difference(lastlocation.departure_time, lastlocation.schedule_time)
			hoursMinutes = setTimeDelta(hm, diff1).split(':')
			inven['shuttle']['hour'] = hoursMinutes[0]
			inven['shuttle']['minute'] = hoursMinutes[1]

		for scheduletable in scheduletables:
			hoursMinutes = scheduletable.time.split(':')

			if (scheduletable.lflag == 2):
				addr = '출발'
				if (lastlocation and lastlocation.schedule_time >= scheduletable.time):
					pass
				# 아직 출발하지 않았으면
				else:
					inven['shuttle']['hour'] = hoursMinutes[0]
					inven['shuttle']['minute'] = hoursMinutes[1]
			elif (scheduletable.lflag == 3):
				addr = '도착'
				# 도착했으면
				if (lastlocation and lastlocation.schedule_time == scheduletable.time):
					inven['shuttle']['hour'] = hoursMinutes[0]
					inven['shuttle']['minute'] = hoursMinutes[1]
			else:
				addr = scheduletable.addr

				if (lastlocation and lastlocation.schedule_time < scheduletable.time and hm > scheduletable.time and diff2 < 0):
					diff2 = 1
					hoursMinutes = setTimeDelta(scheduletable.time, -1).split(':')
					inven['shuttle']['hour'] = hoursMinutes[0]
					inven['shuttle']['minute'] = hoursMinutes[1]

			inven['schedules'].append({'hour': hoursMinutes[0], 'minute': hoursMinutes[1], 'addr': addr})

		invens.append(inven)

		msg += "id : " + str(inventory.id)
		msg += "car : " + str(inventory.carnum)
		msg += "\n"

		inven_id = inventory.id

	return render(request, 'shuttles.html', {'msg': msg, 'invens': invens})

class RealtimeLocationHistory:
	def __init__(self):
		self.carnum = 0
		self.historyscheduletables = None

class HistoryScheduleTableWithRealtimeLocation:
	def __init__(self):
		schedule_time = None
		color = 'grey'
		addr = None

def realtimeLocationHistory(request):
	realtimeLocationHistories = list()
	cars = Car.objects.all().order_by('carname')
	cursor = connection.cursor()
	cur_date = request.GET.get('cur_date')
	if (cur_date == None):
		t = timeToDate()
		cur_date = t.timeToYmd()

	for car in cars:
		cursor.execute("select addr, lflag, time, departure_time from schedule_historyscheduletable history LEFT OUTER JOIN (SELECT carnum, schedule_time, MIN(departure_time) AS departure_time FROM schedule_realtimelocation WHERE date = '%s' group by carnum, schedule_time) realtimelocation ON( realtimelocation.schedule_time = history.time) WHERE history.date = '%s' and history.carnum = %s" % (cur_date, cur_date, car.carname));

		realtimeLocationHistory = RealtimeLocationHistory()
		realtimeLocationHistory.carnum = car.carname
		realtimeLocationHistory.historyscheduletables = list()

		for row in cursor.fetchall():
			h = HistoryScheduleTableWithRealtimeLocation()
			h.schedule_time = row[2]
			if (row[1] == 2):
				h.addr = '출발'
			elif (row[1] == 3):
				h.addr = '도착'
			else:
				h.addr = row[0]

			if (row[3] == None):
				h.color = 'red'
			elif (get_difference(row[3], row[2]) >= 3):
				h.color = 'orange'
			else:
				h.color = 'green'

			realtimeLocationHistory.historyscheduletables.append(h)

		realtimeLocationHistories.append(realtimeLocationHistory)

	#return render(request, 'realtimeLocationHistory.html', {'histories': realtimeLocationHistories, 'cur_date': cur_date.replace("-", "/")})
	return render(request, 'realtimeLocationHistory.html', {'histories': realtimeLocationHistories, 'cur_date': cur_date})
