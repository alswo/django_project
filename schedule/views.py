# -*- coding: utf-8 -*-
import logging
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from schedule.models import HistoryScheduleTable, Inventory, ScheduleTable, Building, Branch, InventoryRequest, Area, Car, RealtimeLocation, EditedInven, EditedScheduleTable, TodayLoadTimeLog, InvenAuditing
from passenger.models import Academy, Group, StudentInfo, Profile
from django.db.models import Q
from django.db.models import Prefetch
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
import collections
import re
from schedule.updateInventory import UpdateInven 
from schedule.createInventory import CreateInven
from schedule.maintainTodayLoad import getUnloadSid, getTflag

class TimeHistory:
	def __init__(self):
		self.carnum = -1
		self.academies = set()
		self.scheduletable = list()
		self.warning = 0
class DailyHistory:
	def __init__(self):
		self.date = ""
		self.timehistory = list()

def set_audit(comment, done, user):
    InvenAuditing.objects.create(create_time = str(datetime.datetime.now())[:16], create_user = user, comment = comment, done = done)

def invenToJson(invens):
    contacts = []

    for i in invens:
        inventory={}
        inventory['id'] = i.id
        inventory['carnum'] = i.carnum
        inventory['bid'] = i.bid
        inventory['day'] = i.day
        inventory['alist'] = i.alist
        inventory['anamelist'] = i.anamelist
        inventory['slist'] = i.slist
        inventory['stime'] = i.stime
        inventory['etime'] = i.etime
        inventory['week1'] = i.week1
        inventory['week2'] = i.week2
        inventory['week3'] = i.week3
        inventory['req'] = i.req
        inventory['memo'] = i.memo
        inventory['passenger'] = 1

        for studentInfo in i.slist:
            try:
                sInfo = StudentInfo.objects.get(id = studentInfo)
            except StudentInfo.DoesNotExist:
                continue

            if sInfo.birth_year == None or ((datetime.datetime.now().year - int(sInfo.birth_year) + 1) <= 13):
                inventory['passenger'] = 0
                break

        schedules = ScheduleTable.objects.filter(iid = i.id)

        inventory['schedule'] = []

        for s in schedules:
            schedule={}
            schedule['id'] = s.id
            schedule['time'] = s.time
            schedule['addr'] = s.addr
            schedule['req'] = s.req
            schedule['alist'] = s.alist
            schedule['anamelist'] = s.anamelist
            schedule['slist'] = s.slist
            schedule['sinfo'] = []

            for si in s.slist:
                sInfo={}
                try:
                    studentInfo = StudentInfo.objects.get(id = si)
                    academy = Academy.objects.get(id = studentInfo.aid_id)
                    sInfo['id'] = studentInfo.id
                    sInfo['name'] = studentInfo.sname
                    sInfo['aid'] = studentInfo.aid
                    sInfo['aname'] = academy.name
                    sInfo['aphone'] = academy.phone_1
                    sInfo['grade'] = studentInfo.grade
                    sInfo['phone1'] = studentInfo.phone1
                    sInfo['phonelist'] = studentInfo.phonelist
                    sInfo['parents_phonenumber'] = studentInfo.parents_phonenumber
                    sInfo['grandparents_phonenumber'] = studentInfo.grandparents_phonenumber
                    sInfo['self_phonenumber'] = studentInfo.self_phonenumber
                    sInfo['care_phonenumber'] = studentInfo.care_phonenumber

		except:
		    HttpResponse(si)

	        schedule['sinfo'].append(sInfo)

	    schedule['sname']= s.sname
            schedule['tflag'] = s.tflag
            schedule['lflag'] = s.lflag

            inventory['schedule'].append(schedule)

        contacts.append(inventory)

    return contacts

#return inventory, editedInven where updateSchedule
def getContacts(bid, day, carnum, week, searchTime, aid = -1):
    
    contacts = []
    
    if aid == -1:
        if searchTime == '':
            if week == 0:
                contacts.extend(Inventory.objects.filter(bid = bid).filter(day = day).filter(carnum = carnum).prefetch_related('scheduletables'))

            elif week == 1:
                contacts.extend(Inventory.objects.filter(bid = bid).filter(day = day).filter(carnum = carnum).filter(week1 = 0).prefetch_related('scheduletables'))
                contacts.extend(EditedInven.objects.filter(bid = bid).filter(day = day).filter(carnum = carnum).filter(week = 1).prefetch_related('editedscheduletables'))

            elif week == 2:
                contacts.extend(Inventory.objects.filter(bid = bid).filter(day = day).filter(carnum = carnum).filter(week2 = 0).prefetch_related('scheduletables'))
                contacts.extend(EditedInven.objects.filter(bid = bid).filter(day = day).filter(carnum = carnum).filter(week = 2).prefetch_related('editedscheduletables'))

            elif week == 3:
                contacts.extend(Inventory.objects.filter(bid = bid).filter(day = day).filter(carnum = carnum).filter(week3 = 0).prefetch_related('scheduletables'))
                contacts.extend(EditedInven.objects.filter(bid = bid).filter(day = day).filter(carnum = carnum).filter(week = 3).prefetch_related('editedscheduletables'))

        else:
            searchTime = int(searchTime)
        
            if week == 0:
                contacts.extend(Inventory.objects.filter(bid = bid).filter(day = day).filter(etime__gte = searchTime-90, stime__lte = searchTime+90).filter(carnum = carnum).prefetch_related('scheduletables'))

            elif week == 1:
                contacts.extend(Inventory.objects.filter(bid = bid).filter(day = day).filter(week1=0).filter(etime__gte = searchTime-90, stime__lte = searchTime+90).filter(carnum = carnum).prefetch_related('scheduletables'))
                contacts.extend(EditedInven.objects.filter(bid = bid).filter(day = day).filter(week = 1).filter(etime__gte = searchTime-90, stime__lte = searchTime+90).filter(carnum = carnum).prefetch_related('editedscheduletables'))

            elif week == 2:
                contacts.extend(Inventory.objects.filter(bid = bid).filter(day = day).filter(week2=0).filter(etime__gte = searchTime-90, stime__lte = searchTime+90).filter(carnum = carnum).prefetch_related('scheduletables'))
                contacts.extend(EditedInven.objects.filter(bid = bid).filter(day = day).filter(week = 2).filter(etime__gte = searchTime-90, stime__lte = searchTime+90).filter(carnum = carnum).prefetch_related('editedscheduletables'))


            elif week == 3:
                contacts.extend(Inventory.objects.filter(bid = bid).filter(day = day).filter(week3=0).filter(etime__gte = searchTime-90, stime__lte = searchTime+90).filter(carnum = carnum).prefetch_related('scheduletables'))
                contacts.extend(EditedInven.objects.filter(bid = bid).filter(day = day).filter(week = 3).filter(etime__gte = searchTime-90, stime__lte = searchTime+90).filter(carnum = carnum).prefetch_related('editedscheduletables'))

    else:
        if searchTime == '':

            if week == 0:
                contacts.extend(Inventory.objects.filter(bid = bid).filter(day = day).filter(alist__contains = [aid]).prefetch_related('scheduletables'))

            elif week == 1:
                contacts.extend(Inventory.objects.filter(bid = bid).filter(day = day).filter(alist__contains = [aid]).filter(week1 = 0).prefetch_related('scheduletables'))
                contacts.extend(EditedInven.objects.filter(bid = bid).filter(day = day).filter(alist__contains = [aid]).filter(week = 1).prefetch_related('editedscheduletables'))

            elif week == 2:
                contacts.extend(Inventory.objects.filter(bid = bid).filter(day = day).filter(alist__contains = [aid]).filter(week2 = 0).prefetch_related('scheduletables'))
                contacts.extend(EditedInven.objects.filter(bid = bid).filter(day = day).filter(alist__contains = [aid]).filter(week = 2).prefetch_related('editedscheduletables'))

            elif week == 3:
                contacts.extend(Inventory.objects.filter(bid = bid).filter(day = day).filter(alist__contains = [aid]).filter(week3 = 0).prefetch_related('scheduletables'))
                contacts.extend(EditedInven.objects.filter(bid = bid).filter(day = day).filter(alist__contains = [aid]).filter(week = 3).prefetch_related('editedscheduletables'))

        else:
            searchTime = int(searchTime)

            if week == 0:
                contacts.extend(Inventory.objects.filter(bid = bid).filter(day = day).filter(alist__contains = [aid]).filter(etime__gte = searchTime-90, stime__lte = searchTime+90).prefetch_related('scheduletables'))

            elif week == 1:
                contacts.extend(Inventory.objects.filter(bid = bid).filter(day = day).filter(alist__contains = [aid]).filter(week1=0).filter(etime__gte = searchTime-90, stime__lte = searchTime+90).prefetch_related('scheduletables'))
                contacts.extend(EditedInven.objects.filter(bid = bid).filter(day = day).filter(alist__contains = [aid]).filter(week = 1).filter(etime__gte = searchTime-90, stime__lte = searchTime+90).prefetch_related('editedscheduletables'))

            elif week == 2:
                contacts.extend(Inventory.objects.filter(bid = bid).filter(day = day).filter(alist__contains = [aid]).filter(week2=0).filter(etime__gte = searchTime-90, stime__lte = searchTime+90).prefetch_related('scheduletables'))
                contacts.extend(EditedInven.objects.filter(bid = bid).filter(day = day).filter(alist__contains = [aid]).filter(week = 2).filter(etime__gte = searchTime-90, stime__lte = searchTime+90).prefetch_related('editedscheduletables'))


            elif week == 3:
                contacts.extend(Inventory.objects.filter(bid = bid).filter(day = day).filter(alist__contains = [aid]).filter(week3=0).filter(etime__gte = searchTime-90, stime__lte = searchTime+90).prefetch_related('scheduletables'))
                contacts.extend(EditedInven.objects.filter(bid = bid).filter(day = day).filter(alist__contains = [aid]).filter(week = 3).filter(etime__gte = searchTime-90, stime__lte = searchTime+90).prefetch_related('editedscheduletables'))  

    contacts = sorted(contacts, key=lambda x: x.stime,reverse=False)

    return contacts

def checkEditedInven(iid, week):
    try:
        eInven = EditedInven.objects.get(id = iid, week = week)
        eInven_index = 0
    except:
        eInven_index = 1
    
    return eInven_index

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
    if request.method == "POST":
        sid = int(request.POST.get('sid'))
        stableid = int(request.POST.get('stableid'))

        stable = ScheduleTable.objects.get(id = stableid)
        temp_tflag = stable.tflag
        slist = stable.slist
        temp_index = slist.index(sid)

        # 0 -> load, 1 -> unload
        if temp_tflag[temp_index] == 0:
            temp_tflag[temp_index] = 1
            button_flag = 0

        elif temp_tflag[temp_index] == 1:
            temp_tflag[temp_index] = 0
            button_flag = 1

        stable.tflag = temp_tflag
        stable.save()

        reqtime = str(datetime.datetime.now())[:16]

        TodayLoadTimeLog.objects.create(sid_id = sid , stable_id = stableid, reqtime = reqtime)

        return HttpResponse(button_flag)

@csrf_exempt
def getSchedule(request):
    if request.method == "GET":
        car = request.GET.get('car')
        bid = request.GET.get('bid')
        aid = request.GET.get('aid')
        day = request.GET.get('day')
        uid = request.user.id

	t = timeToDate()
        today = t.timeToYmd()
       	realtimelocation = RealtimeLocation.objects.filter(date=today, carnum=car).order_by('schedule_time').last()
		
	if (day and t.timeToD() == day):
		pass
	elif (realtimelocation != None):
		realtimelocation = None

        if request.user.is_staff:
            
            invens = Inventory.objects.filter(bid = bid).filter(alist__contains = [aid]).filter(day = day)
            list_invensid = []
            contacts = invenToJson(invens)

            if car:
                cars = Car.objects.filter(branchid_id = bid)
                branch = Car.objects.get(carname = car)
                invens = Inventory.objects.filter(carnum=car).filter(day = day)

                contacts = invenToJson(invens)

                return render_to_response('getCarSchedule.html', {"cars" : cars, "bid": bid, "contacts": contacts,"car": car, 'user':request.user, 'realtimelocation':realtimelocation, 'day':day})

            return render_to_response('getSchedule.html', {"day" : day, "contacts": contacts, "bid" : bid, "aid" : aid,'user':request.user})

        elif request.user.groups.filter(name__in = ['academy']).exists():
            if day:
                invens = Inventory.objects.filter(bid = bid).filter(alist__contains = [aid]).filter(day = day)
                list_invensid = []

                contacts = invenToJson(invens)

                return render_to_response('getSchedule.html', {"day" : day, "contacts": contacts, "bid" : bid, "aid" : aid,'user':request.user})

            else:
                profile = Profile.objects.get(user=request.user)
                aid = profile.aid
                bid = profile.bid

                invens = Inventory.objects.filter(bid = bid).filter(alist__contains = [aid]).filter(day='월')

                list_invensid = []
                contacts = invenToJson(invens)

                return render_to_response('getSchedule.html', {"day" : day, "contacts": contacts, "bid" : bid, "aid" : aid,'user':request.user})

        elif request.user.groups.filter(name__in = ['driver']).exists():
            cars = Car.objects.filter(branchid_id = bid)
            invens = Inventory.objects.filter(carnum=car).filter(day = day)

            contacts = invenToJson(invens)

            return render_to_response('getCarSchedule.html', {"bid": bid, "cars":cars, "day" : day, "contacts": contacts,"car": car, 'user':request.user, 'realtimelocation':realtimelocation, 'day':day})

        return HttpResponse('로그인 후 사용해주세요.')

@csrf_exempt
def putScheduleForm(request):
    weekdaylist = ['월', '화', '수', '목', '금', '토']
    if request.method == "GET":
        bid = request.GET.get('bid')
        carnum = int(request.GET.get('carnum', '0'))
        day = request.GET.get('day')
        week = int(request.GET.get('week', '0'))

    elif request.method == 'POST':
        times = request.POST.getlist('time[]')
        addrs = request.POST.getlist('addr[]')

    if bid:
        academy = Academy.objects.filter(bid = bid)
        group = Car.objects.filter(branchid = bid)

    return render_to_response('putSchedule.html', {"academy" : academy, "bid" : bid,"carnum":carnum,"day":day,"week":week, "group" : group,'user':request.user, 'weekdaylist': weekdaylist, 'weeknum_range': range(0, 4), 'times': times, 'addrs': addrs})


@csrf_exempt
def putSchedule(request):
    weekdaylist = ['월', '화', '수', '목', '금', '토']
    if request.method == "GET":
        bid = request.GET.get('bid')
        carnum = int(request.GET.get('carnum', '0'))
        day = request.GET.get('day')
        week = int(request.GET.get('week', '0'))

    elif request.method == "POST":
        day = request.POST.getlist('day[]')
        carnum = request.POST.get('carnum')
        bid = request.POST.get('bid')
        req = request.POST.get('req')
        time = request.POST.getlist('time[]')
        addr = request.POST.getlist('addr[]')
        name = request.POST.getlist('name[]')
        name2 = request.POST.getlist('name[]')
        load = request.POST.getlist('load[]')
        sid = request.POST.getlist('sid[]')
        week = int(request.POST.get('week'))
        alist = request.POST.getlist('alist[]')

        if not alist:
            alist = 0

        putInven = CreateInven(bid,carnum,day,req,time,addr,name,name2,load,sid,week,alist)

        if putInven.setAlist() == 1:
            return HttpResponse('error setAlist')

        if putInven.setSlist() == 1:
            return HttpResponse('error setSlist')

        if putInven.setANameList() == 1:
            return HttpResponse('error setANameList')

        if putInven.setSEtime() == 1:
            return HttpResponse('error setSEtime')

        if week == 0:
            putInven.setWeek0()

        elif week == 1:
            putInven.setWeek1()

        elif week == 2:
            putInven.setWeek2()

        else:
            putInven.setWeek3()

    if bid:
        academy = Academy.objects.filter(bid = bid)
        group = Car.objects.filter(branchid = bid)

    return render_to_response('putSchedule.html', {"academy" : academy, "bid" : bid,"carnum":carnum,"day":day,"week":week, "group" : group,'user':request.user, 'weekdaylist': weekdaylist, 'weeknum_range': range(0, 4)})


@csrf_exempt
def updateSchedule(request):
    if request.method == "GET":
        searchflag = request.GET.get('searchinven')
        if searchflag:
            if searchflag == '2':
                area = Area.objects.all()
                carnum = int(request.GET.get('car'))
                week = request.GET.get('week')
                searchflag = request.GET.get('searchinven')
                bid = int(request.GET.get('bid'))
                day = request.GET.get('day')
                searchTime = request.GET.get('searchTime')
                areaid = request.GET.get('areaid')

                academy = Academy.objects.filter(bid=bid)
                branch = Branch.objects.filter(areaid = areaid)

                carlist = Car.objects.filter(branchid=bid)

                if week == None:
                    week = 0

                else:
	            week = int(week)

                contacts = []
                
                contacts = getContacts(bid, day, carnum, week, searchTime)

                return render_to_response('supdateSchedule.html',{"area":area,"searchTime":searchTime,"day":day,"branch":branch,"academy":academy,"carlist": carlist,"carnum": carnum,"bid":bid,"areaid": areaid,"week": week,"contacts":contacts,'user':request.user})


        area = Area.objects.all()
        branch = Branch.objects.all()

        return render_to_response('supdateSchedule.html',{'area':area, 'branch': branch, 'user':request.user})


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
            areaid = 0
            bid = int(request.POST.get('bid'))
            day = request.POST.get('day')
            searchTime = request.POST.get('searchTime')

            if searchflag == '1':
                academy = Academy.objects.filter(bid=bid)
                if (request.POST.get('area')):
                    areaid = int(request.POST.get('area'))
                    branch = Branch.objects.filter(areaid = areaid)
                else:
                    branch = Branch.objects.all()
                carlist = Car.objects.filter(branchid=bid)
                carnum = carlist[0].carname

                if searchTime == '':
                    invens = Inventory.objects.filter(bid = bid).filter(day = day).filter(carnum = carlist[0].carname)

                    contacts = []

                    for i in invens:
                        contacts.extend(Inventory.objects.filter(id = i.id).prefetch_related('scheduletables'))

                    return render_to_response('supdateSchedule.html',{"area":area,"searchTime":searchTime,"academy":academy,"branch":branch,"day":day,"carlist": carlist,"carnum":carnum,"bid":bid,"areaid": areaid,"week": 0,"contacts":contacts,'user':request.user})

                else:
                    searchTime = int(searchTime)
                    invens = Inventory.objects.filter(bid = bid).filter(day = day).filter(etime__gte = searchTime-90, stime__lte = searchTime+90).filter(carnum = carlist[0].carname)

                    contacts = []

                    for i in invens:
                        contacts.extend(Inventory.objects.filter(id = i.id).prefetch_related('scheduletables'))

                    return render_to_response('supdateSchedule.html',{"area":area,"searchTime":searchTime,"academy":academy,"branch":branch,"day":day,"carlist": carlist,"carnum":carnum,"bid":bid,"areaid": areaid,"week": 0 ,"contacts":contacts,'user':request.user})

        #update -> 1 : update inven
        if update == '1':
            iid = int(request.POST.get('iid'))
            areaid = int(request.POST.get('areaid'))
            bid = int(request.POST.get('bid'))
            week = int(request.POST.get('week'))
            time = request.POST.getlist('time[]')
            addr = request.POST.getlist('addr[]')
            req = request.POST.getlist('req[]')
            name = request.POST.getlist('name[]')
            name2 = request.POST.getlist('name[]')
            academy = request.POST.getlist('academy[]')
            load = request.POST.getlist('load[]')
            sid = request.POST.getlist('sid[]')
            bus_check = request.POST.get('bus_check')
	    busAlist = request.POST.getlist('alist[]')
            option = request.POST.get('option')
            #redirect
            carnum = int(request.POST.get('carnum'))

            #searchTime,day,area,branch for inventory searching and redirection
            searchTime = request.POST.get('searchTime')
            day = request.POST.get('day')
            area = Area.objects.all()
            branch = Branch.objects.filter(areaid = areaid)
            #carlist for searching with carnum and redirection
            carlist = Car.objects.filter(branchid=bid)
            
            #버스인벤 체크 1 -> 버스인벤 수정, 2 -> 인벤수정
            if bus_check == '1':
                alist = []
                for a in busAlist:
                    alist.append(int(a))
                slist_temp3 = [0]

            else:
                slist_temp = list(set([i for i in sid if i is not None and i != '']))
                slist_temp2 = ','.join(slist_temp)
                slist_temp3 = list(set(slist_temp2.split(',')))
                slist = []

                for s in slist_temp3:
                    slist.append(int(s))

                slist_temp3 = slist
                academy = StudentInfo.objects.filter(id__in = slist_temp3)
                alist = [a.aid_id for a in academy]

            stime = int(time[0].split(':')[0] + time[0].split(':')[1])
            etime = int(time[-1].split(':')[0] + time[-1].split(':')[1])

            academyList = Academy.objects.filter(id__in = alist)
            anamelist_inven = []

            for a in academyList:
                anamelist_inven.append(a.name)

            snum = len(slist_temp3)

            comment = 'carnum: ' + str(carnum) + ', day: ' + str(day) + ', stime: ' + str(stime) + ', week: ' + str(week) + ' update'
            set_audit(comment, 'update', request.user)

            uInven = UpdateInven(bid, carnum, day, req, time,stime, etime, addr, name, name2, load, sid, week, alist, snum, anamelist_inven, slist_temp3)

            if week == 1:
                eInven_index = checkEditedInven(iid, week)                
            
                #update inventory editedinven
                if eInven_index == 0:
                    uInven.update_edited_inven(iid,1)

                    contacts = []
                   
                    contacts = getContacts(bid, day, carnum, week, searchTime)

                    academy = Academy.objects.filter(bid=bid)

                    return render_to_response('supdateSchedule.html',{"area":area,"branch":branch,"searchTime":searchTime,"academy":academy,"day":day,"carlist": carlist,"carnum":carnum,"bid":bid,"areaid": areaid,"week": week,"contacts":contacts,'user':request.user})

                #first update editedinven
                elif eInven_index == 1:
                    inven = Inventory.objects.get(id = iid)

                    ei1 = EditedInven(iid = inven , carnum = carnum, bid = bid, snum = snum, day = day, alist = alist, anamelist= anamelist_inven, slist=slist_temp3, stime = stime, etime = etime, week = week)
                    ei1.save()
                    e1iid = ei1.id

                    ei2 = EditedInven(iid = inven , carnum = carnum, bid = bid, snum = snum, day = day, alist = alist, anamelist= anamelist_inven, slist=slist_temp3, stime = stime, etime = etime, week = 2)
                    ei2.save()
                    e2iid = ei2.id

                    ei3 = EditedInven(iid = inven , carnum = carnum, bid = bid, snum = snum, day = day, alist = alist, anamelist= anamelist_inven, slist=slist_temp3, stime = stime, etime = etime, week = 3)
                    ei3.save()
                    e3iid = ei3.id

                    inven.week1 = 1
                    inven.week2 = 1
                    inven.week3 = 1

                    inven.save()

                    for j in range(3):

                        if j == 0:
                            eiid = e1iid
                        elif j == 1:
                            eiid = e2iid
                        else:
                            eiid = e3iid

                        uInven.create_edited_stable(eiid)
                                                 
                    contacts = []

                    academy = Academy.objects.filter(bid=bid)
                    
                    contacts = getContacts(bid, day, carnum, week, searchTime)                    

                    return render_to_response('supdateSchedule.html',{"area":area,"branch":branch,"searchTime":searchTime,"academy":academy,"day":day,"carlist": carlist,"carnum":carnum,"bid":bid,"areaid": areaid,"week": week,"contacts":contacts,'user':request.user})

            elif week == 2:
                eInven_index = checkEditedInven(iid, week)

                #update inventory editedinven
                if eInven_index == 0:
                    uInven.update_edited_inven(iid,1)

                    contacts = []

                    academy = Academy.objects.filter(bid=bid)

                    contacts = getContacts(bid, day, carnum, week, searchTime)

                    return render_to_response('supdateSchedule.html',{"area":area,"branch":branch,"searchTime":searchTime,"academy":academy,"day":day,"carlist": carlist,"carnum":carnum,"bid":bid,"areaid": areaid,"week": week,"contacts":contacts,'user':request.user})

                #first update editedinven
                elif eInven_index == 1:
                    inven = Inventory.objects.get(id = iid)

                    ei2 = EditedInven(iid = inven , carnum = carnum, bid = bid, snum = snum, day = day, alist = alist, anamelist= anamelist_inven, slist=slist_temp3, stime = stime, etime = etime, week = 2)
                    ei2.save()
                    e2iid = ei2.id

                    ei3 = EditedInven(iid = inven , carnum = carnum, bid = bid, snum = snum, day = day, alist = alist, anamelist= anamelist_inven, slist=slist_temp3, stime = stime, etime = etime, week = 3)
                    ei3.save()
                    e3iid = ei3.id

                    inven.week2 = 1
                    inven.week3 = 1

                    inven.save()

                    for j in range(2):

                        if j == 0:
                            eiid = e2iid
                        elif j == 1:
                            eiid = e3iid

                        uInven.create_edited_stable(eiid)
 
                    contacts = []

                    academy = Academy.objects.filter(bid=bid)
                    
                    contacts = getContacts(bid, day, carnum, week, searchTime)
                    
                    return render_to_response('supdateSchedule.html',{"area":area,"branch":branch,"searchTime":searchTime,"academy":academy,"day":day,"carlist": carlist,"carnum":carnum,"bid":bid,"areaid": areaid,"week": week,"contacts":contacts,'user':request.user})

            elif week == 3:

                eInven_index = checkEditedInven(iid, week)

                #update inventory editedinven
                if eInven_index == 0:
                    uInven.update_edited_inven(iid,1)

                    contacts = []

                    academy = Academy.objects.filter(bid=bid)
 
                    contacts = getContacts(bid, day, carnum, week, searchTime)

                    return render_to_response('supdateSchedule.html',{"area":area,"branch":branch,"searchTime":searchTime,"academy":academy,"day":day,"carlist": carlist,"carnum":carnum,"bid":bid,"areaid": areaid,"week": week,"contacts":contacts,'user':request.user})

                #first update editedinven
                elif eInven_index == 1:
                    inven = Inventory.objects.get(id = iid)

                    ei = EditedInven(iid = inven , carnum = carnum, bid = bid, snum = snum, day = day, alist = alist, anamelist= anamelist_inven, slist=slist_temp3, stime = stime, etime = etime, week = week)
                    ei.save()
                    eiid = ei.id

                    inven.week3 = 1
                    inven.save()

		    uInven.create_edited_stable(eiid)
                    contacts = []

                    academy = Academy.objects.filter(bid=bid)
                    contacts = getContacts(bid, day, carnum, week, searchTime)

                    return render_to_response('supdateSchedule.html',{"area":area,"branch":branch,"searchTime":searchTime,"academy":academy,"day":day,"carlist": carlist,"carnum":carnum,"bid":bid,"areaid": areaid,"week": week,"contacts":contacts,'user':request.user})

            #week0 update
            else:
                inven = Inventory.objects.get(id=iid)
                inven.snum = snum 
                inven.alist=alist 
                inven.anamelist = anamelist_inven 
                inven.slist=slist_temp3 
                inven.stime = stime 
                inven.etime = etime 
                inven.carnum = carnum
                inven.save()

                if option == '1':
 
                    unloadSidList = getUnloadSid(iid)
                    
                    #delete stable before updateing stable
                    delete_stable = ScheduleTable.objects.filter(iid_id=iid)
                    delete_stable.delete()

                    uInven.update_inven(iid, unloadSidList)  

                    if inven.week1 == 1 or inven.week2 == 1 or inven.week3 == 1:
                         
                        uInven.update_edited_inven(iid, 0)

                    else:
		        if not alist:
		            alist = 0
			    cInven = CreateInven(bid, carnum, day,req, time, addr, name, name2, load, sid, week, alist)
		        if alist != None:
			    cInven = CreateInven(bid, carnum, day, req, time, addr, name, name2, load, sid, week, alist)
		        
                        if cInven.setAlist == 1:
		            return HttpResponse('error setAlist')
		        if cInven.setSlist() == 1:
			    return HttpResponse('error setSlist')
		        if cInven.setANameList() == 1:
			    return HttpResponse('error setANameList')
		        if cInven.setSEtime() == 1:
			    return HttpResponse('error setSEtime')
		        
                        cInven.setWeek1(unloadSidList, iid)     
                elif option == '0':
                    Inventory.objects.filter(id=iid).update(snum = snum, alist=alist, anamelist = anamelist_inven, slist=slist_temp3, stime = stime, etime = etime, carnum = carnum)

		    unloadSidList = getUnloadSid(iid)

                    #delete stable before updateing stable
                    delete_stable = ScheduleTable.objects.filter(iid_id=iid)
                    delete_stable.delete()
       
                    uInven.update_inven(iid, unloadSidList) 
                            
                if searchTime == '':
                    invens = Inventory.objects.filter(bid = bid).filter(day = day).filter(carnum = carnum)

                else:
                    invens = Inventory.objects.filter(bid = bid).filter(day = day).filter(etime__gte = int(searchTime)-90, stime__lte = int(searchTime)+90).filter(carnum = carnum)

                contacts = []

                for i in invens:
                    contacts.extend(Inventory.objects.filter(id = i.id).prefetch_related('scheduletables'))

                academy = Academy.objects.filter(bid=bid)

                return render_to_response('supdateSchedule.html',{"area":area,"branch":branch,"searchTime":searchTime,"academy":academy,"day":day,"carlist": carlist,"carnum":carnum,"bid":bid,"areaid": areaid,"week": week,"contacts":contacts,'user':request.user})

        #update -> 0 delete inventory, stable
        elif update == '0':
            iid = request.POST.get('iid')
            bid = request.POST.get('bid')
            #searchTime,day,area,branch for inventory searching and redirection
            searchTime = request.POST.get('searchTime')
            day = request.POST.get('day')
            time = request.POST.get('time')
            week = int(request.POST.get('week'))
            areaid = int(request.POST.get('areaid'))
            area = Area.objects.all()
            branch = Branch.objects.filter(id = bid)
            #carlist for searching with carnum and redirection
            carlist = Car.objects.filter(branchid=bid)
            #for redirection
            carnum = request.POST.get('carnum')
           
            if week == 0:
                a_inven = Inventory.objects.get(id = iid)
                comment = 'carnum: ' + str(carnum) + ', day: ' + str(day) + ', stime: ' + str(a_inven.stime) + ', week: ' + str(week) + ' delete'
                set_audit(comment, 'delete' , request.user)
            else:
                a_inven = EditedInven.objects.get(id = iid)
                comment = 'carnum: ' + str(carnum) + ', day: ' + str(day) + ', stime: ' + str(a_inven.stime) + ', week: ' + str(week) + ' delete'
                set_audit(comment, 'delete' , request.user)

            if week > 0:
                try:
                    estable = EditedScheduleTable.objects.filter(ieid_id = iid)
                    estable.delete()
                except:
                    return HttpResponse("inven delete error:estable")

                try:
                    inven = EditedInven.objects.get(id = iid)
                    inven.delete()
                except:
                    return HttpResponse("inven delete error:Editedinventory")

            else:
                try:
                    stable  = ScheduleTable.objects.filter(iid_id = iid)
                    stable.delete()

                except:
                    return HttpResponse("inven delete error:stable")

		# reload after deleting
		try:
                	inven = Inventory.objects.get(id = iid)
                	inven.delete()
		except:
			pass

            contacts = []
           
            contacts = getContacts(bid, day, carnum, week, searchTime)

            #redirect
            academy = Academy.objects.filter(bid=bid)

            return render_to_response('supdateSchedule.html',{"area":area,"branch":branch,"searchTime":searchTime,"academy":academy,"day":day,"carlist": carlist,"carnum": int(carnum),"bid":bid,"areaid": areaid,"week": week,"contacts":contacts,'user':request.user})


@csrf_exempt
def acaUpdateSchedule(request):
    if request.method == "GET":
        searchInven = request.GET.get('searchinven')
        area = Area.objects.all()

        if searchInven == '1':
            day = request.GET.get('day')
            searchTime = request.GET.get('searchTime')
            areaid = int(request.GET.get('areaid'))
            bid = int(request.GET.get('bid'))
            aid = int(request.GET.get('aca'))
            week = request.GET.get('week')
            

            academy = Academy.objects.filter(bid=bid)
            branch = Branch.objects.filter(areaid = areaid)

            if week == None:
                week = 0

            week = int(week)

            contacts = []
            
            #fake
            carnum = -1
            contacts = getContacts(bid, day, carnum , week, searchTime, aid)

            carlist = Car.objects.filter(branchid=bid)

            return render_to_response('acaUpdateSchedule.html',{"area":area,"searchTime":searchTime,"week":week,"day":day,"carlist":carlist, "branch":branch,"academy":academy,"areaid": areaid,"aid":aid,"bid":bid, "contacts":contacts,'user':request.user})

        return render_to_response('acaUpdateSchedule.html',{'area':area,'user':request.user})

    elif request.method == "POST":
        area = Area.objects.all()
        #updateflag 1(select branch),2(search inven)
        updateflag = request.POST.get('updateflag')
        #update 1(update inven,stable),0(delete inven,stable)
        update = request.POST.get('update')
        areaid = request.POST.get('areaid')

        if request.POST.get('acaSelected') == '1':
            bid = request.POST.get('branch')
            aca = Academy.objects.filter(bid = bid)

            data = serialize('json', aca)

            return HttpResponse(data, content_type="application/json" )

        #updateflag == 1: selects area for getting branch
        if updateflag == '1':
            areaid = request.POST.get('area')
            branch = Branch.objects.filter(areaid = areaid)
            data = serialize('json', branch)

            return HttpResponse(data, content_type="application/json" )

        #update -> 1 : update inven
        if update == '1':
            iid = request.POST.get('iid')
            week = int(request.POST.get('week'))
            time = request.POST.getlist('time[]')
            addr = request.POST.getlist('addr[]')
            req = request.POST.getlist('req[]')
            name = request.POST.getlist('name[]')
            name2 = request.POST.getlist('name[]')
            load = request.POST.getlist('load[]')
            sid = request.POST.getlist('sid[]')
            aid = int(request.POST.get('aca'))
            raid = int(request.POST.get('aca'))
            areaid = int(request.POST.get('areaid'))
            bid = int(request.POST.get('bid'))
            carnum = request.POST.get('carnum')
            carlist = Car.objects.filter(branchid=bid)
            alist = request.POST.getlist('alist[]')
            option = request.POST.get('option')

            #searchTime,day,area,branch for inventory searching and redirection
            searchTime = request.POST.get('searchTime')
            day = request.POST.get('day')
            area = Area.objects.all()
            branch = Branch.objects.filter(id = bid)

            slist_temp = list(set([i for i in sid if i is not None and i != '']))
            slist_temp2 = ','.join(slist_temp)
            slist_temp3 = list(set(slist_temp2.split(',')))
            slist = []

            for s in slist_temp3:
                slist.append(int(s))

            slist_temp3 = slist
            academy = StudentInfo.objects.filter(id__in = slist_temp3)
            alist = [a.aid_id for a in academy]

            stime = int(time[0].split(':')[0] + time[0].split(':')[1])
            etime = int(time[-1].split(':')[0] + time[-1].split(':')[1])

            academyList = Academy.objects.filter(id__in = alist)
            anamelist_inven = []

            for a in academyList:
                anamelist_inven.append(a.name)

            snum = len(slist_temp3)

            comment = 'carnum: ' + str(carnum) + ', day: ' + str(day) +', stime: '+ str(time[0])+ ', week: ' + str(week) + ' update'
            set_audit(comment, 'update', request.user)

            uInven = UpdateInven(bid, carnum, day, req, time,stime, etime, addr, name, name2, load, sid, week, alist, snum, anamelist_inven, slist_temp3)

            if week == 1:
                eInven_index = checkEditedInven(iid, week)

                #update inventory editedinven
                if eInven_index == 0:
                    uInven.update_edited_inven(iid, 1)

                    contacts = []

                    academy = Academy.objects.filter(bid=bid)
                    contacts = getContacts(bid, day, carnum, week, searchTime,aid)

                    return render_to_response('acaUpdateSchedule.html',{"area":area,"branch":branch,"searchTime":searchTime,"carlist":carlist, "academy":academy,"day":day,"carnum":carnum,"aid":raid,"bid":bid,"areaid": areaid,"week": week,"contacts":contacts,'user':request.user})


				#first update editedinven
                elif eInven_index == 1:
                    inven = Inventory.objects.get(id = iid)

                    ei1 = EditedInven(iid = inven , carnum = carnum, bid = bid, snum = snum, day = day, alist = alist, anamelist= anamelist_inven, slist=slist_temp3, stime = stime, etime = etime, week = week)
                    ei1.save()
                    e1iid = ei1.id

                    ei2 = EditedInven(iid = inven , carnum = carnum, bid = bid, snum = snum, day = day, alist = alist, anamelist= anamelist_inven, slist=slist_temp3, stime = stime, etime = etime, week = 2)
                    ei2.save()
                    e2iid = ei2.id

                    ei3 = EditedInven(iid = inven , carnum = carnum, bid = bid, snum = snum, day = day, alist = alist, anamelist= anamelist_inven, slist=slist_temp3, stime = stime, etime = etime, week = 3)
                    ei3.save()
                    e3iid = ei3.id

                    inven.week1 = 1
                    inven.week2 = 1
                    inven.week3 = 1

                    inven.save()

                    for j in range(3):

                        if j == 0:
                            eiid = e1iid
                        elif j == 1:
                            eiid = e2iid
                        else:
                            eiid = e3iid

                        uInven.create_edited_stable(eiid)

                    contacts = []

                    academy = Academy.objects.filter(bid=bid)
                    contacts = getContacts(bid, day, carnum, week, searchTime, aid) 

                    return render_to_response('acaUpdateSchedule.html',{"area":area,"branch":branch,"searchTime":searchTime,"carlist":carlist,"academy":academy,"day":day,"carnum":carnum,"aid":raid,"bid":bid,"areaid": areaid,"week": week,"contacts":contacts,'user':request.user})

            elif week == 2:
                eInven_index = checkEditedInven(iid, week)

                #update inventory editedinven
                if eInven_index == 0:
                    uInven.update_edited_inven(iid,1)

                    contacts = []

                    contacts = getContacts(bid, day, carnum, week, searchTime, aid)

                    academy = Academy.objects.filter(bid=bid)

                    return render_to_response('acaUpdateSchedule.html',{"area":area,"branch":branch,"searchTime":searchTime,"carlist":carlist,"academy":academy,"day":day,"carnum":carnum,"aid":raid,"bid":bid,"areaid": areaid,"week": week,"contacts":contacts,'user':request.user})


				#first update editedinven
                elif eInven_index == 1:
                    inven = Inventory.objects.get(id = iid)

                    ei2 = EditedInven(iid = inven , carnum = carnum, bid = bid, snum = snum, day = day, alist = alist, anamelist= anamelist_inven, slist=slist_temp3, stime = stime, etime = etime, week = 2)
                    ei2.save()
                    e2iid = ei2.id

                    ei3 = EditedInven(iid = inven , carnum = carnum, bid = bid, snum = snum, day = day, alist = alist, anamelist= anamelist_inven, slist=slist_temp3, stime = stime, etime = etime, week = 3)
                    ei3.save()
                    e3iid = ei3.id

                    inven.week2 = 1
                    inven.week3 = 1

                    inven.save()

                    for j in range(2):

                        if j == 0:
                            eiid = e2iid
                        else:
                            eiid = e3iid

                        uInven.create_edited_stable(eiid)

                    contacts = []

                    contacts = getContacts(bid, day, carnum, week, searchTime, aid)

                    academy = Academy.objects.filter(bid=bid)
                    contacts = sorted(contacts, key=lambda x: x.stime,reverse=False)

                    return render_to_response('acaUpdateSchedule.html',{"area":area,"branch":branch,"searchTime":searchTime,"carlist":carlist,"academy":academy,"day":day,"carnum":carnum,"aid":raid,"bid":bid,"areaid": areaid,"week": week,"contacts":contacts,'user':request.user})


            elif week == 3:
                eInven_index = checkEditedInven(iid, week)

                #update inventory editedinven
                if eInven_index == 0:
                    uInven.update_edited_inven(iid,1)

                    contacts = []

                    contacts = getContacts(bid, day, carnum, week, searchTime, aid)

                    academy = Academy.objects.filter(bid=bid)

                    return render_to_response('acaUpdateSchedule.html',{"area":area,"branch":branch,"searchTime":searchTime,"carlist":carlist,"academy":academy,"day":day,"carnum":carnum,"aid":raid,"bid":bid,"areaid": areaid,"week": week,"contacts":contacts,'user':request.user})


	        #first update editedinven
                elif eInven_index == 1:
                    inven = Inventory.objects.get(id = iid)

                    ei3 = EditedInven(iid = inven , carnum = carnum, bid = bid, snum = snum, day = day, alist = alist, anamelist= anamelist_inven, slist=slist_temp3, stime = stime, etime = etime, week = 3)
                    ei3.save()
                    e3iid = ei3.id
                    
                    inven.week3 = 1
                    inven.save()
                   
                    uInven.create_edited_stable(e3iid) 

                    contacts = []
                    
                    contacts = getContacts(bid, day, carnum, week, searchTime, aid)

                    academy = Academy.objects.filter(bid=bid)

                    return render_to_response('acaUpdateSchedule.html',{"area":area,"branch":branch,"searchTime":searchTime,"carlist":carlist,"academy":academy,"day":day,"carnum":carnum,"aid":raid,"bid":bid,"areaid": areaid,"week": week,"contacts":contacts,'user':request.user})
            
            else:
                inven = Inventory.objects.get(id=iid)
                inven.snum = snum 
                inven.alist=alist 
                inven.anamelist = anamelist_inven 
                inven.slist=slist_temp3 
                inven.stime = stime 
                inven.etime = etime 
                inven.carnum = carnum
                inven.save()

                if option == '1':

                    unloadSidList = getUnloadSid(iid)

                    #delete stable before updateing stable
                    delete_stable = ScheduleTable.objects.filter(iid_id=iid)
                    delete_stable.delete()

                    uInven.update_inven(iid, unloadSidList)

                    if inven.week1 == 1 or inven.week2 == 1 or inven.week3 == 1:

                        uInven.update_edited_inven(iid, 0)
                    
                    else:
                        if not alist:
                            alist = 0
			    cInven = CreateInven(bid, carnum, day,req, time, addr, name, name2, load, sid, week, alist)
		        if alist != None:
			    cInven = CreateInven(bid, carnum, day, req, time, addr, name, name2, load, sid, week, alist)
		        
                        if cInven.setAlist == 1:
		            return HttpResponse('error setAlist')
		        if cInven.setSlist() == 1:
			    return HttpResponse('error setSlist')
		        if cInven.setANameList() == 1:
			    return HttpResponse('error setANameList')
		        if cInven.setSEtime() == 1:
			    return HttpResponse('error setSEtime')
		        
                        cInven.setWeek1(unloadSidList, iid) 
                
                elif option == '0':
                    Inventory.objects.filter(id=iid).update(snum = snum, alist=alist, anamelist = anamelist_inven, slist=slist_temp3, stime = stime, etime = etime, carnum = carnum)

		    unloadSidList = getUnloadSid(iid)

                    #delete stable before updateing stable
                    delete_stable = ScheduleTable.objects.filter(iid_id=iid)
                    delete_stable.delete()
                   
                    uInven.update_inven(iid, unloadSidList)
                
                #redirect
                area = Area.objects.all()
                academy = Academy.objects.filter(bid=bid)

                contacts = []

                contacts = getContacts(bid, day, carnum, week, searchTime, aid)

                return render_to_response('acaUpdateSchedule.html',{"area":area,"searchTime":searchTime,"week":week,"day":day,"carlist":carlist,"branch":branch,"academy":academy,"areaid": areaid,"aid":raid,"bid":bid, "contacts":contacts,'user':request.user})

        #update -> 0 delete inventory, stable
        elif update == '0':
            iid = request.POST.get('iid')
            bid = request.POST.get('bid')
            #searchTime,day,area,branch for inventory searching and redirection
            searchTime = request.POST.get('searchTime')
            day = request.POST.get('day')
            time = request.POST.get('time')
            week = int(request.POST.get('week'))
            areaid = int(request.POST.get('areaid'))
            aid = int(request.POST.get('aca'))
            raid = int(request.POST.get('aca'))
            area = Area.objects.all()
            branch = Branch.objects.filter(id = bid)
            #carlist for searching with carnum and redirection
            carlist = Car.objects.filter(branchid=bid)
            #for redirection
            carnum = request.POST.get('carnum')

            if week == 0: 
                a_inven = Inventory.objects.get(id = iid)
                comment = 'carnum: ' + str(carnum) + ', day: ' + str(day) + ', stime: ' + str(a_inven.stime) + ', week: ' + str(week) + ' delete'
                set_audit(comment, 'delete' , request.user)
            else:
                a_inven = EditedInven.objects.get(id = iid)
                comment = 'carnum: ' + str(carnum) + ', day: ' + str(day) + ', stime: ' + str(a_inven.stime) + ', week: ' + str(week) + ' delete'
                set_audit(comment, 'delete' , request.user)

            if week > 0:
                try:
                    estable = EditedScheduleTable.objects.filter(ieid_id = iid)
                    estable.delete()
                except:
                    return HttpResponse("inven delete error:estable")

                try:
                    inven = EditedInven.objects.get(id = iid)
                    inven.delete()
                except:
                    return HttpResponse("inven delete error:Editedinventory")

            else:
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

            contacts = []

            contacts = getContacts(bid, day, carnum, week, searchTime, aid) 

            academy = Academy.objects.filter(bid=bid)

            return render_to_response('acaUpdateSchedule.html',{"area":area,"searchTime":searchTime,"carlist":carlist,"week":week,"day":day,"branch":branch,"academy":academy,"areaid": areaid,"aid":raid,"bid":bid, "contacts":contacts,'user':request.user})

@csrf_exempt
def studentLoad(request):
    if request.method == "POST":

        aid = request.POST.get('aid')
        stu = StudentInfo.objects.filter(aid = aid).order_by('sname')

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

    return render_to_response('getHistory.html', {"history": history, "academy": allacademy, "aid" : aid, 'aname': aname, 'total_count': total_count, 'uniq_count': uniq_count, 'startdate': startdate, 'enddate': enddate, 'user':request.user})


## HH:MM ==> HHMM
def convertDateFormat(str):
	ret = str.replace(':', '')
	#ret.replace(':', '')
	return int(ret)


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
        memo = request.POST.get('memo')
        flag = request.POST.get('flag')

        if flag == '0':
            inven = Inventory.objects.get(id=iid)
            inven.req = req
            inven.memo = memo
            inven.save()

        elif flag == '1':
            eInven = EditedInven.objects.get(id = iid)
            eInven.req = req
            eInven.memo = memo
            eInven.save()

        return HttpResponse(req)

def setRealtimeLocation(request):
    if request.method == "GET":
        carnum = request.GET.get('carnum')
        schedule_time = request.GET.get('schedule_time')
        t = timeToDate()
        today = t.timeToYmd()
        current_time = t.timeToHMS()

        RealtimeLocation.objects.create(carnum=carnum, schedule_time=schedule_time, date=today, departure_time=current_time)

        return HttpResponse("success")

## time format : HH:MM
def get_difference(time1, time2):
    timevar1 = time1.split(':')
    timevar2 = time2.split(':')

    return int(timevar2[0]) * 60 + int(timevar2[1]) - (int(timevar1[0]) * 60 + int(timevar1[1]))

def format_hm(time):
    return (time[:2] + ':' + time[2:])

def getRealtimeLocation(request):
    if request.method == "GET":
        t = timeToDate()
        d = t.timeToD()
        today = t.timeToYmd()
        rawhm = t.timeToRawHM()
        hm = t.timeToHM()
        #rawhm = int(request.GET.get('rawhm'))
        hm = request.GET.get('hm')
        sid = request.GET.get('sid')
        sname = request.GET.get('sname')
        carnum = -1
        iid = ""
        siid = ""
        #expected_time = "00:00"

        #if (sid and len(sid) > 0):
            #sids = StudentInfo.objects.get(id = sid)
            #if (len(sids) <= 0):
                #return HttpResponse("해당 사용자가 존재하지 않습니다.")
        #else:
            #return HttpResponse("파라미터가 유효하지 않습니다.")


        today_inventories = Inventory.objects.filter(day=d)
        today_inventory_ids = today_inventories.values('id')
        scheduletables = ScheduleTable.objects.filter(iid_id__in = today_inventory_ids).filter(slist__contains = [sid]).order_by('-time')
        if (len(scheduletables) <= 0):
            return HttpResponse("해당 사용자는 오늘 스케쥴이 없습니다.")

        ## 마지막 스케쥴도 지났으면 (desc order 인 것 주의)
        if (Inventory.objects.get(id = scheduletables.first().iid_id).etime < rawhm):
            return HttpResponse("오늘 운행 스케쥴이 종료되었습니다.")

        for scheduletable in scheduletables:
            inventory = Inventory.objects.get(id = scheduletable.iid_id)
            format_etime = format_hm(str(inventory.etime))
            if (inventory.etime > rawhm):
                ## inventory 중간에 있으면..
                if (inventory.stime < rawhm):
                    carnum = inventory.carnum
                    expected_time = scheduletable.time
                    realtimelocation = RealtimeLocation.objects.filter(date=today, carnum=carnum, departure_time__lte=format_etime).order_by('schedule_time').last()
                    waittime = get_difference(hm, expected_time) + get_difference(realtimelocation.schedule_time, realtimelocation.departure_time) - 1
                    return HttpResponse(str(waittime) + "분 후 도착합니다.")
                ## 다음 inventory 로..
                else:
                    continue
            ## inventory 사이에..
            else:
                return HttpResponse("다음 스케쥴이 아직 시작되지 않았습니다.")
@csrf_exempt
def moveCarInven(request):
    if request.method == 'POST':
        iid = request.POST.get('iid')
        carname = request.POST.get('carname')
        Inventory.objects.filter(id = iid).update(carnum = carname)

    return HttpResponse(carname)

@csrf_exempt
def moveCarEditedInven(request):
    if request.method == "POST":
        iid = request.POST.get('iid')
        carname = request.POST.get('carname')

        EditedInven.objects.filter(id = iid).update(carnum = carname)

    return HttpResponse(carname)

@csrf_exempt
def busAcademy(request):
    if request.method == "POST":
        alist = request.POST.getlist('alist[]')
        iid = request.POST.get('iid')
        anamelist = []

        for a in alist:
            academy = Academy.objects.get(id = a)
            anamelist.append(academy.name)

        Inventory.objects.filter(id = iid).update(alist = alist, anamelist = anamelist)

        return HttpResponse(0)
