#-*- coding: utf-8 -*-
import sys
import os, django
from django.conf import settings
from passenger.models import StudentInfo, PersonalInfo
from django.utils.crypto import get_random_string
from util.PersonalInfoUtil import compareLists, saveNewPersonInfo

def run():
	students = StudentInfo.objects.all()
	i = 0
	print "len = " + str(len(students))
	for student in students:
		try:
			people = PersonalInfo.objects.filter(name = student.sname, branch_id = student.bid)
			found = False
			for person in people:
				try :
					another = StudentInfo.objects.get(personinfo = person)
				except :
					#print "person.id = " + str(person.id)
					#print "student.sname = " + student.sname
					continue
				if compareLists(student.phone1, student.phonelist, another.phone1, another.phonelist):
					student.personinfo = person
					student.save(update_fields=['personinfo'])
					found = True
					break
			if (found == False):
				saveNewPersonInfo(student)
			
		except PersonalInfo.DoesNotExist:
			# add PersnoalInfo if there is no record
			saveNewPersonInfo(student)

		sys.stderr.write("[" + str(i) + "] " + student.sname + "\n")
		i += 1
	
	print "end"
