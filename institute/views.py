# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from passenger.models import Academy, StudentInfo, PersonalInfo, BillingHistory
from schedule.models import Branch, HistoryScheduleTable, Poi, Placement, Car
from django.db import connection
from util.PhoneNumber import CleanPhoneNumber, FormatPhoneNumber
from util.PersonalInfoUtil import compareLists, saveNewPersonInfo2, findSamePerson
from django.utils import timezone
import datetime
import re
from django.db.models import Min
from django.db import IntegrityError, transaction
import math
import psycopg2
from django.db import connection
import calendar
import json
from institute.models import BillingHistorySetting
from django.contrib.auth.models import User
from django.http import JsonResponse
from import_export import resources
import xlwt
import xlrd
from institute.forms import XlsInputForm
from schedule.views import getContacts

# Create your views here.
BANKCODES = ['003', '004', '011', '020', '027', '071', '081', '088']

TAYO_SUCCESS = 200
TAYO_ERROR_SAME_PERSON = 400
TAYO_ERROR_SAVE_FAILURE = 500

class BeautifyStudent :
	def __init__(self):
		self.info = ''
		self.phonenumber = ''
		self.other_phone = False
		self.age = None
		self.billing_date = None

class Uncollected :
	def __init__(self):
		self.month = ''
		self.billing_amount = ''
		self.additional_charge = ''
		self.total_charge = ''


def compareStudents(student1, student2):
	if (student1.aid.bid == student2.aid.bid and student1.sname == student2.sname):
		list1 = []
		list1.append(student1.parents_phonenumber)
		list1.append(student1.grandparents_phonenumber)
		list1.append(student1.self_phonenumber)
		list2 = []
		list2.append(student2.parents_phonenumber)
		list2.append(student2.grandparents_phonenumber)
		list2.append(student2.self_phonenumber)

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

	if institute:
		try:
			academy = Academy.objects.get(name = institute)
		except Academy.DoesNotExist:
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
		try:
			academy = Academy.objects.get(name = institute)
		except Academy.DoesNotExist:
			return render(request, 'message.html', {'msg': "학원 검색에 실패했습니다.", 'redirect_url': "http://www.edticket.com/institute/listStudents"})

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

def funcAddStudent(academy_name, student_name, p_number, g_number, s_number, c_number, age):
	if academy_name:
		academy_name.strip()

	if student_name:
		student_name.strip()

	if p_number:
		p_number = str(p_number)
		p_number.strip()

	if g_number:
		g_number = str(g_number)
		g_number.strip()

	if s_number:
		s_number = str(s_number)
		s_number.strip()

	if c_number:
		c_number = str(c_number)
		c_number.strip()

	if age:
		age = str(age)
		age.strip()

	academy = Academy.objects.get(name = academy_name)
	parents_phonenumber = CleanPhoneNumber(p_number)
	grandparents_phonenumber = CleanPhoneNumber(g_number)
	self_phonenumber = CleanPhoneNumber(s_number)
	care_phonenumber = CleanPhoneNumber(c_number)
	birth_year = None
	if (age):
		birth_year = str(timezone.now().year - int(float(age)) + 1)

	students = StudentInfo.objects.filter(aid = academy).filter(deleted_date__isnull=True)
	studentinfo = StudentInfo(sname = student_name, aid = academy, parents_phonenumber = parents_phonenumber, grandparents_phonenumber = grandparents_phonenumber, self_phonenumber = self_phonenumber, care_phonenumber = care_phonenumber, birth_year = birth_year)

	for student in students:
		if findSamePerson(student, studentinfo):
			return TAYO_ERROR_SAME_PERSON

	if (studentinfo.parents_phonenumber or studentinfo.grandparents_phonenumber or studentinfo.self_phonenumber) :
		rv = saveNewPersonInfo2(studentinfo)
		if (rv == False):
			return TAYO_ERROR_SAVE_FAILURE

	studentinfo.save()

	return TAYO_SUCCESS

@csrf_exempt
@login_required
def addStudent(request):
	if request.user.is_staff :
		institute = request.session.get('institute', None)
	else :
		institute = request.user.first_name

	academy = None

	if institute:
		try:
			academy = Academy.objects.get(name = institute)
		except AcademyDeosNotExist:
			return render(request, 'message.html', {'msg': "학원 검색에 실패했습니다.", 'redirect_url': request.META.get('HTTP_REFERER')})
	else:
		return render(request, 'message.html', {'msg': "학원 권한이 필요합니다.", 'redirect_url': request.META.get('HTTP_REFERER')})


	rv = funcAddStudent(institute, request.POST.get('sname'), request.POST.get('parents_phonenumber'), request.POST.get('grandparents_phonenumber'), request.POST.get('self_phonenumber'), request.POST.get('care_phonenumber'), request.POST.get('age'))
	if (rv == TAYO_ERROR_SAME_PERSON):
		return render(request, 'message.html', {'msg': "동일한 학생이 존재합니다.", 'redirect_url': request.META.get('HTTP_REFERER')})
	elif (rv == TAYO_ERROR_SAVE_FAILURE):
		return render(request, 'message.html', {'msg': '학원생 추가 실패했습니다. error : Too many retry for make random pin_number', 'redirect_url': request.META.get('HTTP_REFERER')})


	return render(request, 'message.html', {'msg': "학원생 추가 성공했습니다.", 'redirect_url': request.META.get('HTTP_REFERER')})

@csrf_exempt
@login_required
def updateStudent(request):
	rv = checkAuth(request)
	if (rv != None):
		return rv

	sid = request.POST.get('sid')

	student = None
	age = None
	noPersoninfo = False
	try:
		student = StudentInfo.objects.get(id=sid)

		if ((not student.parents_phonenumber) and (not student.grandparents_phonenumber) and (not student.self_phonenumber)):
			noPersoninfo = True

		student.sname = request.POST.get('sname')
		student.parents_phonenumber = CleanPhoneNumber(request.POST.get('parents_phonenumber'))
		student.grandparents_phonenumber = CleanPhoneNumber(request.POST.get('grandparents_phonenumber'))
		student.self_phonenumber = CleanPhoneNumber(request.POST.get('self_phonenumber'))
		student.care_phonenumber = CleanPhoneNumber(request.POST.get('care_phonenumber'))
		if (request.POST.get('age')):
			age = int(request.POST.get('age'))
			student.birth_year = str(timezone.now().year - age + 1)
		if (request.POST.get('billing_date')):
			student.billing_date = request.POST.get('billing_date')
	except:
		return render(request, 'message.html', {'msg': "학생 수정에 에러가 발생했습니다.", 'redirect_url': request.META.get('HTTP_REFERER')})

	if (noPersoninfo == True):
		saveNewPersonInfo2(student)
	else:
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
	BILLING_NORMAL =         0b00000000
	BILLING_OVERPEOPLE =     0b00000001
	BILLING_PASSENGER =      0b00000010
	BILLING_OVERTIME =       0b00000100
	BILLING_NONCHARGE =      0b00001000
	BILLING_OVERPEOPLE_10 =  0b00010000
	BILLING_OVERPEOPLE_15 =  0b00100000
	BILLING_OVERPEOPLE_20 =  0b01000000
	def __init__(self):
		self.carnum = -1
		self.inventory_id = -1
		self.academies = set()
		self.scheduletable = list()
		self.warning = False
		self.first_time = 0
		self.last_time = 0
                self.lflag = False
		self.studentnum = 0
		self.msg = ''

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

	if (academy.id == 62):
		overtime = 50

	if (student_num <= 0):
		code = TimeHistory.BILLING_NONCHARGE | code

	## overtime 과 overpeople 은 동시에 setting 되지 않음
	if ((not isShare) and (last_time - first_time > overtime)):
		code = TimeHistory.BILLING_OVERTIME | code
	elif (student_num > 20):
		code = TimeHistory.BILLING_OVERPEOPLE_20 | code
	elif (student_num > 15):
		code = TimeHistory.BILLING_OVERPEOPLE_15 | code
	elif (student_num > 10):
		code = TimeHistory.BILLING_OVERPEOPLE_10 | code
	elif (student_num > 5):
		code = TimeHistory.BILLING_OVERPEOPLE | code
	if (passenger == True):
		code = TimeHistory.BILLING_PASSENGER | code

	if (code == 0):
		code = TimeHistory.BILLING_NORMAL

	return code

def setNonCharge(academy, studentNum, warning_number_set, warning_set):
	maxvehicle = max(academy.maxvehicle, int(math.ceil(float(studentNum)/10.0)))
	if (len(warning_number_set) > maxvehicle):
		sorted_warning = sorted(warning_set, key=lambda timehistory: timehistory.billing_code, reverse=True)
		for i_warning in range(maxvehicle, len(sorted_warning)):
			sorted_warning[i_warning].warning = True

# 개월차 계산
# ex. 2017-09, 2017-03 이면 6 return
def diffMonth(a, b):
	(a_year, a_month) = a.split('-')
	(b_year, b_month) = b.split('-')

	return (int(a_year) * 12 + int(a_month)) - (int(b_year) * 12 + int(b_month))

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

    if request.method == 'GET':
    	aid = request.GET.get('aid')
    	daterange = request.GET.get('daterange')
        startdate = request.GET.get('startdate')
        enddate = request.GET.get('enddate')
        carids = request.GET.getlist('carid[]')
        monthpick = request.GET.get('monthpick')
    elif request.method == 'POST':
    	aid = request.POST.get('aid')
    	daterange = request.POST.get('daterange')
        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        carids = request.POST.getlist('carid[]')
        monthpick = request.POST.get('monthpick')

    billingHistorySettings = None
    total_uncollected = 0
    uncollectedes = []


    if len(carids) == 0:
        carid = 'all'
    else:
        carid = ':'.join(carids)

    if (aid != None and monthpick != None):
        academy = Academy.objects.get(id = aid)

        billingHistorySettings = BillingHistorySetting.objects.filter(academy = academy, carid = carid, monthpick = monthpick)
	uncollectedHistories = BillingHistory.objects.filter(academy = academy, billing_il__isnull = True, billing_bank__isnull = True, month__lt = monthpick.replace('-', '')).order_by('month')
	#uncollectedHistories = BillingHistory.objects.filter(academy = academy, billing_il__isnull = True, billing_bank__isnull = True).order_by('month')
	for u in uncollectedHistories:
		uncollected = Uncollected()
		uncollected.month = u.month[:4] + '-' + u.month[4:]
		uncollected.billing_amount = "{:,}".format(u.billing_amount)
		# 2% 연체이자, 10원단위 절사
		additional_charge = int(u.billing_amount * 0.02 * diffMonth(monthpick, uncollected.month) / 100) * 100
		uncollected.additional_charge = "{:,}".format(additional_charge)
		uncollected.total_charge = "{:,}".format(u.billing_amount + additional_charge)
		total_uncollected += u.billing_amount + additional_charge
		uncollectedes.append(uncollected)

    if daterange is not None and daterange != '':
    	(startdate, enddate) = daterange.split(' - ')

    history = []

    total_count = 0
    aname = ""
    academy = None
    day_dict = {'Mon':'월', 'Tue':'화', 'Wed':'수', 'Thu':'목', 'Fri':'금', 'Sat':'토', 'Sun':'일'}
    cars = set()

    overtime = 30


    if aid is not None and aid != '' and ((startdate is not None and startdate != '' and enddate is not None and enddate != '') or (monthpick is not None)):
        if monthpick :
            ym = monthpick.split('-')
            tt, end = calendar.monthrange(int(ym[0]), int(ym[1]))
            begin = '01'
            start_date = datetime.date(*map(int, monthpick.split('-') + [begin]))
            end_date = datetime.date(*map(int, monthpick.split('-') + [end]))
            startdate = monthpick + '-' + str(begin)
            enddate = monthpick + '-' + str(end)
        else :
            start_date = datetime.date(*map(int, startdate.split('-')))
            end_date = datetime.date(*map(int, enddate.split('-')))

        total_days = (end_date - start_date).days + 1
        academy = Academy.objects.get(id=aid)
	#aname = Academy.objects.get(pk=aid).name

        if (academy.id == 62):
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
                    timeHistory.inventory_id = i
                    cars.add(timeHistory.carnum)
                    index = 0
                    studentNum = 0
                    sharingFlag = False
                    isPassenger = False
                    lflag_on_count = 0
                    lflag_off_count = 0
                    for schedule in scheduletable:
                        #timeHistory.studentnum += schedule.members.count()
			currentStudentNum = 0
                        for student in schedule.members.all():
                            if student.aid != academy:
                                sharingFlag = True
                            else:
				currentStudentNum += 1
                                timeHistory.studentnum += 1
				for offmember in schedule.offmembers.all():
					if (offmember == student):
                                                #return HttpResponse("offmember = " + str(offmember.id))
						currentStudentNum -= 1
                                if ((student.birth_year == None) or ((datetime.datetime.now().year - int(student.birth_year) + 1) <= 13)):
                                    isPassenger = True

			studentNum += currentStudentNum

                        if (schedule.lflag == 1):
                                lflag_on_count += 1
                        elif (schedule.lflag == 0):
                                lflag_off_count += 1

                        for aca in schedule.academies.all():
		            timeHistory.academies.add(aca.name)

			if (single_date >= '2017-10-01'):
                            if (index == 0):
                                timeHistory.first_time = convertMins(schedule.time)
			    # 등원인 경우 최초 탑승학생 스케쥴 이전 row 가 시작시간
			    if (schedule.lflag == 1 and studentNum == 0):
			        timeHistory.first_time = convertMins(schedule.time)
			    # 하원인 경우 마지막 하차학생 스케쥴 row 가 끝나는 시간
			    if (schedule.lflag == 0 and currentStudentNum > 0):
			        timeHistory.last_time = convertMins(schedule.time)
			    elif (schedule.lflag == 3 and lflag_on_count > lflag_off_count):
                       	        timeHistory.lflag = True
                                timeHistory.last_time = convertMins(schedule.time)
			# 2017-10-01 이전 기준을 위한 legacy
			else:
			    if (index == 0):
			        timeHistory.first_time = convertMins(schedule.time)
			    timeHistory.last_time = convertMins(schedule.time)

			# 2017-10-01 이전 기준을 위한 legacy
			if (lflag_on_count > lflag_off_count):
			    timeHistory.lflag = True

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
            warning_number_set = set()
            studentNum = 0
            for idx, h in enumerate(dailyHistory.timehistory):
                fire = False

                if ((standard_h == None) or (standard_h.last_time <= h.first_time)):
                    if (len(warning_set) > 0):
                        # warning 처리
                        # 학생 수가 많아서 어쩔 수 없이 차량이 많아진 경우는 maxvehicle 보다 우선시한다.
			setNonCharge(academy, studentNum, warning_number_set, warning_set)
                        #if (len(warning_number_set) > maxvehicle):
                            #sorted_warning = sorted(warning_set, key=lambda timehistory: timehistory.billing_code, reverse=True)
                            #for i_warning in range(maxvehicle, len(sorted_warning)):
                                #sorted_warning[i_warning].warning = True
                    standard_h = h
                    warning_set = set()
                    warning_number_set = set()
                    studentNum = h.studentnum
                    if not (h.billing_code & TimeHistory.BILLING_NONCHARGE):
                        warning_set.add(h)
                        warning_number_set.add(h.carnum)
                else:
                    studentNum += h.studentnum
                    if not (h.billing_code & TimeHistory.BILLING_NONCHARGE):
                        warning_set.add(h)
                        warning_number_set.add(h.carnum)

		if (idx == len(dailyHistory.timehistory)-1 and (len(warning_set) > 0)):
			setNonCharge(academy, studentNum, warning_number_set, warning_set)
			# warning 처리
			# 학생 수가 많아서 어쩔 수 없이 차량이 많아진 경우는 maxvehicle 보다 우선시한다.
			#maxvehicle = max(academy.maxvehicle, int(math.ceil(float(studentNum)/10.0)))
			#if (len(warning_number_set) > maxvehicle):
				#sorted_warning = sorted(warning_set, key=lambda timehistory: timehistory.billing_code, reverse=True)
				#for i_warning in range(maxvehicle, len(sorted_warning)):
					#sorted_warning[i_warning].warning = True

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
        if (len(carids) != 0):
            for dailyHistory in history:
                dailyHistory.timehistory[:] = [x for x in dailyHistory.timehistory if str(x.carnum) in carids]

    cur_year = datetime.datetime.now().year
    cur_month = datetime.datetime.now().month
    monthpick_range = [
        '{}-{:0>2}'.format(year, month)
            for year in xrange(2016, cur_year+1)
            for month in xrange(1, 12+1)
            if not (year == cur_year and month > cur_month)
    ]

    if (monthpick) :
        lastmonth = monthpick
    else :
        if (cur_month > 1):
            lastmonth = '{}-{:0>2}'.format(cur_year, cur_month - 1)
        else:
            lastmonth = '{}-{:0>2}'.format(cur_year - 1, 12)



    return render(request, 'getHistory.html', {"history": history, "academy" : academy, 'total_count': total_count, 'startdate': startdate, 'enddate': enddate, 'user':request.user, 'cars':sorted(cars), 'carids':carids, 'carid':carid, 'overtime':overtime, 'monthpick_range': monthpick_range, 'lastmonth': lastmonth, "billingHistorySettings": billingHistorySettings, 'uncollectedes': uncollectedes, 'total_uncollected': "{:,}".forma(total_uncollected)})


@login_required
def addAcademyForm(request):
	redirect_url = request.META.get('HTTP_REFERER', 'http://' + request.META.get('SERVER_NAME') + '/institute/listStudents')

	if not request.user.is_staff :
		return render(request, 'message.html', {'msg': "staff 권한이 필요합니다.", 'redirect_url': redirect_url})

	buses = Car.objects.all()

	return render(request, 'addUpdateAcademyForm.html', {'buses' : buses})

@login_required
def updateAcademyForm(request):
	redirect_url = request.META.get('HTTP_REFERER', 'http://' + request.META.get('SERVER_NAME') + '/institute/listStudents')

	if not request.user.is_staff :
		return render(request, 'message.html', {'msg': "staff 권한이 필요합니다.", 'redirect_url': redirect_url})

	aid = request.GET.get('aid')
	academy = Academy.objects.get(id = aid)

	buses = Car.objects.filter(branchid__id = academy.bid)

	return render(request, 'addUpdateAcademyForm.html', {'academy' : academy, 'buses' : buses})

@csrf_exempt
@login_required
def addAcademy(request):
	redirect_url = request.META.get('HTTP_REFERER', 'http://' + request.META.get('SERVER_NAME') + '/institute/listStudents')
        cursor = connection.cursor()
	if not request.user.is_staff :
		return render(request, 'message.html', {'msg': "staff 권한이 필요합니다.", 'redirect_url': redirect_url})

	try:
	    cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['003','0'])
	    giup = cursor.fetchone()

	    cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['004','0'])
	    gukmin = cursor.fetchone()

	    cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['011','0'])
	    nonghyup = cursor.fetchone()

	    cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['020','0'])
	    woori = cursor.fetchone()

	    cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['027','0'])
	    city = cursor.fetchone()

	    cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['071','0'])
	    woochegook = cursor.fetchone()

	    cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['081','0'])
	    hana = cursor.fetchone()

	    cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['088','0'])
	    shinhan = cursor.fetchone()

	except Exception, e:
		print ("Can't call Insert", e)



	bid = request.POST.get('bid')
	aname = request.POST.get('aname')
	phone_1 = request.POST.get('phone_1')
	phone_2 = request.POST.get('phone_2')
	maxvehicle = request.POST.get('maxvehicle')
	lat = request.POST.get('lat')
	lng = request.POST.get('lng')
	address = request.POST.get('address')
	address2 = request.POST.get('address2')
        linebuses = request.POST.getlist('linebuses[]')

	branch = Branch.objects.get(id=bid)
	msg = None

	try:
		poi = Poi.objects.get(lat = lat, lng = lng)
	except Poi.DoesNotExist:
		poi = Poi.objects.create(lat = lat, lng = lng, address = address)

	try:
		placement = Placement.objects.get(poi = poi, alias = aname)
	except Placement.DoesNotExist:
		placement = Placement.objects.create(poi = poi, alias = aname, branch = branch)
	placement = None

	try:
		academy = Academy.objects.create(name = aname, address = address, address2 = address2, phone_1 = phone_1, phone_2 = phone_2, bid = bid, maxvehicle = maxvehicle, placement = placement, bank003 = giup[0].strip(), bank004 = gukmin[0].strip(), bank011 = nonghyup[0].strip(), bank020 = woori[0].strip(), bank027 = city[0].strip(), bank071 = woochegook[0].strip(), bank081 = hana[0].strip(), bank088 = shinhan[0].strip())

		for busid in linebuses:
			bus = Car.objects.get(id = busid)
			academy.linebuses.add(bus)

	except IntegrityError as e:
		#if 'unique constraint' in e.message:
		msg = "중복되는 학원명입니다."
	except:
		msg = "에러가 발생했습니다."
	else:
		msg = "학원 추가 성공했습니다."
		aca_bank = Academy.objects.get(name = aname)
		bank003 = aca_bank.bank003
		bank004 = aca_bank.bank004
		bank011 = aca_bank.bank011
		bank020 = aca_bank.bank020
		bank027 = aca_bank.bank027
		bank071 = aca_bank.bank071
		bank081 = aca_bank.bank081
		bank088 = aca_bank.bank088
		cursor.execute("UPDATE vacs_vact SET acct_st = %s, tramt_cond = %s WHERE acct_no = %s", ['1','0',bank003])
		cursor.execute("UPDATE vacs_vact SET acct_st = %s, tramt_cond = %s WHERE acct_no = %s", ['1','0',bank004])
		cursor.execute("UPDATE vacs_vact SET acct_st = %s, tramt_cond = %s WHERE acct_no = %s", ['1','0',bank011])
		cursor.execute("UPDATE vacs_vact SET acct_st = %s, tramt_cond = %s WHERE acct_no = %s", ['1','0',bank020])
		cursor.execute("UPDATE vacs_vact SET acct_st = %s, tramt_cond = %s WHERE acct_no = %s", ['1','0',bank027])
		cursor.execute("UPDATE vacs_vact SET acct_st = %s, tramt_cond = %s WHERE acct_no = %s", ['1','0',bank071])
		cursor.execute("UPDATE vacs_vact SET acct_st = %s, tramt_cond = %s WHERE acct_no = %s", ['1','0',bank081])
		cursor.execute("UPDATE vacs_vact SET acct_st = %s, tramt_cond = %s WHERE acct_no = %s", ['1','0',bank088])
                cursor.close()
		connection.commit()
		connection.close()
	return render(request, 'message.html', {'msg': msg, 'redirect_url': request.META.get('HTTP_REFERER')})

@csrf_exempt
@login_required
def updateAcademy(request):
	redirect_url = request.META.get('HTTP_REFERER', 'http://' + request.META.get('SERVER_NAME') + '/institute/listStudents')

	if not request.user.is_staff :
		return render(request, 'message.html', {'msg': "staff 권한이 필요합니다.", 'redirect_url': redirect_url})

	aid = request.POST.get('aid')
	bid = request.POST.get('bid')
	aname = request.POST.get('aname')
	phone_1 = request.POST.get('phone_1')
	phone_2 = request.POST.get('phone_2')
	maxvehicle = request.POST.get('maxvehicle')
	lat = request.POST.get('lat')
	lng = request.POST.get('lng')
	address = request.POST.get('address')
	address2 = request.POST.get('address2')
        linebuses = request.POST.getlist('linebuses[]')

	branch = Branch.objects.get(id=bid)
	msg = None

	try:
		poi = Poi.objects.get(lat = lat, lng = lng)
	except Poi.DoesNotExist:
		poi = Poi.objects.create(lat = lat, lng = lng, address = address)

	try:
		placement = Placement.objects.get(poi = poi, alias = aname)
	except Placement.DoesNotExist:
		placement = Placement.objects.create(poi = poi, alias = aname, branch = branch)

	try:
		academy = Academy.objects.get(id = aid)
		academy.name = aname
		academy.address = address
		academy.address2 = address2
		academy.phone_1 = phone_1
		academy.phone_2 = phone_2
		academy.bid = bid
		academy.maxvehicle = maxvehicle
		academy.placement = placement
		academy.save()

		for busid in linebuses:
			bus = Car.objects.get(id = busid)
			academy.linebuses.add(bus)


		#academy.placement = placement

	except IntegrityError as e:
		msg = "중복되는 학원명입니다."
	except:
		msg = "에러가 발생했습니다."
	else:
		msg = "학원 정보 수정 성공했습니다."

	return render(request, 'message.html', {'msg': msg, 'redirect_url': request.META.get('HTTP_REFERER')})

@login_required
def listAcademies(request):
	if not request.user.is_staff :
		msg = "staff 권한이 필요합니다."
		return render(request, 'message.html', {'msg': msg, 'redirect_url': request.META.get('HTTP_REFERER')})

	academies = Academy.objects.all().order_by('bid')
	branches = Branch.objects.all()
	branch_dict = {}
	for branch in branches:
		branch_dict[branch.id] = branch.bname

	return render(request, 'listAcademies.html', {'academies': academies, 'branch_dict': branch_dict});

def prevmonth(yearmonth):
	arr = yearmonth.split('-')

	return arr[0] + arr[1]

def thismonth():
	return "%04d%02d" % (timezone.now().year, timezone.now().month)

@csrf_exempt
@login_required
def saveBill(request):
	aid = request.POST.get('aid')
	amount = request.POST.get('amount')
	yearmonth = request.POST.get('yearmonth')

	current_yearmonth = thismonth()
	previous_yearmonth = prevmonth(yearmonth)

	start_billday = current_yearmonth + "07"
	end_billday = current_yearmonth + "15"

	academy = Academy.objects.get(id = aid)


	conn = None

	with connection.cursor() as cursor:
		try:
			for bankcode in BANKCODES:
				field = "bank" + bankcode
				cursor.execute("""UPDATE vacs_vact SET tr_amt = %s, trbegin_il = %s, trend_il = %s WHERE bank_cd = %s AND acct_no = %s;""", (amount, start_billday, end_billday, bankcode, getattr(academy, field)))
		except:
			return HttpResponse("error occured")

	obj, created = BillingHistory.objects.update_or_create(academy = academy, month = previous_yearmonth, defaults = {'billing_amount': int(amount)},)
	#billinghistory = BillingHistory.objects.create(academy = academy, month = prevmonth, billing_amount = int(amount))

	return HttpResponse("start : " + start_billday + " <> end : " + end_billday)


@login_required
def listAcademiesBilling(request):
	if not request.user.is_staff :
		msg = "staff 권한이 필요합니다."
		return render(request, 'message.html', {'msg': msg, 'redirect_url': request.META.get('HTTP_REFERER')})


	billinghistorys = BillingHistory.objects.all()
	academy = Academy.objects.all()
	aca_name_dict = {}
	aca_phone_dict = {}

	for aname in academy:
		aca_name_dict[aname.id] = aname.name

	for aphone in academy:
		aca_phone_dict[aphone.id] = aphone.phone_1

	return render(request, 'listAcademiesBilling.html', {'billinghistory': billinghistorys, 'aca_name_dict': aca_name_dict, 'aca_phone_dict': aca_phone_dict});

def makeBillingHistorySettingName(billingHistorySetting):
	return billingHistorySetting.created_time + " By " + billingHistorySetting.created_user.username + "(" + billingHistorySetting.created_user.first_name + " " + billingHistorySetting.created_user.last_name + ") " + billingHistorySetting.fix

def makeBillingHistorySettingValue(billingHistorySetting):
	return billingHistorySetting.created_time + "_" + str(billingHistorySetting.created_user_id)

@csrf_exempt
@login_required
def saveBillingHistorySetting(request):
	aid = request.GET.get('aid')
	carid = request.GET.get('carid')
	monthpick = request.GET.get('monthpick')
	fix = request.GET.get('fix')

	received_json_data = json.loads(request.body)

	if (aid == None or carid == None or monthpick == None or fix == None):
		return JsonResponse({'msg' : 'Error'})

	if (fix == 'fix'):
		fix_msg = '확정'
	else:
		fix_msg = '임시저장'

	academy = Academy.objects.get(id = aid)
	billingHistorySetting = BillingHistorySetting.objects.create(academy = academy, carid = carid, monthpick = monthpick, fix = fix_msg, created_user = request.user, setting = received_json_data)
	name = makeBillingHistorySettingName(billingHistorySetting)
	value = makeBillingHistorySettingValue(billingHistorySetting)

	return JsonResponse({'msg' : 'Success', 'name' : name, 'value' : value})

@login_required
def getBillingHistorySetting(request):
	created_time = request.GET.get('created_time')
	created_user_id = request.GET.get('created_user_id')

	try :
		created_user = User.objects.get(id = created_user_id)
		billingHistorySetting = BillingHistorySetting.objects.filter(created_time = created_time, created_user = created_user)
	except User.DoesNotExist:
		return HttpResponse("해당 히스토리의 사용자가 존재하지 않습니다.")
	except BillingHistorySetting.DoesNotExist:
		return HttpResponse("해당 히스토리가 존재하지 않습니다.")

	return JsonResponse(billingHistorySetting[0].setting)

@login_required
def getBillingHistorySettingList(request):
    	aid = request.GET.get('aid')
        carid = request.GET.get('carid')
        monthpick = request.GET.get('monthpick')

	try :
        	academy = Academy.objects.get(id = aid)
        	billingHistorySettings = BillingHistorySetting.objects.filter(academy = academy, carid = carid, monthpick = monthpick).order_by('created_time')
	except BillingHistorySetting.DoesNotExist:
		return HttpResponse("해당 히스토리가 존재하지 않습니다.")

	jsonObj = {}
	jsonObj['list'] = []

	for billingHistorySetting in billingHistorySettings:
		name = makeBillingHistorySettingName(billingHistorySetting)
		value = makeBillingHistorySettingValue(billingHistorySetting)
		jsonObj['list'].append({'name' : name, 'value' : value})

	return JsonResponse(jsonObj)

@login_required
def exportStudentList(request):
	rv = checkAuth(request)
	if rv != None :
		return rv

	if request.user.is_staff :
		institute = request.session.get('institute', None)
	else :
		institute = request.user.first_name

	response = HttpResponse(content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename="student.xls"'

	workbook = xlwt.Workbook(encoding='utf-8')
	workbook.default_style.font.height = 20 * 11 # 11pt

	worksheet = workbook.add_sheet(u'학생리스트')

	font_style = xlwt.easyxf('font: height 280, bold on')
	worksheet.row(0).set_style(font_style)

	studentList = StudentInfo.objects.filter(aid__name = institute).filter(deleted_date__isnull=True).order_by('sname')
	row = 0
	worksheet.write(row, 0, u'학원')
	worksheet.write(row, 1, u'이름')
	worksheet.write(row, 2, u'부모님전화번호')
	worksheet.write(row, 3, u'조부모님전화번호')
	worksheet.write(row, 4, u'학생전화번호')
	worksheet.write(row, 5, u'돌봄전화번호')
	worksheet.write(row, 6, u'나이')
	row += 1
	for student in studentList:
		worksheet.write(row, 0, student.aid.name)
		worksheet.write(row, 1, student.sname)
		worksheet.write(row, 2, student.parents_phonenumber)
		worksheet.write(row, 3, student.grandparents_phonenumber)
		worksheet.write(row, 4, student.self_phonenumber)
		worksheet.write(row, 5, student.care_phonenumber)
		if (student.birth_year):
			worksheet.write(row, 6, timezone.now().year - int(student.birth_year) + 1)
		row += 1

	workbook.save(response)

	return response


@login_required
@csrf_exempt
def importStudentList(request):
	rv = checkAuth(request)

	if request.user.is_staff :
		institute = request.session.get('institute', None)
	else :
		institute = request.user.first_name

	if request.method == 'POST':
		form = XlsInputForm(request.POST, request.FILES)
		msg = ''
		same_person = 0
		nrows = 0
		if form.is_valid():
			input_excel = request.FILES['input_excel']
			workbook = xlrd.open_workbook(file_contents = input_excel.read(), encoding_override = 'utf8')
			worksheet = workbook.sheet_by_index(0)
			nrows = worksheet.nrows

			for row_num in range(nrows) :
				if (row_num != 0) :
					values = worksheet.row_values(row_num)
					if len(values) != 7 :
						return render(request, 'message.html', {'msg': 'excel file 의 format 이 정상적이지 않습니다.', 'redirect_url': request.META.get('HTTP_REFERER')})
					if (values[0] != institute) :
						return render(request, 'message.html', {'msg': 'excel file 의 format 이 정상적이지 않습니다.', 'redirect_url': request.META.get('HTTP_REFERER')})

			for row_num in range(nrows) :
				if (row_num != 0) :
					values = worksheet.row_values(row_num)
					# values[0] = 학원명
					rv = funcAddStudent(*values)
					if (rv == TAYO_ERROR_SAME_PERSON):
						same_person += 1
						#return render(request, 'message.html', {'msg': str(row_num) + "번째 row : 동일한 학생이 존재합니다.", 'redirect_url': request.META.get('HTTP_REFERER')})
					elif (rv == TAYO_ERROR_SAVE_FAILURE):
						return render(request, 'message.html', {'msg': str(row_num) + '번째 row : 학원생 추가 실패했습니다. error : Too many retry for make random pin_number', 'redirect_url': request.META.get('HTTP_REFERER')})

		if (same_person > 0):
			msg = str(same_person) + '명의 중복 사용자가 존재합니다. '

		msg += str(nrows-1-same_person) + '명의 신규 학원생 추가 성공했습니다.'
		return render(request, 'message.html', {'msg': msg, 'redirect_url': request.META.get('HTTP_REFERER')})

	return HttpResponse("Error")

@login_required
def importStudentListForm(request):
	return render(request, 'importStudentListForm.html');

@login_required
def listSchedule(request):
	areaid = request.GET.get('areaid')
	branchid = request.GET.get('branchid')
	day = request.GET.get('day')
	week = request.GET.get('week')
	carnum = int(request.GET.get('carnum', 0))
	searchTime = request.GET.get('searchTime')

	branch = Branch.objects.filter(id = branchid)

	#contacts = getContacts(branchid, day, carnum, week, searchTime)
	contacts = getContacts(1, '월', 1, 1, '')
	return render(request, 'listSchedule.html', {'contacts': contacts});

def getCarsByBranch(request):
	bid = request.GET.get('bid')

	cars = Car.objects.filter(branchid__id = bid)

	msg = {}
	msg['cars'] = []

	for car in cars:
		data = {}
		data['id'] = car.id
		data['name'] = car.carname
		msg['cars'].append(data)

	return JsonResponse(msg)
