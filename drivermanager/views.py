#-*- coding:utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core import serializers
from passenger.models import Profile, StudentInfo
from schedule.models import Inventory, ScheduleTable, Branch, Area, Car
import datetime
from collections import defaultdict
from django.views.decorators.csrf import csrf_exempt
import json

def is_not_drivermanager(user):
    if user:
        return (user.groups.filter(name='drivermanager').exists() == True)
    
    return False

def day_schedule(bid, day):

    invens = Inventory.objects.filter(bid = bid).filter(day = day)
   
    temp_car = []

    for inven in invens:
        temp_car.append(inven.carnum)
    
    temp_car = set(temp_car)

    contacts = []
    for tc in temp_car:
        temp_dict = {}
        temp_dict['carnum'] = tc
        
        temp_inven_list = []
        for inven in invens:
            temp_invens = {}
            if inven.carnum == tc:
                temp_invens['stime'] = inven.stime
		temp_invens['etime'] = inven.etime
                temp_invens['snum'] = inven.snum
                temp_invens['iid'] = inven.id
                temp_invens['aname'] = inven.anamelist
                temp_invens['day'] = inven.day
                
                for studentInfo in inven.slist:
                    try:
                        sInfo = StudentInfo.objects.get(id = studentInfo)
                    except StudentInfo.DoesNotExist:
                        continue
                    if sInfo.birth_year == None or ((datetime.datetime.now().year - int(sInfo.birth_year) + 1) <= 13):
                        temp_invens['passenger'] = 0
                        break

                temp_inven_list.append(temp_invens)
                

        temp_dict['invens'] = temp_inven_list
        
        contacts.append(temp_dict)

    return contacts

def car_schedule(car):
   
    temp_day = ['월','화','수','목','금','토']

    contacts = []
    for tc in temp_day:
        invens = Inventory.objects.filter(carnum = car).filter(day=tc)
        temp_dict = {}
        temp_dict['day'] = tc
        
        temp_inven_list = []
        for inven in invens:
            temp_invens = {}
            temp_invens['carnum'] = inven.carnum
            temp_invens['day'] = inven.day
            temp_invens['stime'] = inven.stime
            temp_invens['etime'] = inven.etime
            temp_invens['snum'] = inven.snum
            temp_invens['iid'] = inven.id
            temp_invens['aname'] = inven.anamelist
                
            for studentInfo in inven.slist:
                try:
                    sInfo = StudentInfo.objects.get(id = studentInfo)
                except StudentInfo.DoesNotExist:
                    continue
                if sInfo.birth_year == None or ((datetime.datetime.now().year - int(sInfo.birth_year) + 1) <= 13):
                    temp_invens['passenger'] = 0
                    break

            temp_inven_list.append(temp_invens)
                

        temp_dict['invens'] = temp_inven_list
        
        contacts.append(temp_dict)

    return contacts  
    
@login_required
@user_passes_test(is_not_drivermanager, login_url='/', redirect_field_name=None)
def get_drivermanager_page(request):
    if request.method == 'GET':
        bid = Profile.objects.get(user = request.user).bid
        
        return render_to_response('getDmPage.html')

@login_required
@user_passes_test(is_not_drivermanager, login_url='/', redirect_field_name=None)
@csrf_exempt
def get_schedule(request):
    weekdaylist = ['월', '화', '수', '목', '금', '토']

    if request.method == 'GET':
        if request.user.is_superuser:
            if request.GET.get('bid'):
                bid = int(request.GET.get('bid'))
                
            else:
                bid = 1

            branch = Branch.objects.all()
        
        else: 
            areaid = Profile.objects.get(user_id = request.user).bid
            branch = Branch.objects.filter(areaid = areaid)  

            if request.GET.get('bid'):
                bid = int(request.GET.get('bid'))
            else:
                bid = branch[0].id    

        return render_to_response('daySchedule.html', {"weekdaylist":weekdaylist,"branch": branch,"bid":bid, "user":request.user})

    else:
        day = request.POST.get('day')
        if request.POST.get('bid'):
            bid = request.POST.get('bid')
        else:
            bid = Profile.objects.get(user_id = request.user).bid    
    
        if day:
            contacts = day_schedule(bid, day)
        else:
            pass 
        return HttpResponse(json.dumps(contacts))

@login_required
@user_passes_test(is_not_drivermanager, login_url='/', redirect_field_name=None)
@csrf_exempt
def get_car_schedule(request):
    weekdaylist = ['월', '화', '수', '목', '금', '토']

    if request.method == 'GET':
        if request.user.is_superuser:
            if request.GET.get('aid'):
                aid = int(request.GET.get('aid'))
            else:
                aid = -1

            if request.GET.get('bid'):
                bid = int(request.GET.get('bid'))
            else:
                bid = -1

            if request.GET.get('car'):
                car = int(request.GET.get('car'))
            else:
                car = -1

            area = Area.objects.all() 
            if aid > 0:
                if bid > 0:
                    branch = Branch.objects.filter(areaid=aid)
                    car = Car.objects.filter(branchid=bid)

                    return render_to_response('carSchedule.html', {'area':area, 'branch':branch,'car':car, 'aid':aid, 'bid':bid, 'user':request.user}) 
                
                else:
                    branch = Branch.objects.filter(areaid=aid)

                    return render_to_response('carSchedule.html', {'area':area, 'branch':branch, 'aid':aid, 'user':request.user})    

            else:
                return render_to_response('carSchedule.html', {'area':area, 'user':request.user})            
 
        else:
            areaid = Profile.objects.get(user_id = request.user).bid 
            branch = Branch.objects.filter(areaid = areaid)

            if request.GET.get('bid'):
                bid = int(request.GET.get('bid'))
            else:
                bid = -1

            if bid > 0:
                car = Car.objects.filter(branchid=bid)

                return render_to_response('carSchedule.html', {'branch':branch,'car':car, 'bid':bid, 'user':request.user})

            return render_to_response('carSchedule.html', {'branch':branch, 'user':request.user})

        return render_to_response('carSchedule.html', {'user':request.user})  

    if request.method == "POST":
        car = int(request.POST.get('car'))
        
        contacts = car_schedule(car)

        return HttpResponse(json.dumps(contacts)) 


