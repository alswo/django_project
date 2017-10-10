#-*- coding:utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core import serializers
from passenger.models import Profile, StudentInfo
from schedule.models import Inventory, ScheduleTable
import datetime
from collections import defaultdict
from django.views.decorators.csrf import csrf_exempt
import json

def is_not_drivermanager(user):
    if user:
        return (user.groups.filter(name='drivermanager').exists() == False)
    
    return True

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
    bid = Profile.objects.get(user_id=request.user).bid

    if request.method == 'GET':

        return render_to_response('daySchedule.html', {"weekdaylist":weekdaylist,"user":request.user})

    else:
        day = request.POST.get('day')
        
        if day:
            contacts = day_schedule(bid, day)
        else:
            pass 
        return HttpResponse(json.dumps(contacts))


