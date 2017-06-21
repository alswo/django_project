#_*_ coding:utf-8 _*_
from schedule.models import Inventory,ScheduleTable,HistoryScheduleTable
from passenger.models import StudentInfo, Academy, ShuttleSchedule, ScheduleDate
from passenger.dateSchedule import timeToDate
import sys
import requests
import simplejson
reload(sys)
sys.setdefaultencoding('utf-8')


def store_historyschedule():
	t = timeToDate()
	dmy = t.timeToDmy()
	ymd = t.timeToYmd()
	d = t.timeToD()

	inventories = Inventory.objects.filter(day=d).select_related()
	for inventory in inventories:
		scheduletables = ScheduleTable.objects.filter(iid_id = inventory.id)
		for scheduletable in scheduletables:
			hst = HistoryScheduleTable(date=ymd, iid_id=scheduletable.iid_id, carnum=inventory.carnum, time=scheduletable.time, addr=scheduletable.addr, alist=scheduletable.alist, tflag=scheduletable.tflag, lflag=scheduletable.lflag)
			hst.save()
                	for sid in scheduletable.slist:
                    	    student = StudentInfo.objects.get(id=sid)
                    	    hst.members.add(student)
                	for aid in scheduletable.alist:
                    	    academy = Academy.objects.get(id=aid)
                    	    hst.academies.add(academy)


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

	print "len = " + str(len(studentset))
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
			if found == False :
				inventory = Inventory.objects.get(id = scheduletable.iid_id)
				if same_inventory == False :
					msg += "\t\t신규 {" + inventory.day + "} [" + scheduletable.time + "] : " + scheduletable.addr + "\n"
				else :
					msg += "\t\t변경 {" + inventory.day + "} [" + scheduletable.time + "] : " + scheduletable.addr + "\n"
                if (msg != ""):
		    notice_to_student(sid, msg)

	notice_to_student(0, "end")
