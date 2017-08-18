# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from passenger.models import Academy, StudentInfo, PersonalInfo
from schedule.models import Branch
from util.PhoneNumber import CleanPhoneNumber, FormatPhoneNumber
from util.PersonalInfoUtil import compareLists, saveNewPersonInfo2
from datetime import datetime
import re

# Create your views here.

class BeautifyStudent :
	def __init__(self):
		self.info = ''
		self.phonenumber = ''
		self.age = None


def compareStudents(student1, student2):
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

@login_required
def setSession(request):
	instituteid = request.GET.get('instituteid')
	try:
		request.session['instituteid'] = int(instituteid)
		request.session['institute'] = Academy.objects.get(id = instituteid).name
	except Academy.DoesNotExist:
		del request.session['institute']
		del request.session['instituteid']

	return HttpResponse(request.session.get('institute', None))

@login_required
def listStudents(request):
	if request.user.is_staff :
		institute = request.session.get('institute', None)
	else :
		institute = request.user.first_name

	if institute:
		academy = Academy.objects.get(name = institute)
		students = StudentInfo.objects.filter(aid_id = academy.id).order_by('sname')
	else:
		students = StudentInfo.objects.all().order_by('sname')

	beautifyStudents = []
	for student in students:
		beautifyStudent = BeautifyStudent()
		beautifyStudent.info = student
		beautifyStudent.phonenumber  = FormatPhoneNumber(student.parents_phonenumber)
		if (student.birth_year):
			beautifyStudent.age = datetime.now().year - int(student.birth_year) + 1
		beautifyStudents.append(beautifyStudent)

	return render(request, 'listStudents.html', {'students': beautifyStudents});

@login_required
def addStudentsForm(request):
	return render(request, 'addUpdateStudentsForm.html', )

@login_required
def updateStudentsForm(request):
	sid = request.GET.get('sid')
	try:
		student = StudentInfo.objects.get(id=sid)
	except StudentInfo.DoesNotExist:
		return HttpResponse("존재하지 않는 학생입니다.")

	age = None
	if (student.birth_year):
		age = datetime.now().year - int(student.birth_year) + 1
	return render(request, 'addUpdateStudentsForm.html', {'student': student, 'age': age})

@csrf_exempt
@login_required
def addStudents(request):
	if request.user.is_staff :
		institute = request.session.get('institute', None)
	else :
		institute = request.user.first_name

	if institute:
		try:
			academy = Academy.objects.get(name = institute)
		except AcademyDeosNotExist:
			return HttpResponse("학원 검색에 실패했습니다.")
	else:
		return HttpResponse("학원 권한이 필요합니다.")

	bname = Branch.objects.get(id=academy.bid).bname
	aid = Academy.objects.get(name=institute).id
	sname = request.POST.get('sname')
	if sname:
		sname.strip()
	parents_phonenumber = CleanPhoneNumber(request.POST.get('parents_phonenumber'))
	grandparents_phonenumber = CleanPhoneNumber(request.POST.get('grandparents_phonenumber'))
	self_phonenumber = CleanPhoneNumber(request.POST.get('self_phonenumber'))
	care_phonenumber = CleanPhoneNumber(request.POST.get('care_phonenumber'))
	age = request.POST.get('age')
	billing_date = request.POST.get('billing_date')
	if age:
		birth_year = str(datetime.now().year - int(age) + 1)
	else:
		brith_year = "1900"

	birmon = request.POST.get('birmon')
	birday = request.POST.get('birday')

	if (birmon and birday):
		birthday = '%02d%02d' % (int(birmon), int(birday))

	students = StudentInfo.objects.filter(bid=academy.bid, aid=aid, sname=sname)
	studentinfo = StudentInfo(bid=academy.bid, sname=sname, bname=bname, phone1=0, aid=aid, aname=institute, parents_phonenumber=parents_phonenumber, grandparents_phonenumber=grandparents_phonenumber, self_phonenumber=self_phonenumber, care_phonenumber=care_phonenumber, birth_year=birth_year, billing_date=billing_date, phonelist=None)

	# same person in the same academy
	for student in students:
		if compareStudents(student, studentinfo):
			return HttpResponse("동일한 학생이 존재합니다.")


	# for PersonalINfo
	# same person in another academy
	try:
		people = PersonalInfo.objects.filter(name = studentinfo.sname, branch_id = studentinfo.bid)
		found = False
		for person in people:
			try :
				another = StudentInfo.objects.get(personinfo = person)
			except :
				continue
			if compareStudents(studentinfo, another):
				studentinfo.personinfo = person
				#studentinfo.save(update_fields=['personinfo'])
				found = True
				break
		if (found == False):
			saveNewPersonInfo2(studentinfo)

	except PersonalInfo.DoesNotExist:
		# add PersnoalInfo if there is no record
		saveNewPersonInfo2(studentinfo)

	studentinfo.save()

	return redirect(addStudentsForm)

@login_required
def addClassForm(request):
	return render(request, 'addClassForm.html')

