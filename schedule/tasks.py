#_*_ coding:utf-8 _*_
from __future__ import absolute_import
from tayo.celery import app
from schedule.models import Inventory,ScheduleTable,HistoryScheduleTable
from passenger.dateSchedule import timeToDate

def get_offmember_list(tflag, slist):
	ret = []
	for idx, t in enumerate(tflag):
		if t == 1:
			ret.append(slist[idx])

	return ret

@app.task
def store_historyschedule():
	t = timeToDate()
	dmy = t.timeToDmy()
	ymd = t.timeToYmd()
	d = t.timeToD()

	inventories = Inventory.objects.filter(day=d).select_related()
	#print "# of inventory = " + str(len(inventories))
	for inventory in inventories:
		scheduletables = ScheduleTable.objects.filter(iid_id = inventory.id)
		#print "# of scheduletables = " + str(len(scheduletables))
		for scheduletable in scheduletables:
			hst = HistoryScheduleTable(date=ymd, iid_id=scheduletable.iid_id, carnum=inventory.carnum, time=scheduletable.time, addr=scheduletable.addr, alist=scheduletable.alist, tflag=scheduletable.tflag, lflag=scheduletable.lflag, req=scheduletable.req)
			hst.save()
			try :
				for sid in scheduletable.slist:
					student = StudentInfo.objects.get(id=sid)
					hst.members.add(student)
				for aid in scheduletable.alist:
					academy = Academy.objects.get(id=aid)
					hst.academies.add(academy)

				offmembers = get_offmember_list(scheduletable.tflag, scheduletable.slist)
				for offmember in offmembers:
					student = StudentInfo.objects.get(id=offmember)
					hst.offmembers.add(student)
			except Exception as e:
				print(e)

@app.task
def say_hello():
	print("Hello, celery!")
