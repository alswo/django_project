#-*- coding: utf-8 -*-
from passenger.models import Academy, StudentInfo
from schedule.models import Inventory, ScheduleTable, Car
from django.db.models import Func, F
from indicator.models import ShuttleIndicator, InstituteIndicator
from django.utils import timezone
import time

def get_current_date():
	return str(timezone.now())[:10]

def get_current_day():
	day_dict = {'Mon':'월', 'Tue':'화', 'Wed':'수', 'Thu':'목', 'Fri':'금', 'Sat':'토', 'Sun':'일'}
	current_time = time.localtime()
	return day_dict[time.strftime("%a", current_time)]

def run(*args):

	today = get_current_date()
	current_day = get_current_day()

	totalInventoryNum = 0
	totalScheduleTableNum = 0
	totalStudentinfoNum = 0
	for academy in Academy.objects.all():
		studentInfos = StudentInfo.objects.filter(aid = academy, deleted_date__isnull = True)
		academyStudentList = list(studentInfos.values_list('id', flat=True))

		inventories = Inventory.objects.filter(alist__contains = [academy.id])
		scheduleTables = ScheduleTable.objects.filter(alist__contains = [academy.id])

		inventorynum = inventories.count()
		scheduletablenum = scheduleTables.count()
		studentInfoSet = set(list(scheduleTables.exclude(slist__exact='{}').annotate(sid = Func(F('slist'), function='unnest')).values_list('sid', flat=True))) & set(academyStudentList)
		studentinfonum = len(studentInfoSet)

		#For day
		dayInventories = inventories.filter(day = current_day)
		dayScheduleTables = scheduleTables.filter(iid_id__in = dayInventories.values_list('id', flat=True)).filter(slist__overlap = academyStudentList)

		# model filter 로 처리하려 했는데.. 실패
		#dayStudentCount = dayScheduleTables.exclude(slist__exact='{}').annotate(sid = Func(F('slist'), function='unnest')).values_list('sid').filter(sid__in = academyStudentList).count()
		dayinventorynum = dayInventories.count()
		dayscheduletablenum = dayScheduleTables.count()
		dayStudentInfoSet = set(list(dayScheduleTables.exclude(slist__exact='{}').annotate(sid = Func(F('slist'), function='unnest')).values_list('sid', flat=True))) & set(academyStudentList)
		daystudentinfonum = len(dayStudentInfoSet)


		instituteIndicator = InstituteIndicator(date = today, inventorynum = inventorynum, scheduletablenum = scheduletablenum, studentinfonum = studentinfonum, academy = academy, dayinventorynum = dayinventorynum, dayscheduletablenum = dayscheduletablenum, daystudentinfonum = daystudentinfonum)
		instituteIndicator.save()
		#print "[tot] name = {0}, studentNum = {1}, inventorynum = {2}, scheduletablenum = {3}".format(academy.name, studentinfonum, inventorynum, scheduletablenum)
		#print "[day] name = {0}, studentNum = {1}, inventorynum = {2}, scheduletablenum = {3}".format(academy.name, daystudentinfonum, dayinventorynum, dayscheduletablenum)

		totalInventoryNum += inventorynum
		totalScheduleTableNum += scheduletablenum
		totalStudentinfoNum += studentinfonum
		
	#print "totalinvennum = {0}".format(totalInventoryNum)
	#print "totalschedulenum = {0}".format(totalScheduleTableNum)
	#print "totalstudentnum = {0}".format(totalStudentinfoNum)

	totalInventoryNum = 0
	totalScheduleTableNum = 0
	totalStudentinfoNum = 0
	for car in Car.objects.all():
		inventories = Inventory.objects.filter(carnum = car.carname)
		inventorynum = inventories.count()
		scheduletablenum = 0
		studentinfonum = 0
		for inventory in inventories:
			scheduletablenum += inventory.scheduletables.all().count()
			studentinfonum +=  inventory.scheduletables.exclude(slist__exact='{}').annotate(sid = Func(F('slist'), function='unnest')).count()

		dayInventories = inventories.filter(day = current_day)
		dayinventorynum = dayInventories.count()
		dayscheduletablenum = 0
		daystudentinfonum = 0
		for inventoy in dayInventories:
			dayscheduletablenum += inventory.scheduletables.all().count()
			daystudentinfonum +=  inventory.scheduletables.exclude(slist__exact='{}').annotate(sid = Func(F('slist'), function='unnest')).count()
		shuttleIndicator = ShuttleIndicator(date = today, inventorynum = inventorynum, scheduletablenum = scheduletablenum, studentinfonum = studentinfonum, car = car, dayinventorynum = dayinventorynum, dayscheduletablenum = dayscheduletablenum, daystudentinfonum = daystudentinfonum)
		shuttleIndicator.save()
		#print "[tot] carname = {0}, studentNum = {1}, inventorynum = {2}, scheduletablenum = {3}".format(car.carname, studentinfonum, inventorynum, scheduletablenum)
		#print "[day] carname = {0}, studentNum = {1}, inventorynum = {2}, scheduletablenum = {3}".format(car.carname, daystudentinfonum, dayinventorynum, dayscheduletablenum)
		totalInventoryNum += inventorynum
		totalScheduleTableNum += scheduletablenum
		totalStudentinfoNum += studentinfonum
		
	#print "totalinvennum = {0}".format(totalInventoryNum)
	#print "totalschedulenum = {0}".format(totalScheduleTableNum)
	#print "totalstudentnum = {0}".format(totalStudentinfoNum)
