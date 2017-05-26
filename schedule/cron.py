#_*_ coding:utf-8 _*_
from schedule.models import Inventory,ScheduleTable,HistoryScheduleTable
from passenger.models import StudentInfo, Academy, ShuttleSchedule, ScheduleDate
from passenger.dateSchedule import timeToDate
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def store_historyschedule():
	t = timeToDate()
	dmy = t.timeToDmy()
	d = t.timeToD()

	inventories = Inventory.objects.filter(day=d).select_related()
	for inventory in inventories:
		scheduletables = ScheduleTable.objects.filter(iid_id = inventory.id)
		for scheduletable in scheduletables:
			hst = HistoryScheduleTable(iid_id=scheduletable.iid_id, carnum=inventory.carnum, time=scheduletable.time, addr=scheduletable.addr, alist=scheduletable.alist, tflag=scheduletable.tflag, lflag=scheduletable.lflag)
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

