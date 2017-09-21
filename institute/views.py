# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from passenger.models import Academy, StudentInfo, PersonalInfo
from schedule.models import Branch, HistoryScheduleTable
from util.PhoneNumber import CleanPhoneNumber, FormatPhoneNumber
from util.PersonalInfoUtil import compareLists, saveNewPersonInfo2
from django.utils import timezone
import datetime
import re
from django.db.models import Min
import math

# Create your views here.

class BeautifyStudent :
	def __init__(self):
		self.info = ''
		self.phonenumber = ''
		self.other_phone = False
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

	redirect_url = request.META.get('HTTP_REFERER', 'http://' + request.META.get('SERVER_NAME') + '/institute/listStudents')
	#if (request.META['HTTP_REFERER'] == None):
		#redirect_url = 'http://' + request.META['SERVER_NAME'] + '/institute/listStudents'
	#else:
		#redirect_url = request.META['HTTP_REFERER']

	if institute:
		try:
			academy = Academy.objects.get(name = institute)
		except AcademyDeosNotExist:
			return render(request, 'message.html', {'msg': "학원 검색에 실패했습니다.", 'redirect_url': redirect_url})
	else:
		return render(request, 'message.html', {'msg': "학원 권한이 필요합니다.", 'redirect_url': redirect_url})

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
		beautifyStudent.other_phone = student.grandparents_phonenumber or student.parents_phonenumber or student.self_phonenumber

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
		return render(request, 'message.html', {'msg': "존재하지 않는 학생입니다.", 'redirect_url': request.META.get('HTTP_REFERER')})

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
			return render(request, 'message.html', {'msg': "학원 검색에 실패했습니다.", 'redirect_url': request.META.get('HTTP_REFERER')})
	else:
		return render(request, 'message.html', {'msg': "학원 권한이 필요합니다.", 'redirect_url': request.META.get('HTTP_REFERER')})

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
			return render(request, 'message.html', {'msg': "동일한 학생이 존재합니다.", 'redirect_url': request.META.get('HTTP_REFERER')})


	rv = True
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
			rv = saveNewPersonInfo2(studentinfo)

	except StudentInfo.DoesNotExist:
		# add PersnoalInfo if there is no record
		rv = saveNewPersonInfo2(studentinfo)

	if (rv == False):
		return render(request, 'message.html', {'msg': '학원생 추가 실해했습니다. error : Too many retry for make random pin_number', 'redirect_url': request.META.get('HTTP_REFERER')})

	studentinfo.save()

	return render(request, 'message.html', {'msg': "학원생 추가 성공했습니다.", 'redirect_url': request.META.get('HTTP_REFERER')})
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
		return render(request, 'message.html', {'msg': "학생 수정에 에러가 발생했습니다.", 'redirect_url': request.META.get('HTTP_REFERER')})

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
		return render(request, 'message.html', {'msg': msg, 'redirect_url': request.META.get('HTTP_REFERER')})

	student.deleted_date = timezone.now()
	student.save(update_fields=['deleted_date'])

	msg = "'" + student.sname + "' 학생이 삭제되었습니다."

	return render(request, 'message.html', {'msg': msg, 'redirect_url': request.META.get('HTTP_REFERER')})


@login_required
def addClassForm(request):
	return render(request, 'addClassForm.html')

class TimeHistory:
	BILLING_NORMAL = 0b0000
	BILLING_OVERPEOPLE = 0b0001
	BILLING_PASSENGER = 0b0010
	BILLING_OVERTIME = 0b0100
	BILLING_NONCHARGE = 0b1000
	def __init__(self):
		self.carnum = -1
		self.academies = set()
		self.scheduletable = list()
		self.warning = False
		self.first_time = 0
		self.last_time = 0
                self.lflag = False
		self.studentnum = 0

class DailyHistory:
	def __init__(self):
		self.date = ""
		self.weekday = ""
		self.billing_code = 0
		self.timehistory = list()

## HH:MM ==> HHMM
def convertDateFormat(str):
	ret = str.replace(':', '')
	#ret.replace(':', '')
	return int(ret)

def maskingName(str):
	return str[:1] + '**'

def convertMins(timestr):
	timestr = timestr.strip()
	mins = int(timestr[:2]) * 60 + int(timestr[3:])
	return mins

def chooseBillingCode(academy, first_time, last_time, isShare, student_num, passenger):
	code = 0
	overtime = 35

	if (academy.bid == 11 or academy.bid == 12):
		overtime = 50

	if (student_num <= 0):
		code = TimeHistory.BILLING_NONCHARGE | code

	## overtime 과 overpeople 은 동시에 setting 되지 않음
	if ((not isShare) and (last_time - first_time > overtime)):
		code = TimeHistory.BILLING_OVERTIME | code
	elif (student_num > 5):
		code = TimeHistory.BILLING_OVERPEOPLE | code
	if (passenger == True):
		code = TimeHistory.BILLING_PASSENGER | code

	if (code == 0):
		code = TimeHistory.BILLING_NORMAL 

	return code

@csrf_exempt
@login_required
def getHistory(request):
    if request.user.is_staff :
        institute = request.session.get('institute', None)
    else :
        institute = request.user.first_name

    if institute:
        try:
            academy = Academy.objects.get(name = institute)
        except AcademyDeosNotExist:
            return render(request, 'message.html', {'msg': "학원 검색에 실패했습니다.", 'redirect_url': request.META.get('HTTP_REFERER')})
    else:
        return render(request, 'message.html', {'msg': "학원 권한이 필요합니다.", 'redirect_url': request.META.get('HTTP_REFERER')})

    rv = checkAuth(request)
    if (rv != None):
        return rv

    carid = 0

    if request.method == 'GET':
    	aid = request.GET.get('aid')
    	daterange = request.GET.get('daterange')
        startdate = request.GET.get('startdate')
        enddate = request.GET.get('enddate')
        carid = request.GET.get('carid')
    elif request.method == 'POST':
    	aid = request.POST.get('aid')
    	daterange = request.POST.get('daterange')
        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        carid = request.POST.get('carid')

    if (carid == None or carid == 'all'):
        carid = 0
    else:
        carid = int(carid)

    if daterange is not None and daterange != '':
    	(startdate, enddate) = daterange.split(' - ')

    history = []

    total_count = 0
    aname = ""
    academy = None
    day_dict = {'Mon':'월', 'Tue':'화', 'Wed':'수', 'Thu':'목', 'Fri':'금', 'Sat':'토', 'Sun':'일'}
    cars = set()

    overtime = 30


    if aid is not None and aid != '' and startdate is not None and startdate != '' and enddate is not None and enddate != '':
        start_date = datetime.date(*map(int, startdate.split('-')))
        end_date = datetime.date(*map(int, enddate.split('-')))
        total_days = (end_date - start_date).days + 1
        academy = Academy.objects.get(id=aid)
	#aname = Academy.objects.get(pk=aid).name

        if (academy.bid == 11 or academy.bid == 12):
            overtime = 45

        for day_number in range(total_days):
            single_date = (start_date + datetime.timedelta(days = day_number)).strftime('%Y-%m-%d')
            schedules = []

            #iids = HistoryScheduleTable.objects.filter(alist__contains = [aid]).filter(date = single_date).values_list('iid_id', flat=True).distinct()
            uniq_iids = HistoryScheduleTable.objects.filter(alist__contains = [aid]).filter(date = single_date).values('iid_id').annotate(min_time = Min('time')).order_by('min_time').values_list('iid_id', flat=True)

            last_time = 0
            dailyHistory = DailyHistory()
            dailyHistory.date = single_date
            dailyHistory.weekday = day_dict[(start_date + datetime.timedelta(days = day_number)).strftime('%a')]
            for i in uniq_iids:
                scheduletable = HistoryScheduleTable.objects.filter(date = single_date).order_by('time').filter(iid_id = i)
                if len(scheduletable) > 0:

                    timeHistory = TimeHistory()
                    timeHistory.scheduletable = scheduletable
                    timeHistory.carnum = scheduletable[0].carnum
                    cars.add(timeHistory.carnum)
                    index = 0
                    studentNum = 0
                    sharingFlag = False
                    isPassenger = False
                    lflag_on_count = 0
                    lflag_off_count = 0
                    for schedule in scheduletable:
                        #timeHistory.studentnum += schedule.members.count()
                        for student in schedule.members.all():
                            if student.aid != academy:
                                sharingFlag = True
                            else:
                                studentNum += 1
                                timeHistory.studentnum += 1
				for offmember in schedule.offmembers.all():
					if (offmember == student):
                                                #return HttpResponse("offmember = " + str(offmember.id))
						studentNum -= 1
                                if ((student.birth_year == None) or ((datetime.datetime.now().year - int(student.birth_year) + 1) <= 13)):
                                    isPassenger = True

                        if (schedule.lflag == 1):
                                lflag_on_count += 1
                        elif (schedule.lflag == 0):
                                lflag_off_count += 1

                        for aca in schedule.academies.all():
		            timeHistory.academies.add(aca.name)

                        if (index == 0):
                            timeHistory.first_time = convertMins(schedule.time)
                        timeHistory.last_time = convertMins(schedule.time)
                        index += 1

                    if (lflag_on_count > lflag_off_count):
                        timeHistory.lflag = True

                    timeHistory.billing_code = chooseBillingCode(academy, timeHistory.first_time, timeHistory.last_time, sharingFlag, studentNum, isPassenger)
                    if (timeHistory.billing_code & TimeHistory.BILLING_NONCHARGE):
                        timeHistory.warning = True
                    dailyHistory.timehistory.append(timeHistory)
                    total_count += 1
            if len(dailyHistory.timehistory) > 0:
                history.append(dailyHistory)


            standard_h = None
            warning_set = set()
            studentNum = 0
            for h in dailyHistory.timehistory:
                fire = False

                if ((standard_h == None) or (standard_h.last_time <= h.first_time)):
                    if (len(warning_set) > 0):
                        # warning 처리
                        # 학생 수가 많아서 어쩔 수 없이 차량이 많아진 경우는 maxvehicle 보다 우선시한다.
                        maxvehicle = max(academy.maxvehicle, int(math.ceil(float(studentNum)/10.0)))
                        if (len(warning_set) > maxvehicle):
                            sorted_warning = sorted(warning_set, key=lambda timehistory: timehistory.billing_code, reverse=True)
                            for i_warning in range(maxvehicle, len(sorted_warning)):
                                sorted_warning[i_warning].warning = True 
                    standard_h = h
                    warning_set = set()
                    studentNum = h.studentnum
                    if not (h.billing_code & TimeHistory.BILLING_NONCHARGE):
                        warning_set.add(h)
                else:
                    studentNum += h.studentnum
                    if not (h.billing_code & TimeHistory.BILLING_NONCHARGE):
                        warning_set.add(h)

		#if (h.warning == True):
			#continue

		#maxvehicle = academy.maxvehicle

                #studentNum = h.studentnum
                #for inner_h in dailyHistory.timehistory:
                    #if (fire == False and h != inner_h):
                        #continue
                    #elif (h == inner_h):
                        #fire = True
                    #else:
                        #if (h.lflag == inner_h.lflag and h.last_time > inner_h.first_time):
                            #studentNum += inner_h.studentnum
                            #if not (h.billing_code & TimeHistory.BILLING_NONCHARGE):
                                #warning_set.add(h)
                    	    #if not (inner_h.billing_code & TimeHistory.BILLING_NONCHARGE):
                                #warning_set.add(inner_h)

                #necessaryVehicle = int(math.ceil(float(studentNum)/10.0))
                #if (necessaryVehicle > maxvehicle):
                    #maxvehicle = necessaryVehicle

                #if (len(warning_set) > maxvehicle):
                    #sorted_warning = sorted(warning_set, key=lambda timehistory: timehistory.billing_code, reverse=True)
                    #for i_warning in range(maxvehicle, len(sorted_warning)):
                        #sorted_warning[i_warning].warning = True


        rem = 0
        if (carid != 0):
            for dailyHistory in history:
                dailyHistory.timehistory[:] = [x for x in dailyHistory.timehistory if x.carnum == carid]

    return render(request, 'getHistory.html', {"history": history, "academy" : academy, 'total_count': total_count, 'startdate': startdate, 'enddate': enddate, 'user':request.user, 'cars':sorted(cars), 'carid':carid, 'overtime':overtime})


@login_required
def addAcademyForm(request):
	rv = checkAuth(request)
	if (rv != None):
		return rv

	return render(request, 'addAcademyForm.html', )

@login_required
def updateAcademy(request):
	rv = checkAuth(request)
	if (rv != None):
		return rv

	aid = request.GET.get('aid')
	academy = Academy.objects.get(id = aid)

	return render(request, 'addAcademyForm.html', {'academy' : academy})

