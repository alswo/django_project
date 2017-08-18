#-*- coding: utf-8 -*-
from passenger.models import StudentInfo, PersonalInfo
from schedule.models import Branch
from django.utils.crypto import get_random_string
import re

import sys

def getHangul(str):
	#hangul = re.compile('[\u3131-\u3163\uac00-\ud7a3]+')
	#hangul = re.compile('([\xE0-\xFF][\x80-\xFF][\x80-\xFF])+')
	hangul = re.compile(u'([\uAC00-\uD7A3])+')
	m = hangul.match(str)
	if (m==None):
		sys.stderr.write("str = [" + str + "]:none\n")
		sys.exit()
		
	if (str != m.group()):
		sys.stderr.write("str = [" + str + "] ==> [" + m.group() + "]\n")

	return m.group()

def compareLists(name1, item1, list1, name2, item2, list2):
        if (getHangul(name1) != getHangul(name2)):
		#print "name not equal"
		return False

	if ((len(str(item1)) < 9) or (len(str(item2)) < 9)):
		#print "length error"
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

def findSamePerson(student1, student2):
	if (student1.bid == student2.bid and getHangul(student1.sname) == getHangul(student2.sname)):
		list1 = []
		list1.append(student1.parents_phonenumber)
		list1.append(student1.grandparents_phonenumber)
		list1.append(student1.self_phonenumber)
		list2 = []
		list2.append(student1.parents_phonenumber)
		list2.append(student1.grandparents_phonenumber)
		list2.append(student1.self_phonenumber)

		if not set(list1).isdisjoint(list2):
			return True

	return False

def findSibling(student1, student2):
	if (student1.bid == student2.bid):
		list1 = []
		list1.append(student1.parents_phonenumber)
		list1.append(student1.grandparents_phonenumber)
		list1.append(student1.self_phonenumber)
		list2 = []
		list2.append(student1.parents_phonenumber)
		list2.append(student1.grandparents_phonenumber)
		list2.append(student1.self_phonenumber)

		if not set(list1).isdisjoint(list2):
			return True

	return False


def saveNewPersonInfo(student):
	# for sibling
	pin_number = get_random_string(length=7)
	others = StudentInfo.objects.filter(bid = student.bid)
	for other in others:
		if compareLists(student.sname, student.phone1, student.phonelist, other.sname, other.phone1, other.phonelist):
			student.personinfo = other.personinfo
			student.save()
			break

	siblings = StudentInfo.objects.filter(bid = student.bid)
	for sibling in siblings:
		# different name but same phone number
		if compareLists(u"가", student.phone1, student.phonelist, u"가", sibling.phone1, sibling.phonelist):
			if (sibling.personinfo):
				pin_number = sibling.personinfo.pin_number
				break

	person = PersonalInfo(pin_number = pin_number)
	person.save()
	student.personinfo = person
	student.save(update_fields=['personinfo'])
	
def saveNewPersonInfo2(student):
	# for sibling
	pin_number = get_random_string(length=7)
	others = StudentInfo.objects.filter(bid = student.bid)
	for other in others:
		if findSamePerson(student, other):
			student.personinfo = other.personinfo
			student.save()
			return

	siblings = StudentInfo.objects.filter(bid = student.bid)
	for sibling in siblings:
		if findSibling(sibling, student):
			if (sibling.personinfo):
				pin_number = sibling.pin_number
				break

	person = PersonalInfo(pin_number = pin_number)
	person.save()
	student.personinfo = person
	student.save()
	
