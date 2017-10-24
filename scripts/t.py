#-*- coding: utf-8 -*-
from util.PhoneNumber import CleanPhoneNumber, FormatPhoneNumber
from util.PersonalInfoUtil import findSibling, findSamePerson
from passenger.models import StudentInfo

created_time = '2017-10-23 00:00:00'

def run():
	students = StudentInfo.objects.all()

	for student in students:
		otherStudents = StudentInfo.objects.filter(bid = student.bid).exclude(id=student.id)
		for otherStudent in otherStudents:
				if (findSamePerson(student, otherStudent) == True):
					print "id [" + str(student.id) + ", " + str(otherStudent.id) + "] same person" 
				if (findSibling(student, otherStudent) == True):
					print "id [" + str(student.id) + ", " + str(otherStudent.id) + "] sibling person" 
	
