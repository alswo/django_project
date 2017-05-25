#_*_ coding:utf-8 _*_
from schedule.models import Inventory,ScheduleTable,HistoryScheduleTable
from passenger.models import StudentInfo, Academy
from passenger.dateSchedule import timeToDate
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def store_historyschedule():
	t = timeToDate()
	dmy = t.timeToDmy()
	d = t.timeToD()

	d = '월'

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
