#
from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from passenger.models import Commute, Academy, Schedule, ShuttleSchedule, Group, ScheduleDate,Branch,Community
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.core import serializers
from passenger.dateSchedule import timeToDate
import json

@login_required
def main(request):
    academies = Academy.objects.order_by('-gid')
    groups = Group.objects.order_by('-gid')
    branch = Branch.objects.order_by('-id')

    return render_to_response('passenger/main.html', {"academies" : academies, "groups": groups, "branch" : branch,'user':request.user})



def sturegi(request):
    return render_to_response('passenger/typeform_sr.html')

@csrf_exempt
def schedule(request):
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

def opti(request):
    if request.method =="GET":
        schedule = request.GET.get('schedule')
        aid = request.GET.get('aid')
        academy = Academy.objects.get(id = aid)

    return render_to_response('passenger/optimizationDistance.html', {"academy" : academy, "schedule" : schedule,'user':request.user})

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


@csrf_exempt
def academySchedule(request):
    if request.method == "GET":
        aid = request.GET.get('aid')
        day = request.GET.get('day')
        academy = Academy.objects.get(id = aid)
        bid = academy.bid
        contacts = ShuttleSchedule.objects.filter(bid=bid).filter(a_name__contains = academy.name).filter(day=day).order_by('time')

        return render_to_response('passenger/academySchedule.html', {"contacts" : contacts, "aid" : aid,'user':request.user})

@login_required
def driverSchedule(request):
    if request.method == "GET":
        gid = request.GET.get('gid')
        day = request.GET.get('day')
        contacts = ShuttleSchedule.objects.filter(gid = gid).filter(day=day).order_by('time')

        return render_to_response('passenger/driverSchedule.html', {"contacts" : contacts, "gid" : gid,'user':request.user})

@csrf_exempt
def updateSchedule(request):
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

    elif request.method == "POST":
        what = request.POST.get('what')
        aid = request.POST.get('aid')
        date = request.POST.get('date')
        toDate = request.POST.get('to')
        fromDate = request.POST.get('from')

        if what == "single":
            a_name = Academy.objects.get(id = aid).name
            contacts = ScheduleDate.objects.filter(date=date).filter(a_name__contains = a_name)
            count = len(contacts)

            return render_to_response('passenger/viewDateSchedule.html', {"contacts": contacts, "count" : count,'user':request.user})

        elif what == "range":
            t = timeToDate()
            toD = t.timeToDtype(toDate)
            fromD = t.timeToDtype(fromDate)
            a_name = Academy.objects.get(id = aid).name

            contacts = ScheduleDate.objects.filter(today__range=[fromD,toD]).filter(a_name__contains = a_name)
            count = len(contacts)
            return render_to_response('passenger/viewDateSchedule.html', {"contacts": contacts, "count" : count,'user':request.user})

@csrf_exempt
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
