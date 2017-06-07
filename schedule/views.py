from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from schedule.models import HistoryScheduleTable, Inventory, ScheduleTable, Building, Branch, InventoryRequest, Area, Car
from passenger.models import Academy, Group, StudentInfo
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.core import serializers
from simple_history.models import HistoricalRecords
from passenger.dateSchedule import timeToDate
from rest_framework.parsers import FormParser
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from itertools import chain
from django.core.serializers import serialize
import datetime
import operator
import json
import logging
import collections

@csrf_exempt
def getAcaPhone(request):
    aid = request.GET.get('aid')
    academy = Academy.objects.get(id=aid)

    phonelist = []

    phonelist.append(academy.phone_1)
    phonelist.append(academy.phone_2)

    return JsonResponse({"phonelist":phonelist})

@csrf_exempt
def getCarPhone(request):
    carnum = request.GET.get('carnum')
    car = Car.objects.get(carname = carnum)

    phonelist = []

    phonelist.append(car.driver)
    phonelist.append(car.passenger)

    return JsonResponse({"phonelist":phonelist})



@csrf_exempt
def todayLoad(request):
    if request.method == "GET":
        offset = request.GET.get('offset')
        invenid = request.GET.get('invenid')
        stableid = request.GET.get('stableid')

        stable = ScheduleTable.objects.get(id = stableid)
        temp_slist = stable.slist
        temp_index = int(offset) - 1
        sinfoid = temp_slist[temp_index]

        sinfo = StudentInfo.objects.get(id=sinfoid)
        dict_sinfo = model_to_dict(sinfo)
        data = json.dumps(dict_sinfo)

        return HttpResponse(data, content_type="application/json")

    if request.method == "POST":
        offset = request.POST.get('offset')
        invenid = request.POST.get('invenid')
        stableid = request.POST.get('stableid')

        stable = ScheduleTable.objects.get(id = stableid)
        temp_tflag = stable.tflag
        temp_index = int(offset) - 1

        # 0 -> load, 1 -> unload
        if temp_tflag[temp_index] == 0:
            temp_tflag[temp_index] = 1
            button_flag = 0

        elif temp_tflag[temp_index] == 1:
            temp_tflag[temp_index] = 0
            button_flag = 1

        stable.tflag = temp_tflag
        stable.save()

        return HttpResponse(button_flag)

@csrf_exempt
def getSchedule(request):
    if request.method == "GET":
        car = request.GET.get('car')
        bid = request.GET.get('bid')
        aid = request.GET.get('aid')
        day = request.GET.get('day')

        if car:
            branch = Car.objects.get(id = car)
            invens = Inventory.objects.filter(carnum=car).filter(day = day)

            contacts = []

            for i in invens:
                contacts.extend(Inventory.objects.filter(id = i.id).prefetch_related('scheduletables'))

            return render_to_response('getCarSchedule.html', {"contacts": contacts,"car": car, 'user':request.user})


        invens = Inventory.objects.filter(bid = bid).filter(alist__contains = [aid]).filter(day = day)
        list_invensid = []
        contacts = []

        for i in invens:
            contacts.extend(Inventory.objects.filter(id = i.id).prefetch_related('scheduletables'))
            # list_invensid.append(i.id)

        # stables = ScheduleTable.objects.filter(iid__in = [iid for iid in list_invensid])

        # for j in invens:
        #     temp = [j]
        #     for k in stables:
        #         if j.id == k.iid:
        #             temp.append(k)
        #     contacts.extend(temp)

        return render_to_response('getSchedule.html', {"contacts": contacts, "bid" : bid, "aid" : aid,'user':request.user})

@csrf_exempt
def putSchedule(request):
    if request.method == "GET":
        bid = request.GET.get('bid')
        if bid:
            academy = Academy.objects.filter(bid = bid)
            group = Car.objects.filter(branchid = bid)

            return render_to_response('putSchedule.html', {"academy" : academy, "bid" : bid, "group" : group,'user':request.user})

    elif request.method == "POST":
        day = request.POST.get('day')
        carnum = request.POST.get('carnum')
        bid = request.POST.get('bid')
        req = request.POST.get('req')
        time = request.POST.getlist('time[]')
        addr = request.POST.getlist('addr[]')
        name = request.POST.getlist('name[]')
        name2 = request.POST.getlist('name[]')
        academy = request.POST.getlist('academy[]')
        load = request.POST.getlist('load[]')
        sid = request.POST.getlist('sid[]')


        try:
            snum = len(set(name)) - 1
            alist_temp = list(set([i for i in academy if i is not None and i != '']))
            alist_temp2 = ','.join(alist_temp)
            alist_temp3 = list(set(alist_temp2.split(',')))
            alist = []

            for a in alist_temp3:
                alist.append(int(a))

        except:
            return HttpResponse('error1')

        slist_temp = list(set([i for i in name if i is not None and i != '']))
        slist_temp2 = ','.join(slist_temp)
        slist_temp3 = list(set(slist_temp2.split(',')))
        slist = []

        studentInfo = StudentInfo.objects.filter(aid__contains = [aid for aid in alist]).filter(sname__in = [name for name in slist_temp3])

        for s in studentInfo:
            slist.append(s.id)

        stime = int(time[0].split(':')[0] + time[0].split(':')[1])
        etime = int(time[-1].split(':')[0] + time[-1].split(':')[1])

        tempSlist = set()
        for s in slist:
            tempSlist.add(s)

        slist = list(tempSlist)

        academyList = Academy.objects.filter(id__in = alist)
        anamelist_inven = []
        for a in academyList:
            anamelist_inven.append(a.name)


        try:
            inven = Inventory.objects.create(carnum = carnum, bid = bid, snum = snum, day = day , alist=alist, anamelist = anamelist_inven, slist=slist, stime = stime, etime = etime, req=req)

        except:
            return HttpResponse("error inventory save")


        iid = inven.id

        # lflag load -> 1 unload ->0 start -> 2 end -> 3
        for i in range(len(time)):
            if i == 0:
                stable = ScheduleTable(iid_id = iid, time = time[i], addr = addr[i], alist='{}', slist='{}', sname=list(name2[i]), tflag='{}', lflag=2)
                stable.save()

            elif i == len(time) - 1:
                stable = ScheduleTable(iid_id = iid, time = time[i], addr = addr[i], alist='{}', slist='{}', sname=list(name2[i]), tflag='{}', lflag=3)
                stable.save()

            elif 0 < i < len(time) - 1:
                sidlist = []
                sidtemp = []
                temp_aca = academy[i].split(',')
                temp_name = [n.strip() for n in name2[i].split(',')]

                student = StudentInfo.objects.filter(aid__contains=[ a for a in temp_aca]).filter(sname__in=[ stu for stu in temp_name ])

                for s in student:
                    sidtemp.append(s.id)

                temp_lflag = [0 for z in range(len(temp_name))]

                anamelist = []

                for aid in temp_aca:
                    aname = Academy.objects.get(id = aid)
                    anamelist.append(aname.name)

                stable = ScheduleTable(iid_id = iid, time = time[i], addr = addr[i], alist=temp_aca, anamelist = anamelist, slist=sidtemp, sname=temp_name, tflag=temp_lflag, lflag=load[i])
                stable.save()

        academy = Academy.objects.filter(bid = bid)
        group = Group.objects.filter(bid = bid)

        return render_to_response('putSchedule.html', {"academy" : academy, "bid" : bid, "group" : group,'user':request.user})


@csrf_exempt
def updateSchedule(request):
    if request.method == "GET":
        searchflag = request.GET.get('searchinven')

        if searchflag:
            if searchflag == '2':
                area = Area.objects.all()
                carnum = request.GET.get('car')
                searchflag = request.GET.get('searchinven')
                bid = request.GET.get('bid')
                day = request.GET.get('day')
                time = int(request.GET.get('time'))

                academy = Academy.objects.filter(bid=bid)
                branch = Branch.objects.get(id = bid)
                carlist = Car.objects.filter(branchid=bid)

                invens = Inventory.objects.filter(bid = bid).filter(day = day).filter(etime__gte = time-90, stime__lte = time+90).filter(carnum = carnum)

                contacts = []

                for i in invens:
                    contacts.extend(Inventory.objects.filter(id = i.id).prefetch_related('scheduletables'))

                return render_to_response('supdateSchedule.html',{"area":area,"time":time,"day":day,"branch":branch,"academy":academy,"carlist": carlist,"carnum": carnum,"bid":bid,"contacts":contacts,'user':request.user})

        area = Area.objects.all()
        return render_to_response('supdateSchedule.html',{'area':area,'user':request.user})


    elif request.method == "POST":
        area = Area.objects.all()
        #updateflag 1(select branch),2(search inven)
        updateflag = request.POST.get('updateflag')
        #update 1(update inven,stable),0(delete inven,stable)
        update = request.POST.get('update')


        #updateflag == 1: selects area for getting branch
        if updateflag == '1':
            areaid = request.POST.get('area')
            branch = Branch.objects.filter(areaid = areaid)
            data = serialize('json', branch)

            return HttpResponse(data, content_type="application/json" )

        if updateflag == '2':
            #searchflag -> 1: first searching
            searchflag = request.POST.get('searchinven')
            bid = request.POST.get('bid')
            day = request.POST.get('day')
            time = int(request.POST.get('time'))

            if searchflag == '1':
                academy = Academy.objects.filter(bid=bid)
                branch = Branch.objects.get(id = bid)
                carlist = Car.objects.filter(branchid=bid)

                invens = Inventory.objects.filter(bid = bid).filter(day = day).filter(etime__gte = time-90, stime__lte = time+90).filter(carnum = carlist[0].carname)

                contacts = []

                for i in invens:
                    contacts.extend(Inventory.objects.filter(id = i.id).prefetch_related('scheduletables'))

                return render_to_response('supdateSchedule.html',{"area":area,"time":time,"academy":academy,"day":day,"carlist": carlist,"bid":bid,"contacts":contacts,'user':request.user})

            # if searchflag == '2':
            #     carnum = request.POST.get('car')
            #     academy = Academy.objects.filter(bid=bid)
            #     branch = Branch.objects.get(id = bid)
            #     carlist = Car.objects.filter(branchid=bid)
            #
            #     invens = Inventory.objects.filter(bid = bid).filter(day = day).filter(etime__gte = time-60, stime__lte = time+60).filter(carnum = carnum)
            #
            #     contacts = []
            #
            #     for i in invens:
            #         contacts.extend(Inventory.objects.filter(id = i.id).prefetch_related('scheduletables'))
            #
            #     return render_to_response('supdateSchedule.html',{"area":area,"time":time,"day":day,"branch":branch,"academy":academy,"carlist": carlist,"carnum": carnum,"bid":bid,"contacts":contacts,'user':request.user})

        #update -> 1 : update inven
        if update == '1':
            iid = request.POST.get('iid')
            bid = request.POST.get('bid')
            time = request.POST.getlist('time[]')
            addr = request.POST.getlist('addr[]')
            name = request.POST.getlist('name[]')
            name2 = request.POST.getlist('name[]')
            academy = request.POST.getlist('academy[]')
            load = request.POST.getlist('load[]')
            sid = request.POST.getlist('sid[]')

            #searchTime,day,area,branch for inventory searching and redirection
            searchTime = request.POST.get('searchTime')
            day = request.POST.get('day')
            area = Area.objects.all()
            branch = Branch.objects.filter(id = bid)
            #carlist for searching with carnum and redirection
            carlist = Car.objects.filter(branchid=bid)
            #for redirection
            carnum = request.POST.get('invencar')

            #Check register student
            for i in range(len(time)):
                if 0 < i < len(time) - 1:
                    sidlist = []
                    temp_aca = [int(a.strip()) for a in academy[i].split(',')]
                    temp_name = [n.strip() for n in name2[i].split(',')]
                    #student = StudentInfo.objects.filter(aid__in=[ a for a in temp_aca])

                    for k in temp_name:
                        s = StudentInfo.objects.filter(sname = k)
                        if s:
                            if
                            continue
                        else:
                            return HttpResponse("Not Register Student")

            try:
                snum = len(set(name))
                alist_temp = list(set([i for i in academy if i is not None and i != '']))
                alist_temp2 = ','.join(alist_temp)
                alist_temp3 = list(set(alist_temp2.split(',')))
                alist = []

                for a in alist_temp3:
                    alist.append(int(a))

            except:
                return HttpResponse('error1')

            slist_temp = list(set([i for i in name if i is not None and i != '']))
            slist_temp2 = ','.join(slist_temp)
            slist_temp3 = [n.strip() for n in list(set(slist_temp2.split(',')))]

            slist = []

            studentInfo = StudentInfo.objects.filter(aid__contains = [aid for aid in alist]).filter(sname__in = [name for name in slist_temp3])

            for s in studentInfo:
                slist.append(s.id)

            stime = int(time[0].split(':')[0] + time[0].split(':')[1])
            etime = int(time[-1].split(':')[0] + time[-1].split(':')[1])

            anamelist_inven = []

            academyList = Academy.objects.filter(id__in = alist)


            for a in academyList:
                anamelist_inven.append(a.name)


            Inventory.objects.filter(id=iid).update(snum = snum,alist=alist, anamelist = anamelist_inven, slist=slist, stime = stime, etime = etime)

            #delete stable before updateing stable
            delete_stable = ScheduleTable.objects.filter(iid_id=iid)
            delete_stable.delete()

            # lflag load -> 1 unload ->0 start -> 2 end -> 3
            for i in range(len(time)):
                if i == 0:
                    stable = ScheduleTable(iid_id = iid, time = time[i], addr = addr[i], alist='{}', slist='{}', sname=list(name2[i]), tflag='{}', lflag=2)
                    stable.save()

                elif i == len(time) - 1:
                    stable = ScheduleTable(iid_id = iid, time = time[i], addr = addr[i], alist='{}', slist='{}', sname=list(name2[i]), tflag='{}', lflag=3)
                    stable.save()

                elif 0 < i < len(time) - 1:
                    sidlist = []
                    sidtemp = []
                    temp_aca = academy[i].split(',')
                    temp_name = [n.strip() for n in name2[i].split(',')]

                    student = StudentInfo.objects.filter(aid__contains=[ a for a in temp_aca]).filter(sname__in=[ stu for stu in temp_name ])

                    for s in student:
                        sidtemp.append(s.id)

                    temp_lflag = [0 for z in range(len(temp_name))]

                    anamelist = []

                    for aid in temp_aca:
                        aname = Academy.objects.get(id = aid)
                        anamelist.append(aname.name)

                    stable = ScheduleTable(iid_id = iid, time = time[i], addr = addr[i], alist=temp_aca, anamelist = anamelist, slist=sidtemp, sname=temp_name, tflag=temp_lflag, lflag=load[i])
                    stable.save()

            #redirect
            carnum = request.POST.get('invencar')
            area = Area.objects.all()
            academy = Academy.objects.filter(bid=bid)

            invens = Inventory.objects.filter(bid = bid).filter(day = day).filter(etime__gte = int(searchTime)-90, stime__lte = int(searchTime)+90).filter(carnum = carnum)

            contacts = []

            for i in invens:
                contacts.extend(Inventory.objects.filter(id = i.id).prefetch_related('scheduletables'))

            return render_to_response('supdateSchedule.html',{"area":area,"time":searchTime,"academy":academy,"day":day,"carlist": carlist,"bid":bid,"contacts":contacts,'user':request.user})

        #update -> 0 delete inventory, stable
        elif update == '0':
            iid = request.POST.get('iid')
            bid = request.POST.get('bid')
            #searchTime,day,area,branch for inventory searching and redirection
            searchTime = request.POST.get('searchTime')
            day = request.POST.get('day')
            area = Area.objects.all()
            branch = Branch.objects.filter(id = bid)
            #carlist for searching with carnum and redirection
            carlist = Car.objects.filter(branchid=bid)
            #for redirection
            carnum = request.POST.get('invencar')

            try:
                stable  = ScheduleTable.objects.filter(iid_id = iid)
                stable.delete()

            except:
                return HttpResponse("inven delete error:stable")

            try:
                inven = Inventory.objects.get(id = iid)
                inven.delete()
            except:
                return HttpResponse("inven delete error:inventory")

            #redirect
            academy = Academy.objects.filter(bid=bid)
            invens = Inventory.objects.filter(bid = bid).filter(day = day).filter(etime__gte = int(searchTime)-90, stime__lte = int(searchTime)+90).filter(carnum = carnum)

            contacts = []

            for i in invens:
                contacts.extend(Inventory.objects.filter(id = i.id).prefetch_related('scheduletables'))

            return render_to_response('supdateSchedule.html',{"area":area,"time":searchTime,"academy":academy,"day":day,"carlist": carlist,"bid":bid,"contacts":contacts,'user':request.user})

@csrf_exempt
def studentLoad(request):
    if request.method == "POST":
        aid = request.POST.get('aid')

        stu = StudentInfo.objects.filter(aid__contains = [aid])
        data = serialize('json', stu)

        return HttpResponse(data, content_type="application/json" )

@csrf_exempt
@login_required
def updateArea(request):
    if request.method == "GET":
        area = Area.objects.all()
        return render_to_response('supdateArea.html',{'area':area,'user':request.user})

    elif request.method == "POST":
        update = request.POST.get('update')
        # save
        if update == '1':
            areaids = request.POST.getlist('areaid[]')
            names = request.POST.getlist('name[]')

            Area.objects.exclude(id__in=areaids).delete()
            i = 0
            for i in range(len(names)):
                if (areaids[i] == '-1'):
                    area = Area(name = names[i])
                    area.save()
	        else:
            	    area = Area.objects.get(id = areaids[i])
                    area.name = names[i]
                    area.save()


            areaList = Area.objects.all()
            return render_to_response('supdateArea.html',{"area":areaList,'user':request.user})

        # delete
        elif update == '0':
            iid = request.POST.get('iid')
            bid = request.POST.get('bid')

            academy = Academy.objects.filter(bid=bid)

            try:
                stable  = ScheduleTable.objects.filter(iid_id = iid)
                stable.delete()

            except:
                return HttpResponse("inven delete error:stable")

            try:
                inven = Inventory.objects.get(id = iid)
                inven.delete()
            except:
                return HttpResponse("inven delete error:inventory")

            return render_to_response('supdateSchedule.html',{"academy":academy,"bid":bid,'user':request.user})

        else:
            bid = request.POST.get('bid')
            day = request.POST.get('day')
            time = int(request.POST.get('time'))
            gid = request.POST.get('gid')

            carnum = Group.objects.filter(bid=bid).order_by('gid')
            academy = Academy.objects.filter(bid=bid)
            branch = Branch.objects.get(id = bid)

            invens = Inventory.objects.filter(bid = bid).filter(day = day).filter(etime__gte = time-60, stime__lte = time+60).filter(carnum = carnum[0].gid)

            list_invensid = []
            contacts = []

            for i in invens:
                contacts.extend(Inventory.objects.filter(id = i.id).prefetch_related('scheduletables'))

            return render_to_response('supdateSchedule.html',{"time":time,"day":day,"branch":branch,"academy":academy,"carnum": carnum,"bid":bid,"contacts":contacts,'user':request.user})

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
    allacademy = Academy.objects.all()

    if aid is not None and aid != '' and startdate is not None and startdate != '' and enddate is not None and enddate != '':
        start_date = datetime.date(*map(int, startdate.split('-')))
        end_date = datetime.date(*map(int, enddate.split('-')))
        total_days = (end_date - start_date).days + 1
        for day_number in range(total_days):
            single_history = {}
            single_date = (start_date + datetime.timedelta(days = day_number)).strftime('%Y-%m-%d')
            academiesDictionary = {}
            schedules = []

            #return HttpResponse(single_date)
            iids = HistoryScheduleTable.objects.filter(alist__contains = [aid]).filter(date = single_date).order_by('time').values_list('iid_id', flat=True).distinct()
            uniq_iids = reduce(lambda x,y: x+[y] if x==[] or x[-1] != y else x, iids, [])
            for i in uniq_iids:
                academyset = set()
                scheduletable = HistoryScheduleTable.objects.filter(date = single_date).filter(iid_id = i)
                schedules.append(scheduletable)
                for schedule in scheduletable:
                    for academy in schedule.academies.all():
                        academyset.add(academy.name)
                academiesDictionary[i] = academyset

            single_history['date'] = single_date

            history.append(single_history)

    #return HttpResponse(academy)
    return render_to_response('getHistory.html', {"history": history, "academy": allacademy, "aid" : aid, 'startdate': startdate, 'enddate': enddate, 'user':request.user})

@csrf_exempt
@login_required
def analyze(request):
    if request.method == 'GET':
    	branch = request.GET.get('branch')
    	daterange = request.GET.get('daterange')
        startdate = request.GET.get('startdate')
        enddate = request.GET.get('enddate')
    elif request.method == 'POST':
    	branch = request.POST.get('branch')
    	daterange = request.POST.get('daterange')
        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')

    if daterange is not None and daterange != '':
    	(startdate, enddate) = daterange.split(' - ')

    sharingInventoryArray = collections.defaultdict(dict)

    if branch is not None and branch != '' and startdate is not None and startdate != '' and enddate is not None and enddate != '':
        start_date = datetime.date(*map(int, startdate.split('-')))
        end_date = datetime.date(*map(int, enddate.split('-')))
        total_days = (end_date - start_date).days + 1
        for day_number in range(total_days):
            single_date = (start_date + datetime.timedelta(days = day_number)).strftime('%Y-%m-%d')

            #return HttpResponse(single_date)
            b = Branch.objects.get(id = branch)
            for car in b.carlist:
                sharingInventoryArray[car][single_date] = HistoryScheduleTable.objects.filter(date = single_date).filter(carnum = car).values_list('iid_id', flat=True).distinct().count()

    return HttpResponse(json.dumps(sharingInventoryArray), content_type="application/json")

def chart(request):
    return render_to_response('chart.html', {'user':request.user})

@csrf_exempt
def reqInventory(request):
    if request.method == "POST":
        iid = request.POST.get('iid')
        req = request.POST.get('req')

        inven = Inventory.objects.get(id=iid)
        inven.req = req
        inven.save()

        return HttpResponse(req)
