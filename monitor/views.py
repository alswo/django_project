# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from schedule.models import Inventory, ScheduleTable, RealtimeLocation
from schedule.views import get_difference
from passenger.dateSchedule import timeToDate
from datetime import datetime

# Create your views here.

def setTimeDelta(time1, timedelta):
	timevar1 = time1.split(':')
	totalmin = int(timevar1[0]) * 60 + int(timevar1[1]) + timedelta

	return str(int(totalmin / 60)) + ':' + str(totalmin - int(totalmin / 60) * 60)

def shuttles(request):
	# filter inventories 
	t = timeToDate()
	today = t.timeToYmd()
	hm = t.timeToHM()

	hm = "18:29"

	msg = ""
	inventories = Inventory.objects.filter(day = '월', stime__lte = '1801', etime__gte = '1801')
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
		lastlocation = RealtimeLocation.objects.filter(date='2017-07-17', carnum=inventory.carnum).order_by('schedule_time').last()
		if (lastlocation):
			diff1 = get_difference(lastlocation.schedule_time, lastlocation.departure_time)
			hoursMinutes = setTimeDelta(hm, diff1).split(':')
			inven['shuttle']['hour'] = hoursMinutes[0]
			inven['shuttle']['minute'] = hoursMinutes[1]

		for scheduletable in scheduletables:
			hoursMinutes = scheduletable.time.split(':')

			if (scheduletable.lflag == 2):
				addr = '출발'
				# 아직 출발하지 않았으면
				if (lastlocation):
					pass
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

			inven['schedules'].append({'hour': hoursMinutes[0], 'minute': hoursMinutes[1], 'addr': addr})
	
			if (lastlocation and lastlocation.schedule_time < scheduletable.time and hm > scheduletable.time and diff2 < 0):
				diff2 = get_difference(scheduletable.time, hm) - 1
				hoursMinutes = setTimeDelta(hm, diff2).split(':')
				inven['shuttle']['hour'] = hoursMinutes[0]
				inven['shuttle']['minute'] = hoursMinutes[1]

		invens.append(inven)

		msg += "id : " + str(inventory.id)
		msg += "car : " + str(inventory.carnum)
		msg += "\n"

		inven_id = inventory.id

	return render_to_response('shuttles.html', {'msg': msg, 'invens': invens})
	#return HttpResponse('\n'.join('{}: {}'.format(*k) for k in enumerate(invens['shuttle']['carnum'])))
	#return HttpResponse("diff1 = " + str(diff1) + ", diff2 = " + str(diff2))
	#return HttpResponse(inven_id)
