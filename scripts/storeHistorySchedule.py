#-*- coding: utf-8 -*-
from passenger.dateSchedule import timeToDate
from schedule.models import Inventory, ScheduleTable, EditedInven, HistoryScheduleTable
from passenger.models import StudentInfo, Academy
import sys
from datetime import datetime, timedelta, date
import psycopg2
import os
import time
from schedule.tasks import get_offmember_list, get_offmember_list_today_click


def store_historyschedule(sdate):
	tt = ['월', '화', '수', '목', '금', '토', '일']

	day = sdate.weekday()
	ymd = sdate.strftime('%Y-%m-%d')
	d = tt[day]

	try :
		conn = psycopg2.connect("dbname='tayo4' user='postgres' host='localhost' password='beclear048@'")
	except :
		print "unable to connect to the database"

	cur = conn.cursor()
	
	try :
		cur.execute("""select inventory.id, inventory.carnum, schedule.time, schedule.addr, schedule.alist, schedule.tflag, schedule.lflag, schedule.req, schedule.slist, schedule.id from schedule_inventory inventory, schedule_scheduletable schedule where inventory.id = schedule.iid_id and inventory.day = '""" + d + """';""")
	except:
		print "Can't call SELECT"

	rows = cur.fetchall()

	print "len = " + str(len(rows))
	academy_dict = {}
	for row in rows:
		#inventories = Inventory.objects.filter(day=d).select_related()
		#sys.stderr.write( "len = " + str(len(inventories)) + "\n")
		#for inventory in inventories:
		#print "[" + str(row[0]) + "] : [" + str(row[1]) + "]"
		
		#hst = HistoryScheduleTable(date=ymd, iid_id=row[0], carnum=row[1], time=row[2], addr=row[3], alist=row[4], tflag=row[5], lflag=row[6], req=row[7])
		#hst.save()
		for sid in row[8]:
			try:
				student = StudentInfo.objects.get(id=sid)
				#hst.members.add(student)
			except StudentInfo.DoesNotExist:
				print "sid = " + str(sid) + " doesn't exist"
		for aid in row[4]:
			try:
				academy = Academy.objects.get(id=aid)
				#hst.academies.add(academy)
			except Academy.DoesNotExist:
				print "aid = " + str(aid) + " doesn't exist"

		offmembers = get_offmember_list(row[5], row[8])
		for offmember in offmembers:
			student = StudentInfo.objects.get(id = offmember)
			#hst.offmembers.add(student)

		offmembers_today_click = get_offmember_list_today_click(row[5], row[8], row[9], ymd)
		for offmember_today_click in offmembers_today_click:
			student = StudentInfo.objects.get(id = offmember_today_click)
			print "[" + ymd + "] : " + str(student.id) + ":" + str(row[9])
			if (student.aid.name in academy_dict.keys()):
				academy_dict[student.aid.name] += 1
			else:
				academy_dict[student.aid.name] = 1

	for k, v in academy_dict.iteritems():
		print str(k) + " ==> " + str(v)


def daterange(start_date, end_date):
	for n in range(int ((end_date - start_date).days)):
		yield start_date + timedelta(n)

def run(*args):
	start_date = date(2017, 10, 1)
	end_date = date(2017, 11, 1)
	for single_date in daterange(start_date, end_date):
		cur_date = single_date.strftime("%Y-%m-%d")
		os.system("/home/ubuntu/backup/restore.sh " + cur_date + " tayo4")
		print "cur_date = " + cur_date
		store_historyschedule(single_date)
