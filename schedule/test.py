#!/usr/bin/python
#_*_ coding:utf-8 _*_
import sys, os, re
from schedule.models import Inventory,ScheduleTable,HistoryScheduleTable
from passenger.models import StudentInfo, Academy, ShuttleSchedule, ScheduleDate
from passenger.dateSchedule import timeToDate
reload(sys)
sys.setdefaultencoding('utf-8')
#sys.path.append('/home/ubuntu/curtis/work/django_project')
#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#from django.conf import settings

def get_phonenumber(phonenumber_str):
	phonenumber_str.replace('-', '')
	return int(phonenumber_str)


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
		text = schedule.schedule
		lines = text.splitlines()
		for line in lines:
			if line:
				line = re.sub(r"^\s*\(\s*", "", line)
				#line = re.sub(r"\s*\)\s*$", "", line)
				line.replace(u'결석', "")
				matchObj = re.match(r"(\d+:\d+) \[(.*?)\]\s*(.*)", line)
				if (matchObj == None):
					matchObj = re.match(r"(\d+:\d+) (.*)", line)
					if (matchObj == None):
						# parse error
						print "************ check it id =", schedule.id
					elif matchObj.group(2) == u"출발":
						# '[출발]' 이 아니라 '출발'
						#print "************ start"
						pass
					continue

				# regular case
				if matchObj.group(2) == u"출발" or matchObj.group(2) == u"도착":
					continue
				elif matchObj.group(2) == u"등원" or matchObj.group(2) == u"하원":
					m = re.match(r"([^,]+)\s+(.*)", matchObj.group(3))
					if (m == None):
						print "No Student"
					else:
						# new
						if matchObj.group(2) == u"등원" : 
							lflag = '1'
						else :
							lflag = '2'
						students = re.sub(r"\(.*?\)", "", m.group(2))
						students = re.sub(r"\[.*?\]", "", students)
						studentsList = students.split(",")
						for student in studentsList:
							student = student.strip()
							if not student: 
								continue
							# Do the job
							slist = []
							alist = []
							tflags = []
							snamelist = []
							studentinfolist = StudentInfo.objects.filter(sname = student)
							if (len(studentinfolist) == 0) :
								print "No Student", student
							elif (len(studentinfolist) > 1) :
								print "Duplicated Student", student
							else :
								slist.append(studentinfolist[0].id)
								alist.append(studentinfolist[0].aid)
								tflags.append(0)
								snamelist.append(student)
								scheduletable = ScheduleTable(iid_id = schedule.id, time = schedule.time, addr = m.group(1), alist = alist, slist = slist, sname = student, tflag = tflags, lflag = lflag)
								pass
								#scheduletable.sname.append(studentinfo.sname)
								#scheduletable.tflag.append('0')
						#scheduletable.save()
					continue
				else:
					print "You should move it manually id = " , schedule.id
					break
