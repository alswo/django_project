from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from passenger.models import Commute, Academy, Schedule, ShuttleSchedule, Group, ScheduleDate,Community
from schedule.models import Branch, Car
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.core import serializers
from django.core.serializers import serialize
from passenger.dateSchedule import timeToDate
from django.utils.crypto import get_random_string
from django.db import connection
import json

def is_not_driver(user):
    if user:
        return (user.groups.filter(name='driver').exists() == False)
    return True

@login_required
def main(request):
    academies = Academy.objects.order_by('name')
    groups = Group.objects.order_by('-gid')
    branch = Branch.objects.order_by('-id')

    join_group = Group.objects.extra(select = {'gid':'passenger_group.gid','gname':'passenger_group.gname', 'bname':'schedule_branch.bname'},tables=['schedule_branch'], where=['schedule_branch.id = passenger_group.bid']).order_by('gid')

    driver = []
    for g in join_group:
        driver.append(g)

    return render_to_response('passenger/main.html', {"driver":driver, "academies" : academies, "groups": groups, "branch" : branch,'user':request.user})



def sturegi(request):
    return render_to_response('passenger/typeform_sr.html')

@csrf_exempt
def schedule(request):
    academys = None
    if request.method == "POST":
        gid = request.POST.get('gid')

        academys = Academy.objects.filter(gid = gid)

    return render_to_response('passenger/schedule.html', {"academys" : academys,'user':request.user})

def safetyTayo(request):
    if request.method =="GET":
        schedule = request.GET.get('schedule')
        aid = request.GET.get('aid')
        contacts = Commute.objects.filter(aid = aid)

    return render_to_response('passenger/tayo.html', {"contacts" : contacts, "schedule" : schedule, "aid" : aid,'user':request.user})


@login_required
@user_passes_test(is_not_driver, login_url='/', redirect_field_name=None)
def opti(request):
    if request.method =="GET":
        return render_to_response('passenger/optimizationDistance.html', {'user':request.user})

@login_required
@user_passes_test(is_not_driver, login_url='/', redirect_field_name=None)
def opti2(request):
    if request.method =="GET":
	unique_id = get_random_string(length=32)
        return render_to_response('passenger/optimizationDistance2.html', {'user':request.user, 'unique_id':unique_id})

@login_required
@user_passes_test(is_not_driver, login_url='/', redirect_field_name=None)
def opti_0613(request):
    if request.method =="GET":
        return render_to_response('passenger/optimizationDistance.0613.html', {'user':request.user})

@login_required
@user_passes_test(is_not_driver, login_url='/', redirect_field_name=None)
def opti_0428(request):
    if request.method =="GET":
        return render_to_response('passenger/optimizationDistance.0428.html', {'user':request.user})

@csrf_exempt
def addSchedule(request):
    if request.method == "POST":
        a_name = request.POST.get('a_name')
        sorting_time = request.POST.get('sorting_time')
        day = request.POST.get('day')
        schedule = request.POST.get('writing')
        aid = request.POST.get('aid')
        slist = request.POST.getlist('slist[]')
        gid = request.POST.get('gid')
        shuttleSchedule = ShuttleSchedule(slist = slist, a_name = a_name, time = sorting_time, day = day, schedule = schedule,aid = aid, gid = gid)
        shuttleSchedule.save()

    return HttpResponse('1')

@csrf_exempt
def saveSchedule(request):
    if request.method == "POST":
        sid = request.POST.get('sid')
        s = ShuttleSchedule.objects.get(id = sid)
        s.p_schedule = s.schedule
        s.save()

    return HttpResponse('Success!')

@csrf_exempt
def deleteSchedule(request):
    if request.method == "POST":
        sid = request.POST.get('sid')
        s = ShuttleSchedule.objects.get(id = sid)
        s.delete()

    return HttpResponse('Success!')

@csrf_exempt
def day(request):
    if request.method == "POST":
        aid = request.POST.get('aid')

    return render_to_response('passenger/day.html', {"id" : aid,'user':request.user})

@csrf_exempt
def updateDay(request):
    if request.method == "POST":
        gid = request.POST.get('gid')

    return render_to_response('passenger/updateDay.html', {"gid" : gid,'user':request.user})

@csrf_exempt
def updateDayAca(request):
    if request.method == "POST":
        aid = request.POST.get('aid')

    return render_to_response('passenger/updateDayAca.html', {"aid" : aid,'user':request.user})

@csrf_exempt
def driverday(request):
    if request.method == "POST":
        gid = request.POST.get('gid')

    return render_to_response('passenger/driverday.html', {"gid" : gid,'user':request.user})

def getAcaButton(request):
    if request.method == "GET":
        bid = request.GET.get('bid')
        academy = Academy.objects.filter(bid=bid)

    return render_to_response('passenger/getAcaButton.html',{"academy":academy})

def getDriButton(request):
    if request.method == "GET":
        bid = request.GET.get('bid')
        carlist = Car.objects.filter(branchid=bid)

    return render_to_response('passenger/getDriButton.html',{"carlist":carlist})


@csrf_exempt
def academySchedule(request):
    if request.method == "GET":
        aid = request.GET.get('aid')
        day = request.GET.get('day')
        academy = Academy.objects.get(id = aid)
        bid = academy.bid
        contacts = ShuttleSchedule.objects.filter(bid=bid).filter(a_name__contains = academy.name).filter(day=day).order_by('time')
        contacts2 = []

        for contact in contacts:
            if (len(contact.schedule) != 0):
                contacts2.append(contact)

        return render_to_response('passenger/academySchedule.html', {"contacts" : contacts2, "aid" : aid,'user':request.user})

@login_required
def driverSchedule(request):
    if request.method == "GET":
        gid = request.GET.get('gid')
        day = request.GET.get('day')
        contacts = ShuttleSchedule.objects.filter(gid = gid).filter(day=day).order_by('time')

        return render_to_response('passenger/driverSchedule.html', {"contacts" : contacts, "gid" : gid,'user':request.user})

@csrf_exempt
def updateSchedule(request):
    if (request.user.is_authenticated() and request.user.username == 'sua'):
        return HttpResponse("You don't have permission for this page!!")

    if request.method == "GET":
        gid = request.GET.get('gid')
        day = request.GET.get('day')
        contacts = ShuttleSchedule.objects.filter(gid = gid).filter(day=day).order_by('time')
        academies = Academy.objects.all()
        groups = Group.objects.all()
        branch = Branch.objects.all()

        return render_to_response('passenger/updateSchedule.html', {"contacts" : contacts, "gid":gid, "branch" : branch,"academies" : academies, "groups": groups,'user':request.user})

    elif request.method == "POST":
        blist = []
        aid = request.POST.get('aid')
        blist.append(aid)
        gid = request.POST.get('gid')
        a_name = request.POST.get('a_name')
        day = request.POST.get('day')
        time = request.POST.get('time')
        schedule = request.POST.get('schedule')

        s = ShuttleSchedule(a_name = a_name, day = day, time = time, schedule = schedule, gid = gid, aid = aid, slist = [0], p_schedule = '', alist = blist, memo = '')
        s.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def uAca(request):
    if (request.user.is_authenticated() and request.user.username == 'sua'):
        return HttpResponse("You don't have permission for this page!!")

    if request.method == "GET":
        aid = request.GET.get('aid')
        day = request.GET.get('day')
        academy = Academy.objects.get(id = aid)
        students = Commute.objects.filter(aid = aid).filter(day = day).order_by('stime')
        contacts = ShuttleSchedule.objects.filter(a_name__contains = academy.name).filter(day=day).order_by('time')
        branch = Branch.objects.all()
        academies = Academy.objects.all()
        groups = Group.objects.all()

    return render_to_response('passenger/uAca.html', {"contacts" : contacts, "aid":aid, "students": students, "academies" : academies, "branch" : branch,"groups" : groups,'user':request.user})

@csrf_exempt
def uSchedule(request):
    if request.method == "POST":
        if request.POST.get('what') == 'memo':
            btn = request.POST.get('btn')
            id = request.POST.get('id')
            if btn == 'save':
                s = ShuttleSchedule.objects.get(id = id)
                memo = request.POST.get('memo')
                s.memo = memo
                s.save()

                return HttpResponse(memo)

            elif btn == 'edit':
                s = ShuttleSchedule.objects.get(id = id)
                memo = request.POST.get('memo')
                s.memo = memo
                s.save()

                return HttpResponse(memo)

            elif btn == 'delete':
                s = ShuttleSchedule.objects.get(id = id)
                s.memo = ''
                s.save()

                return HttpResponse('')

        elif request.POST.get('what') == 'schedule':
            aid = request.POST.get('aid')
            gid = request.POST.get('gid')
            id = request.POST.get('id')
            a_name =request.POST.get('a_name')
            day =request.POST.get('day')
            time = request.POST.get('time')
            schedule = request.POST.get('schedule')
            bid = request.POST.get('bid')
            academy = Academy.objects.get(id = aid)

            s = ShuttleSchedule.objects.get(id = id)

            s.a_name = a_name
            s.gid = gid
            s.day = day
            s.time = time
            s.schedule = schedule
            s.bid = bid
            s.save()

            return HttpResponse(schedule)


        elif request.POST.get('what') == 'driverSchedule':
            gid = request.POST.get('gid')
            id = request.POST.get('id')
            a_name =request.POST.get('a_name')
            day =request.POST.get('day')
            time = request.POST.get('time')
            schedule = request.POST.get('schedule')
            bid = request.POST.get('bid')

            s = ShuttleSchedule.objects.get(id = id)

            s.a_name = a_name
            s.gid = gid
            s.day = day
            s.time = time
            s.schedule = schedule
            s.bid = bid

            s.save()

            return HttpResponse(schedule)


@csrf_exempt
def acaphone(request):
    if request.method == "POST":
        alist = request.POST.getlist('alist[]')
        plist = []
        pnlist = []
        for a in alist:
            academy = Academy.objects.get(id = a)
            plist.append(academy.phone_1)
            pnlist.append(academy.name)
        return JsonResponse({"plist" : plist, "pnlist" : pnlist})

@login_required
@csrf_exempt
def studata(request):
    if request.method == "GET":
        if request.GET.get('id'):
            aid = request.GET.get('id')
            students = Commute.objects.filter(aid=aid).order_by('-id')
            academies = Academy.objects.order_by('-id')

            return render_to_response('passenger/studata.html', {"students" : students, "academies" : academies ,'user':request.user})

        else:
            academies = Academy.objects.order_by('-id')
            students = Commute.objects.order_by('-id')

            return render_to_response('passenger/studata.html', {"students" : students, "academies" : academies,'user':request.user })

    elif request.method == "POST":
        if request.POST.get('class') == 'add':
            name = request.POST.get('name')
            aid = request.POST.get('aid')
            day = request.POST.get('day')
            stime = request.POST.get('start')
            etime = request.POST.get('end')
            onlocation = request.POST.get('onlocation')
            offlocation = request.POST.get('offlocation')
            on_lon = request.POST.get('on_lon')
            on_lat = request.POST.get('on_lat')
            off_lon = request.POST.get('off_lon')
            off_lat = request.POST.get('off_lat')
            etc = request.POST.get('etc')

            if on_lon == '':
                on_lon = 0
            if on_lat == '':
                on_lat = 0
            if off_lon == '':
                off_lon = 0
            if off_lat == '':
                off_lat = 0

            a_name = Academy.objects.get(id = aid).name

            student = Commute(name = name, aid = aid,a_name = a_name, day = day, stime = stime, etime = etime, onlocation = onlocation,
                                offlocation = offlocation, on_lon = on_lon, on_lat = on_lat, off_lon = off_lon, off_lat = off_lat,etc = etc)

            student.save()

            students = Commute.objects.order_by('id')
            academies = Academy.objects.order_by('-id')

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        elif request.POST.get('class') == 'edit':
            name = request.POST.get('name')
            id = request.POST.get('e_sid')
            aid = request.POST.get('eaid')
            day = request.POST.get('day')
            stime = request.POST.get('stime')
            etime = request.POST.get('etime')
            onlocation = request.POST.get('onlocation')
            offlocation = request.POST.get('offlocation')
            on_lon = request.POST.get('on_lon')
            on_lat = request.POST.get('on_lat')
            off_lon = request.POST.get('off_lon')
            off_lat = request.POST.get('off_lat')
            etc = request.POST.get('etc')

            if on_lon == '':
                on_lon = 0
            if on_lat == '':
                on_lat = 0
            if off_lon == '':
                off_lon = 0
            if off_lat == '':
                off_lat = 0

            a_name = Academy.objects.get(id = aid).name
            student = Commute.objects.get(id = id)

            student.name = name
            student.aid = aid
            student.a_name = a_name
            student.day = day
            student.stime = stime
            student.etime = etime
            student.onlocation = onlocation
            student.offlocation = offlocation
            student.on_lon = on_lon
            student.on_lat = on_lat
            student.off_lon = off_lon
            student.off_lat = off_lat
            student.etc = etc

            student.save()

            students = Commute.objects.order_by('id')
            academies = Academy.objects.order_by('-id')

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        elif request.POST.get('class') == 'delete':
            id = request.POST.get('d_sid')
            student = Commute.objects.get(id = id)
            student.delete()

            academies = Academy.objects.order_by('-id')
            students = Commute.objects.order_by('-id')

            return render_to_response('passenger/studata.html', {"students": students, "academies" : academies,'user':request.user})

@csrf_exempt
def dateSchedule(request):

    if request.method == "GET":
        if request.GET.get("what") == "range":
            academy = Academy.objects.all()

            return render_to_response('passenger/rangeSchedule.html',{"academy" : academy,'user':request.user})

        elif request.GET.get("what") == "single":
            academy = Academy.objects.all()

            return render_to_response('passenger/dateSchedule.html', {"academy" : academy,'user':request.user})

        elif request.GET.get("what") == "car":
            group = Group.objects.all()

            return render_to_response('passenger/carRangeSchedule.html', {"group" : group,'user':request.user})

    elif request.method == "POST":
        what = request.POST.get('what')
        aid = request.POST.get('aid')
        gid = request.POST.get('gid')
        date = request.POST.get('date')
        toDate = request.POST.get('to')
        fromDate = request.POST.get('from')

        if what == "single":
            a_name = Academy.objects.get(id = aid).name
            contacts = ScheduleDate.objects.filter(date=date).filter(a_name__contains = a_name).order_by('today','time')

            return render_to_response('passenger/viewDateSchedule.html', {"contacts": contacts, "count" : count,'user':request.user})

        elif what == "range":
            t = timeToDate()
            toD = t.timeToDtype(toDate)
            fromD = t.timeToDtype(fromDate)
            a_name = Academy.objects.get(id = aid).name
            contacts2 = []

            a_name.strip()
            contacts = ScheduleDate.objects.filter(today__range=[fromD,toD]).filter(a_name__contains = a_name).order_by('today','time')

            for contact in contacts:
                anames = contact.a_name.strip().split('&')
                if (a_name in anames):
                    contacts2.append(contact)
            count = len(contacts2)

            return render_to_response('passenger/viewDateSchedule.html', {"contacts": contacts2, "count" : count,'user':request.user})

        elif what == 'car':
            t = timeToDate()
            toD = t.timeToDtype(toDate)
            fromD = t.timeToDtype(fromDate)
            contacts = ScheduleDate.objects.filter(today__range=[fromD,toD]).filter(gid=gid).order_by('today','time')

            count = len(contacts)

            return render_to_response('passenger/viewDateSchedule.html', {"contacts": contacts, "count" : count,'user':request.user})


@csrf_exempt
@login_required
def community(request):
    if request.method == "GET":
        contacts = Community.objects.order_by('-id')

        return render_to_response('passenger/community.html',{"contacts":contacts,'user':request.user})

    elif request.method == "POST":
        choice = request.POST.get('choice')
        uid = request.POST.get('uid')
        cid = request.POST.get('cid')
        response_data = {}

        if choice:
            try:
                contact = Community.objects.get(id=cid)

                for user in contact.disuserid:
                    if str(user) == uid:
                        response_data['error'] = 'true'
                        return HttpResponse(json.dumps(response_data), content_type="application/json")

                for user in contact.likeuserid:
                    if str(user) == uid:
                        response_data['error'] = 'true'
                        return HttpResponse(json.dumps(response_data), content_type="application/json")

                if(choice == '0'):
                    contact.dlike = contact.dlike+1
                    contact.disuser.append(request.user)
                    contact.disuserid.append(uid)
                    response_data['like'] = '0'
                    response_data['num'] = contact.dlike

                elif(choice == '1'):
                    contact.clike = contact.clike+1
                    contact.likeuser.append(request.user)
                    contact.likeuserid.append(uid)
                    response_data['like'] = '1'
                    response_data['num'] = contact.clike

                response_data['error'] = 'false'
                contact.save()

                return HttpResponse(json.dumps(response_data), content_type="application/json")

            except Exception as e:

                return HttpResponse(e.message)

        else:
            aname = request.POST.get('aname')
            complain = request.POST.get('complain')
            plan = request.POST.get('plan')
            t = timeToDate()
            toDate = t.timeToYmd()
            c = Community(aname=aname, complain=complain, plan=plan,showdate = toDate,clike=0,dlike=0,disuser=[],disuserid=[],likeuserid=[],likeuser=[])

            c.save()


            contacts = Community.objects.order_by('-id')

            return render_to_response('passenger/community.html',{"contacts":contacts,'user':request.user})

@csrf_exempt
def studentInfo(request):
    if request.method == "GET":
        branch = Branch.objects.all()

        return render_to_response('passenger/studentInfo.html',{'branch':branch,'user':request.user})

    elif request.method == "POST":
        flag = request.POST.get('flag')
        if flag == '1':
            bid = request.POST.get('branch')
            aca = Academy.objects.filter(bid = bid)
            data = serialize('json', aca)

            return HttpResponse(data, content_type="application/json" )

@csrf_exempt
def profileInfo(request):
    if request.method == "POST":
        areaid = request.POST.get('bid')
        branch = Branch.objects.filter(areaid__in = areaid)
        temp_bid = [ b.id for b in branch]
        aca = Academy.objects.filter(bid__in = temp_bid)
        data = serialize('json', aca)

        return HttpResponse(data, content_type="application/json")



def robots(request):
	return render_to_response('passenger/robots.txt', content_type="text/plain")



def insertBanksAcademy():
    academy = Academy.objects.all()
    cursor = connection.cursor()
    for a in academy:
        if a.bank003 == '0':
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['03','0'])
                giup = cursor.fetchone()
                print giup[0].strip()
                cursor.execute("UPDATE vacs_vact SET acct_st = %s WHERE acct_no = %s", ['1',giup[0].strip()])
            except Exception, e:
                print ("Can't call Insert", e)

            a.bank003 = giup[0].strip()

        if a.bank004 == '0':
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['04','0'])
                gukmin = cursor.fetchone()
                cursor.execute("UPDATE vacs_vact SET acct_st = %s WHERE acct_no = %s", ['1',gukmin[0].strip()])
            except Exception, e:
                print ("Can't call Insert", e)

            a.bank004 = gukmin[0].strip()

        if a.bank011 == '0':
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['11','0'])
                nonghyup = cursor.fetchone()
                cursor.execute("UPDATE vacs_vact SET acct_st = %s WHERE acct_no = %s", ['1',nonghyup[0].strip()])
            except Exception, e:
                print ("Can't call Insert", e)

            a.bank011 = nonghyup[0].strip()

        if a.bank020 == '0':
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['20','0'])
                woori = cursor.fetchone()
                cursor.execute("UPDATE vacs_vact SET acct_st = %s WHERE acct_no = %s", ['1',woori[0].strip()])
            except Exception, e:
                print ("Can't call Insert", e)

            a.bank020 = woori[0].strip()

        if a.bank027 == '0':
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['27','0'])
                city = cursor.fetchone()
                cursor.execute("UPDATE vacs_vact SET acct_st = %s WHERE acct_no = %s", ['1',city[0].strip()])
            except Exception, e:
                print ("Can't call Insert", e)

            a.bank027 = city[0].strip()

        if a.bank071 == '0':
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['71','0'])
                woochegook = cursor.fetchone()
                cursor.execute("UPDATE vacs_vact SET acct_st = %s WHERE acct_no = %s", ['1',woochegook[0].strip()])
            except Exception, e:
                print ("Can't call Insert", e)

            a.bank071 = woochegook[0].strip()

        if a.bank081 == '0':
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['81','0'])
                hana = cursor.fetchone()
                cursor.execute("UPDATE vacs_vact SET acct_st = %s WHERE acct_no = %s", ['1',hana[0].strip()])
            except Exception, e:
                print ("Can't call Insert", e)

            a.bank081 = hana[0].strip()

        if a.bank088 == '0':
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['88','0'])
                shinhan = cursor.fetchone()
                cursor.execute("UPDATE vacs_vact SET acct_st = %s WHERE acct_no = %s", ['1',shinhan[0].strip()])
            except Exception, e:
                print ("Can't call Insert", e)

            a.bank088 = shinhan[0].strip()
        cursor.close()
        connection.commit()
        connection.close()
        a.save()

@csrf_exempt
@login_required
def notice(request):
    if request.method == "GET":
        com = Community.objects.all()

        return render(request, 'passenger/notice.html', {'com': com} );

    elif request.method == "POST":
        choice = request.POST.get('choice')

        cid = request.POST.get('cid')
        response_data = {}

        if choice:
            try:
                com = Community.objects.get(id=cid)

                com.clike = com.clike+1
                response_data['num'] = com.clike

                com.save()

                return HttpResponse(json.dumps(response_data), content_type="application/json")

            except Exception as e:

                return HttpResponse(e.message)

        else:
            response_data = {}
            aname = request.POST.get('aname')
            complain = request.POST.get('complain')
            plan = request.POST.get('plan')
            t = timeToDate()
            toDate = t.timeToYmd()
            c = Community(aname=aname, complain=complain, plan=plan,showdate = toDate,clike=0,dlike=0,disuser=[],disuserid=[],likeuserid=[],likeuser=[])
            c.save()

            com = Community.objects.all()

            return render(request, 'passenger/notice.html', {'com': com} );
