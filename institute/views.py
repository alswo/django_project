# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from passenger.models import Academy, StudentInfo, PersonalInfo
from schedule.models import Branch
from util.PhoneNumber import CleanPhoneNumber, FormatPhoneNumber
from util.PersonalInfoUtil import compareLists, saveNewPersonInfo2
from django.utils import timezone
import re

# Create your views here.

class BeautifyStudent :
	def __init__(self):
		self.info = ''
		self.phonenumber = ''
		self.age = None
		self.billing_date = None


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

def checkAuth(request):
	if request.user.is_staff :
		institute = request.session.get('institute', None)
	else :
		institute = request.user.first_name

	if institute:
		try:
			academy = Academy.objects.get(name = institute)
		except AcademyDeosNotExist:
			return render(request, 'message.html', {'msg': "학원 검색에 실패했습니다.", 'redirect_url': request.META['HTTP_REFERER']})
	else:
		return render(request, 'message.html', {'msg': "학원 권한이 필요합니다.", 'redirect_url': request.META['HTTP_REFERER']})

	return None


@login_required
def listStudents(request):
	if request.user.is_staff :
		institute = request.session.get('institute', None)
	else :
		institute = request.user.first_name

	if institute:
		academy = Academy.objects.get(name = institute)
		students = StudentInfo.objects.filter(aid_id = academy.id).filter(deleted_date__isnull=True).order_by('sname')
	else:
		students = StudentInfo.objects.all().filter(deleted_date__isnull=True).order_by('sname')

	beautifyStudents = []
	for student in students:
		beautifyStudent = BeautifyStudent()
		beautifyStudent.info = student
		beautifyStudent.phonenumber  = FormatPhoneNumber(student.parents_phonenumber)
		if (student.birth_year):
			beautifyStudent.age = timezone.now().year - int(student.birth_year) + 1
		beautifyStudents.append(beautifyStudent)

	return render(request, 'listStudents.html', {'students': beautifyStudents});

@login_required
def addStudentsForm(request):
	rv = checkAuth(request)
	if (rv != None):
		return rv

	return render(request, 'addUpdateStudentsForm.html', )

@login_required
def updateStudentsForm(request):
	rv = checkAuth(request)
	if (rv != None):
		return rv

	sid = request.GET.get('sid')
	try:
		student = StudentInfo.objects.get(id=sid)
	except StudentInfo.DoesNotExist:
		return render(request, 'message.html', {'msg': "존재하지 않는 학생입니다.", 'redirect_url': request.META['HTTP_REFERER']})

	beautifyStudent = BeautifyStudent()
	beautifyStudent.info = student
	if (student.birth_year):
		beautifyStudent.age = timezone.now().year - int(student.birth_year) + 1
	if (student.billing_date):
		beautifyStudent.billing_date = int(student.billing_date)
	return render(request, 'addUpdateStudentsForm.html', {'student': beautifyStudent})

@csrf_exempt
@login_required
def addStudent(request):
	if request.user.is_staff :
		institute = request.session.get('institute', None)
	else :
		institute = request.user.first_name

	if institute:
		try:
			academy = Academy.objects.get(name = institute)
		except AcademyDeosNotExist:
			return render(request, 'message.html', {'msg': "학원 검색에 실패했습니다.", 'redirect_url': request.META['HTTP_REFERER']})
	else:
		return render(request, 'message.html', {'msg': "학원 권한이 필요합니다.", 'redirect_url': request.META['HTTP_REFERER']})

	bname = Branch.objects.get(id=academy.bid).bname
	academy = Academy.objects.get(name=institute)
	sname = request.POST.get('sname')
	if sname:
		sname.strip()
	parents_phonenumber = CleanPhoneNumber(request.POST.get('parents_phonenumber'))
	grandparents_phonenumber = CleanPhoneNumber(request.POST.get('grandparents_phonenumber'))
	self_phonenumber = CleanPhoneNumber(request.POST.get('self_phonenumber'))
	care_phonenumber = CleanPhoneNumber(request.POST.get('care_phonenumber'))
	age = request.POST.get('age')
	billing_date = request.POST.get('billing_date')
	birth_year = None
	if age:
		birth_year = str(timezone.now().year - int(age) + 1)

	birmon = request.POST.get('birmon')
	birday = request.POST.get('birday')

	if (birmon and birday):
		birthday = '%02d%02d' % (int(birmon), int(birday))

	students = StudentInfo.objects.filter(bid=academy.bid, aid=academy, sname=sname)
	studentinfo = StudentInfo(bid=academy.bid, sname=sname, bname=bname, phone1=0, aid=academy, aname=institute, parents_phonenumber=parents_phonenumber, grandparents_phonenumber=grandparents_phonenumber, self_phonenumber=self_phonenumber, care_phonenumber=care_phonenumber, birth_year=birth_year, billing_date=billing_date, phonelist=None)

	# same person in the same academy
	for student in students:
		if compareStudents(student, studentinfo):
			return render(request, 'message.html', {'msg': "동일한 학생이 존재합니다.", 'redirect_url': request.META['HTTP_REFERER']})


	# for PersonalINfo
	# same person in another academy
	try:
		found = False
		anotherStudents = StudentInfo.objects.filter(sname = studentinfo.sname, bid = studentinfo.bid)
		for anotherStudent in anotherStudents:
			if compareStudents(studentinfo, anotherStudent):
				studentinfo.personinfo = anotherStudent.personinfo
				#studentinfo.save(update_fields=['personinfo'])
				found = True
				break
		if (found == False):
			saveNewPersonInfo2(studentinfo)

	except StudentInfo.DoesNotExist:
		# add PersnoalInfo if there is no record
		saveNewPersonInfo2(studentinfo)

	studentinfo.save()

	return render(request, 'message.html', {'msg': "학원생 추가 성공했습니다.", 'redirect_url': request.META['HTTP_REFERER']})
	#return redirect(addStudentsForm)

@csrf_exempt
@login_required
def updateStudent(request):
	rv = checkAuth(request)
	if (rv != None):
		return rv

	sid = request.POST.get('sid')

	student = None
	age = None
	try:
		student = StudentInfo.objects.get(id=sid)

		student.sname = request.POST.get('sname')
		student.parents_phonenumber = request.POST.get('parents_phonenumber')
		student.grandparents_phonenumber = request.POST.get('grandparents_phonenumber')
		student.self_phonenumber = request.POST.get('self_phonenumber')
		student.care_phonenumber = request.POST.get('care_phonenumber')
		if (request.POST.get('age')):
			age = int(request.POST.get('age'))
			student.birth_year = str(timezone.now().year - age + 1)
		if (request.POST.get('billing_date')):
			student.billing_date = request.POST.get('billing_date')
	except:
		return render(request, 'message.html', {'msg': "학생 수정에 에러가 발생했습니다.", 'redirect_url': request.META['HTTP_REFERER']})

	student.save()
	beautifyStudent = BeautifyStudent()
	beautifyStudent.info = student
	beautifyStudent.age = age
	if (student.billing_date):
		beautifyStudent.billing_date = int(student.billing_date)

	return render(request, 'addUpdateStudentsForm.html', {'student': beautifyStudent})

@login_required
def deleteStudent(request):
	rv = checkAuth(request)
	if (rv != None):
		return rv

	sid = request.GET.get('sid')

	try:
		student = StudentInfo.objects.get(id=sid)
	except:
		msg = "'" + stduent.sname + "' 학생이 존재하지 않습니다."
		return render(request, 'message.html', {'msg': msg, 'redirect_url': request.META['HTTP_REFERER']})

	student.deleted_date = timezone.now()
	student.save(update_fields=['deleted_date'])

	msg = "'" + student.sname + "' 학생이 삭제되었습니다."

	return render(request, 'message.html', {'msg': msg, 'redirect_url': request.META['HTTP_REFERER']})


@login_required
def addClassForm(request):
	return render(request, 'addClassForm.html')


@csrf_exempt
@login_required
def getHistory(request):
    if request.method == 'GET':
    	aid = request.GET.get('aid')
    	daterange = request.GET.get('daterange')
        startdate = request.GET.get('startdate')
        enddate = request.GET.get('enddate')
    elif request.method == 'POST':
    	aid = request.POST.get('aid')
    	daterange = request.POST.get('daterange')
        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')

    if daterange is not None and daterange != '':
    	(startdate, enddate) = daterange.split(' - ')

    history = []
    allacademy = Academy.objects.all().order_by('name')

    total_count = 0
    uniq_count = 0
    aname = ""


    if aid is not None and aid != '' and startdate is not None and startdate != '' and enddate is not None and enddate != '':
        start_date = datetime.date(*map(int, startdate.split('-')))
        end_date = datetime.date(*map(int, enddate.split('-')))
        total_days = (end_date - start_date).days + 1
	aname = Academy.objects.get(pk=aid).name
        for day_number in range(total_days):
            single_date = (start_date + datetime.timedelta(days = day_number)).strftime('%Y-%m-%d')
            schedules = []

            #return HttpResponse(single_date)
            iids = HistoryScheduleTable.objects.filter(alist__contains = [aid]).filter(date = single_date).order_by('time').values_list('iid_id', flat=True).distinct()
            uniq_iids = reduce(lambda x,y: x+[y] if x==[] or x[-1] != y else x, iids, [])

            last_time = 0
            dailyHistory = DailyHistory()
            dailyHistory.date = single_date
            for i in uniq_iids:
                academyset = set()
                scheduletable = HistoryScheduleTable.objects.filter(date = single_date).order_by('time').filter(iid_id = i)
                #return HttpResponse(str(len(scheduletable)))
                if len(scheduletable) > 0:

                    timeHistory = TimeHistory()
                    timeHistory.scheduletable = scheduletable
                    timeHistory.carnum = scheduletable[0].carnum
                    index = 0
                    for schedule in scheduletable:
                        for academy in schedule.academies.all():
		            timeHistory.academies.add(academy.name)

                        if (index == 0 and last_time > convertDateFormat(schedule.time)):
                            timeHistory.warning = 1
                        last_time = convertDateFormat(schedule.time)
                        index += 1

                    dailyHistory.timehistory.append(timeHistory)
                    total_count += 1
                    if (timeHistory.warning != 1):
                        uniq_count += 1
            if len(dailyHistory.timehistory) > 0:
                history.append(dailyHistory)
    #else :
        #return HttpResponse("error occured", "aid = ", aid, "startdate = ", startdate, "enddate = ", enddate)

    return render(request, 'getHistory.html', {"history": history, "academy": allacademy, "aid" : aid, 'aname': aname, 'total_count': total_count, 'uniq_count': uniq_count, 'startdate': startdate, 'enddate': enddate, 'user':request.user})

