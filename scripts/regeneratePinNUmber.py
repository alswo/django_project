#-*- coding: utf-8 -*-
import sys
import os, django
from django.conf import settings
from passenger.models import StudentInfo, PersonalInfo
from django.utils.crypto import get_random_string
from django.db.models import Q
from util.PersonalInfoUtil import compareLists, saveNewPersonInfo, getHangul
from util.PhoneNumber import FormatPhoneNumber
from django.db import transaction


def isSamePhoneNumber(phone1, phone2):
	if (not phone1 or not phone2):
		return False

	return (phone1 == phone2)

def isSamePerson(student1, student2):
	if (getHangul(student1.sname) != getHangul(student2.sname)):
		return False

	if (isSamePhoneNumber(student1.parents_phonenumber, student2.parents_phonenumber) or isSamePhoneNumber(student1.grandparents_phonenumber, student2.grandparents_phonenumber) or isSamePhoneNumber(student1.self_phonenumber, student2.self_phonenumber)):
		return True

	return False

def isSibling(student1, student2):
	if (isSamePhoneNumber(student1.parents_phonenumber, student2.parents_phonenumber) or isSamePhoneNumber(student1.grandparents_phonenumber, student2.grandparents_phonenumber) or isSamePhoneNumber(student1.self_phonenumber, student2.self_phonenumber)):
		return True

	return False
	
def run():
	students = StudentInfo.objects.all()
	j = 0
	print "len = " + str(len(students))
	pin_number = ""

        #return
	for student in students:
		try:
			# 12 o'clock
			otherStudents = StudentInfo.objects.filter(bid = student.bid, personinfo__created_time__gt = '2017-09-13 02:00').exclude(id=student.id)
			#print "otherStudent len = " + str(len(otherStudents))
			found = False
			for otherStudent in otherStudents:
				if (isSamePerson(student, otherStudent) == True):
					pin_number = otherStudent.personinfo.pin_number
					student.personinfo = otherStudent.personinfo
					student.save(update_fields=['personinfo'])
					found = True
					break

			if (found == False):
				for otherStudent in otherStudents:
					if (isSibling(student, otherStudent) == True):
						pin_number = otherStudent.personinfo.pin_number
						personinfo = PersonalInfo(pin_number = otherStudent.personinfo.pin_number)
						personinfo.save()
						student.personinfo = personinfo
						student.save(update_fields=['personinfo'])
						found = True
						break

			if (found == False):
				for i in range(0, 5):
					try:
						pin_number = get_random_string(length=7)
						personinfos = PersonalInfo.objects.filter(pin_number = pin_number)
						if (len(personinfos) == 0):
							sys.stderr.write(str(i) + "th pin_number [" + pin_number + "] newly created\n")
							raise PersonalInfo.DoesNotExist
						pin_number = None
					except PersonalInfo.DoesNotExist:
						break
				if (pin_number == None):
					print "5 tries failed"
					sys.exit()
				personinfo = PersonalInfo(pin_number = pin_number)
				personinfo.save()
				transaction.commit()
				student.personinfo = personinfo
				student.save(update_fields=['personinfo'])

		except Exception as e:
			print(e)

		sys.stderr.write("[" + str(j) + "] " + student.sname + "==>" + student.personinfo.pin_number + "\n")
		j += 1
		#if (j > 20):
			#break
	
	print "end"
