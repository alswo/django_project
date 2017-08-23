#-*- coding: utf-8 -*-
from passenger.dateSchedule import timeToDate
from schedule.models import Inventory, ScheduleTable, EditedInven, HistoryScheduleTable
from passenger.models import StudentInfo, Academy
import sys
from datetime import datetime, timedelta, date
import psycopg2
import os
import time


def store_historyschedule(sdate):
	tt = ['월', '화', '수', '목', '금', '토', '일']

	day = sdate.weekday()
	ymd = sdate.strftime('%Y-%m-%d')
	d = tt[day]

	try :
		conn = psycopg2.connect("dbname='tayo3' user='postgres' host='localhost' password='beclear048@'")
	except :
		print "unable to connect to the database"

	cur = conn.cursor()
	
	try :
		cur.execute("""select inventory.id, inventory.carnum, schedule.time, schedule.addr, schedule.alist, schedule.tflag, schedule.lflag, schedule.req, schedule.slist from schedule_inventory inventory, schedule_scheduletable schedule where inventory.id = schedule.iid_id and inventory.day = '""" + d + """';""")
	except:
		print "Can't call SELECT"

	rows = cur.fetchall()

	print "len = " + str(len(rows))
	for row in rows:
		#inventories = Inventory.objects.filter(day=d).select_related()
		#sys.stderr.write( "len = " + str(len(inventories)) + "\n")
		#for inventory in inventories:
		print "[" + str(row[0]) + "] : [" + str(row[1]) + "]"
		
		#scheduletables = ScheduleTable.objects.filter(iid_id = row[0])
		#for scheduletable in scheduletables:
		hst = HistoryScheduleTable(date=ymd, iid_id=row[0], carnum=row[1], time=row[2], addr=row[3], alist=row[4], tflag=row[5], lflag=row[6], req=row[7])
		hst.save()
		for sid in row[8]:
			try:
				student = StudentInfo.objects.get(id=sid)
				hst.members.add(student)
			except StudentInfo.DoesNotExist:
				print "sid = " + str(sid) + " doesn't exist"
		for aid in row[4]:
			try:
				academy = Academy.objects.get(id=aid)
				hst.academies.add(academy)
			except Academy.DoesNotExist:
				print "aid = " + str(aid) + " doesn't exist"
		#time.sleep(1)

def daterange(start_date, end_date):
	for n in range(int ((end_date - start_date).days)):
		yield start_date + timedelta(n)

def run(*args):
	start_date = date(2017, 8, 1)
	end_date = date(2017, 8, 23)
	for single_date in daterange(start_date, end_date):
		cur_date = single_date.strftime("%Y-%m-%d")
		os.system("/home/ubuntu/backup/restore.sh " + cur_date)
		print "cur_date = " + cur_date
		store_historyschedule(single_date)
