#-*- coding: utf-8 -*-
import sys
import os, django
from django.conf import settings
from passenger.models import StudentInfo, PersonalInfo
from django.utils.crypto import get_random_string

def compareLists(item1, list1, item2, list2):
	if ((len(str(item1)) < 9) or (len(str(item2)) < 9)):
		return False

	compList1 = []
	if (list1 != None):
		for item in list1:
			if (len(str(item)) >= 9) :
				compList1.append(item)
	compList1.append(item1)

	compList2 = []
	if (list2 != None):
		for item in list2:
			if (len(str(item)) >= 9) :
				compList2.append(item)
	compList2.append(item2)

	if compList1 == None or compList2 == None:
		return False

	return not set(compList1).isdisjoint(compList2)

def saveNewPersonInfo(student):
	# for sibling
	people = PersonalInfo.objects.all()
	pin_number = get_random_string(length=20)
	#sys.stderr.write("pin_number = " + pin_number)
	for person in people:
		try : 
			another = StudentInfo.objects.get(personinfo = person, bid = student.bid)
		except :
			continue
		if compareLists(student.phone1, student.phonelist, another.phone1, another.phonelist):
			pin_number = person.pin_number
			break

	# use existing pin_number
	#sys.stderr.write("end of loop")
	
	person = PersonalInfo(name = student.sname, pin_number = pin_number)
	person.save()
	student.personinfo = person
	student.save(update_fields=['personinfo'])
	
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
