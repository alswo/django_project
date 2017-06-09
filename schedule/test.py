#!/usr/bin/python
#_*_ coding:utf-8 _*_
import sys, os, re
from schedule.models import Inventory,ScheduleTable,HistoryScheduleTable
from passenger.models import StudentInfo, Academy, ShuttleSchedule, ScheduleDate, Group
from passenger.dateSchedule import timeToDate
reload(sys)
sys.setdefaultencoding('utf-8')
#sys.path.append('/home/ubuntu/curtis/work/django_project')
#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#from django.conf import settings

#def get_phonenumber(phonenumber_str):
	#phonenumber_str.replace('-', '')
	#return int(phonenumber_str)


#def regist_student():
	#f = open("a.txt", "r")
	#while True:
		#line = f.readline()
		#if not line: break
		#words = line.split(',')
		#academylist = Academy.objects.filter(name = words[y])
		#aname = ''
		#if len(academylist) == 0:
			#print "Check the academy name:", words[y]
			#break
		#else:
			#aname = academylist[0].name
			#aid = academylist[0].id
			#branch = Branch.objects.get(id = academylist[0].bid)
			#bname = branch.bname
#
		#studentlist = StudentInfo.objects.filter(sname = words[x])
		#if len(studentlist) == 0:
			#StudentInfo(sname = words[x], aname = aname, aid = aid, bname = bname, grade = '', phone1 = get_phonenumber(words[z]), phonelist = 
	#f.close()

def move_schedule():
	schedules = ShuttleSchedule.objects.all()
	for schedule in schedules:
		#print "id = ", schedule.id
		if schedule.aid == 7 :
			continue
		groups = Group.objects.filter(gid = schedule.gid)
		carnum = re.sub(unicode(r"호차", 'utf-8'), "", groups[0].gname)
		anamelist = schedule.a_name.split('&')
		anamel = []
		for aname in anamelist:
			anamel.append(aname.strip())
		alist = []
		for academy in anamelist:
			academy = academy.strip()
			if academy == u'프리모':
				academy = '프리모음악학원'

			academies = Academy.objects.filter(name = academy)
			if len(academies) == 0:
				print "no academy : [", academy, "]"
			else:
				alist.append(academies[0].id)
		
		try :
			snum = len(schedule.slist)
			inventory = Inventory(carnum = carnum, bid = schedule.bid, day = schedule.day, snum = snum, alist=alist, slist = schedule.slist, anamelist = anamel, stime = 0, etime = 0)
			inventory.save()
		except Exception as e: 
			print "exception: ", str(e)
		
		text = schedule.schedule
		lines = text.splitlines()
		for line in lines:
			if line:
				print line
				line = re.sub(r"^\s*\(\s*", "", line)
				#line = re.sub(r"\s*\)\s*$", "", line)
				line.replace(u'결석', "")
				matchObj = re.match(r"(\d+:\d+) \[(.*?)\]\s*(.*)", line)
				if (matchObj == None):
					matchObj = re.match(r"(\d+:\d+) (.*)", line)
					if (matchObj == None):
						# parse error
						print "************ check it id =", schedule.id
						continue
					elif matchObj.group(2) == u"출발":
						# '[출발]' 이 아니라 '출발'
						#print "************ start"
						pass

				# regular case
				if matchObj.group(2) == u"출발" or matchObj.group(2) == u"도착":
					if matchObj.group(2) == u"출발":
						lflag = 2
					else:
						lflag = 3
					scheduletable = ScheduleTable(iid_id = inventory.id, time = matchObj.group(1), alist = [], slist = [], sname = [], tflag = [], lflag = lflag)
					scheduletable.save()
				elif matchObj.group(2) == u"등원" or matchObj.group(2) == u"하원":
					m = re.match(r"([^,]+)\s+(.*)", matchObj.group(3))
					if (m == None):
						print "Parse Error No Student id = ", schedule.id
					else:
						lflag = 1
						# new
						if matchObj.group(2) == u"등원" : 
							lflag = 0
						else :
							lflag = 1
						students = re.sub(r"\(.*?\)", "", m.group(2))
						students = re.sub(r"\[.*?\]", "", students)
						studentsList = students.split(",")
						scheduletable = ScheduleTable(iid_id = inventory.id, time = matchObj.group(1), addr = m.group(1), alist = [], slist = [], sname = [], anamelist = [], tflag = [], lflag = lflag)
						#print "else", students
						for student in studentsList:
							student = student.strip()
							student = re.sub(r"\*\*$", "", student)
							#print "student: ", student
							if not student: 
								continue
							# Do the job
							studentinfolist = StudentInfo.objects.filter(sname = student)
							if (len(studentinfolist) == 0) :
								print "No Student", student, " id = ", schedule.id
							elif (len(studentinfolist) > 1) :
								print "Duplicated Student", student, " id = ", schedule.id
							else :
								scheduletable.slist.append(studentinfolist[0].id)
								scheduletable.alist.append(studentinfolist[0].aid[0])
								scheduletable.tflag.append(0)
								scheduletable.sname.append(student)
								scheduletable.anamelist.append(studentinfolist[0].aname[0])
								#pass
						try:
							scheduletable.save()
						except Exception as e: 
							print "exception: ", str(e)
					continue
				else:
					print "You should move it manually id = " , schedule.id
					break
