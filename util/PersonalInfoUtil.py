#-*- coding: utf-8 -*-
from passenger.models import StudentInfo, PersonalInfo
from schedule.models import Branch
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

def findSamePerson(student1, student2):
	if (student1.bid == student2.bid and student1.sname == student2.sname):
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
	people = PersonalInfo.objects.all()
	pin_number = get_random_string(length=7)
	for person in people:
		try : 
			another = StudentInfo.objects.get(personinfo = person, bid = student.bid)
		except :
			continue
		if compareLists(student.phone1, student.phonelist, another.phone1, another.phonelist):
			pin_number = person.pin_number
			break

	person = PersonalInfo(pin_number = pin_number)
	person.save()
	student.personinfo = person
	student.save(update_fields=['personinfo'])
	
def saveNewPersonInfo2(student):
	# for sibling
	people = PersonalInfo.objects.all()
	pin_number = get_random_string(length=7)
	for person in people:
		try : 
			another = StudentInfo.objects.get(personinfo = person, bid = student.bid)
		except :
			continue
		if findSamePerson(student, another):
			pin_number = person.pin_number
			break

	siblings = StudentInfo.objects.filter(bid = student.bid)
	for sibling in siblings:
		if findSibling(sibling, student):
			pin_number = sibling.pin_number
			break

	person = PersonalInfo(pin_number = pin_number)
	person.save()
	student.personinfo = person
	student.save()
	
