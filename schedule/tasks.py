#_*_ coding:utf-8 _*_
from __future__ import absolute_import
from tayo.celery import app
from schedule.models import Inventory,ScheduleTable,HistoryScheduleTable, EditedInven, EditedScheduleTable
from passenger.models import StudentInfo, Academy, ShuttleSchedule, ScheduleDate
from passenger.dateSchedule import timeToDate
from schedule.models import Inventory, ScheduleTable, EditedInven, EditedScheduleTable, TodayLoadTimeLog
import sys
import requests
import simplejson
reload(sys)
sys.setdefaultencoding('utf-8')


def get_offmember_list(tflag, slist):
	ret = []
	for idx, t in enumerate(tflag):
		if t == 1:
			ret.append(slist[idx])

	return ret

def get_offmember_list_today_click(tflag, slist, stableid, ymd):
	ret = []
	for idx, t in enumerate(tflag):
		if t == 1:
			try:
				todayloadtimelog = TodayLoadTimeLog.objects.filter(stable__id=stableid, sid__id=slist[idx]).last()
			except TodayLoadTimeLog.DoesNotFound:
				print "None [" + ymd + "] sid = " + str(slist[idx]) + ", stable_id = " + str(stableid)
				pass

			if (todayloadtimelog != None):
				if (todayloadtimelog.reqtime > ymd + ' 00:00'):
					ret.append(slist[idx])

	return ret

@app.task
def store_historyschedule():
	t = timeToDate()
	store_historyschedule_func(t)

def store_historyschedule_func(t):
	ymd = t.timeToYmd()
	d = t.timeToD()

	inventories = Inventory.objects.filter(day=d).select_related()
	#print "# of inventory = " + str(len(inventories))
	for inventory in inventories:
		scheduletables = ScheduleTable.objects.filter(iid_id = inventory.id)
		#print "# of scheduletables = " + str(len(scheduletables))
		for scheduletable in scheduletables:
			hst = HistoryScheduleTable(date=ymd, iid_id=scheduletable.iid_id, carnum=inventory.carnum, time=scheduletable.time, addr=scheduletable.addr, tflag=scheduletable.tflag, lflag=scheduletable.lflag, req=scheduletable.req)
			hst.save()
			try :
				academyset = set()
				for sid in scheduletable.slist:
					student = StudentInfo.objects.get(id=sid)
					hst.members.add(student)
					academyset.add(student.aid)

				for academy in academyset:
					hst.academies.add(academy)
					
				#for aid in scheduletable.alist:
					#academy = Academy.objects.get(id=aid)
					#hst.academies.add(academy)

				offmembers = get_offmember_list(scheduletable.tflag, scheduletable.slist)
				for offmember in offmembers:
					student = StudentInfo.objects.get(id=offmember)
					hst.offmembers.add(student)

				todayoffmembers = get_offmember_list_today_click(scheduletable.tflag, scheduletable.slist, scheduletable.id, ymd)
				for todayoffmember in todayoffmembers:
					student = StudentInfo.objects.get(id=todayoffmember)
					hst.todayoffmembers.add(student)
			except Exception as e:
				print(e)

@app.task
def say_hello():
	print("Hello, celery!")


@app.task
def store_historyschedule_old():
	t = timeToDate()
	dmy = t.timeToDmy()
	d = t.timeToD()

	sschedule = ShuttleSchedule.objects.filter(day=d)

	for s in sschedule:
    		ds = ScheduleDate(a_name = s.a_name, day = s.day, time = s.time,schedule = s.schedule, gid = s.gid, aid = s.aid,slist = s.slist,p_schedule = s.p_schedule, alist = s.alist, memo = s.memo, date = dmy)
	    	ds.save()

def reset_lflag_on_every_schedule():
	schedules = ScheduleTable.objects.all()
	for schedule in schedules:
		tflags = map(lambda x:0, schedule.tflag)
		schedule.tflag = tflags
		schedule.save()

def notice_to_student(sid, msg):
	name = ""
	try:
		studentinfo = StudentInfo.objects.get(id = sid)
		name = studentinfo.sname
		data = {
			'text': name + "\n" + msg ,
		}
		r = requests.post("https://hooks.slack.com/services/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", json=data)
	except StudentInfo.DoesNotExist:
		name = "none"

	#print name + "[" + str(sid) + "] : " + msg
	return

def find_update():
	t = timeToDate()
	d = t.timeToD()
	studentset = set()
	scheduletables = list()

	lastweek = ''
	lastweekt = timeToDate()
	lastweekt.setLastWeekDay()
	lastweek = lastweekt.timeToYmd()
	
	inventory_ids = list()

	inventories = Inventory.objects.filter(day=d).select_related()
	for inventory in inventories:
		inventory_ids.append(inventory.id)
		scheduletables = ScheduleTable.objects.filter(iid_id = inventory.id).order_by('time')
		for scheduletable in scheduletables:
			if (scheduletable.slist != None or len(scheduletable.slist) != 0):
				for sid in scheduletable.slist:
					studentset.add(str(sid))

	#print "lastweek = " + lastweek
	print "len = " + str(len(studentset))
	#print "inv_len = " + str(len(inventory_ids))
	for sid in studentset:
		#for inventory in inventories:
		try :
			studentinfo = StudentInfo.objects.get(id=sid)
		except StudentInfo.DoesNotExist:
			continue
		scheduletables = ScheduleTable.objects.filter(iid_id__in = inventory_ids).filter(slist__contains = [sid]).order_by('time')
		old_scheduletables = HistoryScheduleTable.objects.filter(date = lastweek).filter(iid_id__in = inventory_ids).filter(members__in = [studentinfo]).order_by('time')

		msg = ""
		for scheduletable in scheduletables:
			found = False
			same_inventory = False
			for old_scheduletable in old_scheduletables:
				if (scheduletable.iid_id == old_scheduletable.iid_id) :
					same_inventory = True
					if (scheduletable.time == old_scheduletable.time and scheduletable.addr == old_scheduletable.addr):
						found = True
                        print "found True : " + str(sid)
			if found == False :
				inventory = Inventory.objects.get(id = scheduletable.iid_id)
				if same_inventory == False :
					msg += "\t\t신규 {" + inventory.day + "} [" + scheduletable.time + "] : " + scheduletable.addr + "\n"
					#msg += u"\t\t신규 {" + inventory.day + "} [" + scheduletable.time + "] : " + scheduletable.addr + ":" + str(scheduletable.iid_id) + "\n"
				else :
					msg += u"\t\t변경 {" + inventory.day + "} [" + scheduletable.time + "] : " + scheduletable.addr + "\n"
                if (msg != ""):
		    notice_to_student(sid, msg)

	notice_to_student(0, "end")

@app.task
def weekly_update():
        #copy week1 -> OG inven
	invenEditedWeek1 = Inventory.objects.filter(week1 = 1)
	for iw1 in invenEditedWeek1:
		editedInvensWeek1 = iw1.editedinvens.all().filter(week = 1)
		tempInven = Inventory.objects.get(id = iw1.id)

		for eiw1 in editedInvensWeek1:
			tempInven.carnum = eiw1.carnum
			tempInven.bid = eiw1.bid
			tempInven.snum = eiw1.snum
			tempInven.day = eiw1.day
			tempInven.slist = eiw1.slist
			tempInven.stime = eiw1.stime
			tempInven.etime = eiw1.etime
			tempInven.req = eiw1.req
			tempInven.memo = eiw1.memo
			
			tempInven.scheduletables.all().delete()
			tempInven.save()

			editedScheduleTablesWeek1 = eiw1.editedscheduletables.all()

			for estw1 in editedScheduleTablesWeek1:
				stable = ScheduleTable(iid = tempInven, time = estw1.time, addr = estw1.addr, req = estw1.req,slist=estw1.slist,sname=estw1.sname, tflag=estw1.tflag, lflag=estw1.lflag)
				stable.save()


	#Inventory.objects.filter(week1=1,week2=1,week3=1,editedinvens=None).delete()

	#createdInvenWeek1 = EditedInven.objects.filter(week=1).filter(iid_id = None)
	#for ciw1 in createdInvenWeek1:
	#	createdScheduleTablesWeek1 = ciw1.editedscheduletables.all()

	#	inven = Inventory.objects.create(carnum = ciw1.carnum, bid = ciw1.bid, snum = ciw1.snum, day = ciw1.day , alist=ciw1.alist, anamelist = ciw1.anamelist, slist=ciw1.slist, stime = ciw1.stime, etime = ciw1.etime, req=ciw1.req, memo=ciw1.memo, week1 = 1, week2 = 1, week3 = 1)

	#	for cstw1 in createdScheduleTablesWeek1:
	#		ScheduleTable.objects.create(iid = inven, time = cstw1.time, addr = cstw1.addr, req = cstw1.req, alist=cstw1.alist, anamelist=cstw1.anamelist,slist=cstw1.slist,sname=cstw1.sname, tflag=cstw1.tflag, lflag=cstw1.lflag)

	#week1 editedInven, createdInven delete(include referenced tables)
	EditedInven.objects.filter(week=1).prefetch_related('editedscheduletables').delete()


	EditedInven.objects.filter(week=2).update(week=1)
	EditedInven.objects.filter(week=3).update(week=2)


	editedInvenWeek2 = EditedInven.objects.filter(week=2)

	for eiw2 in editedInvenWeek2:
		createInvenWeek3 = EditedInven.objects.create(carnum = eiw2.carnum, bid = eiw2.bid, snum = eiw2.snum, iid = eiw2.iid,day = eiw2.day,slist = eiw2.slist, stime = eiw2.stime, etime = eiw2.etime, req = eiw2.req, memo = eiw2.memo, week = 3)

		editedScheduleTablesWeek2 = eiw2.editedscheduletables.all()

		for estw2 in editedScheduleTablesWeek2:
			EditedScheduleTable.objects.create(ieid = createInvenWeek3, time = estw2.time, addr = estw2.addr, req = estw2.req,slist = estw2.slist, sname = estw2.sname, tflag = estw2.tflag, lflag = estw2.lflag)


	#Inventory week3 -> week2, week2 -> week1, week1->week
	ivenAllWeek1 = Inventory.objects.filter(week1 = 1)

	for ia in ivenAllWeek1:
	 	tempInven = Inventory.objects.get(id = ia.id)
	 	tempInven.week1 = 1
	 	tempInven.week2 = 1
	 	tempInven.week3 = 1
	 	tempInven.save()

	ivenAllWeek2 = Inventory.objects.filter(week2 = 1)

	for ia in ivenAllWeek2:
	 	tempInven = Inventory.objects.get(id = ia.id)
		tempInven.week1 = 1
		tempInven.week2 = 1
	 	tempInven.week3 = 1
	 	tempInven.save()

	ivenAllWeek3 = Inventory.objects.filter(week3 = 1)

	for ia in ivenAllWeek3:
	 	tempInven = Inventory.objects.get(id = ia.id)
		tempInven.week2 = 1
	 	tempInven.week3 = 1
	 	tempInven.save()

@app.task
def resetTodayLoad():
    sTable = ScheduleTable.objects.all()

    for s in sTable:
        lenTflag = len(s.tflag)
        s.tflag = [0]*lenTflag
        s.save()
