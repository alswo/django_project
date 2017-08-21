#-*- coding: utf-8 -*-
import sys
import os, django
from django.conf import settings
from passenger.models import StudentInfo, PersonalInfo
from django.utils.crypto import get_random_string
from django.db.models import Q
from util.PersonalInfoUtil import compareLists, saveNewPersonInfo
from util.PhoneNumber import FormatPhoneNumber

def run():
	students = StudentInfo.objects.all()
	i = 0
	print "len = " + str(len(students))

	#student1 = StudentInfo.objects.get(id = 83)
	#student2 = StudentInfo.objects.get(id = 1234)
#
	#rv = compareLists(student1.sname, student1.phone1, student1.phonelist, student2.sname, student2.phone1, student2.phonelist)
	#sys.stderr.write("rv = " + str(rv) + "\n")

        #return
	for student in students:
		if (student.phone1 and len(str(student.phone1)) >= 9):
			student.parents_phonenumber = '0' + str(student.phone1)
		if (student.grade and student.grade > 0):
			student.birth_year = str(2017 - student.grade + 1)
		student.save(update_fields=['parents_phonenumber', 'birth_year'])
		try:
			otherStudents = StudentInfo.objects.filter(sname = student.sname, bid = student.bid).filter(~Q(id=student.id)).exclude(personinfo__isnull = True)
			found = False
			for otherStudent in otherStudents:
				if compareLists(student.sname, student.phone1, student.phonelist, otherStudent.sname, otherStudent.phone1, otherStudent.phonelist):
					student.personinfo = otherStudent.personinfo
					student.save(update_fields=['personinfo'])
					found = True
					break
			if (found == False):
				saveNewPersonInfo(student)
			
		except StudentInfo.DoesNotExist:
			# add PersnoalInfo if there is no record
			saveNewPersonInfo(student)

		sys.stderr.write("[" + str(i) + "] " + student.sname + "\n")
		i += 1
		#if (i > 50):
			#break
	
	print "end"
