#-*- coding:utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core import serializers
from passenger.models import Profile, StudentInfo
from schedule.models import Inventory, ScheduleTable, Branch, Area, Car
from institute.models import BillingHistorySetting
from drivermanager.models import Salary
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
   
def get_sales_status(car):
    invens = Inventory.objects.filter(carnum = car)
    thisyear = str(datetime.datetime.now())[:4]
    month = []

    for i in range(1,13):
        if i < 10:
            month.append(thisyear + "-0" + str(i))
        else:
            month.append(thisyear + "-" + str(i))
    contacts = []
    for m in month:
        inventory_option = []
        temp_sales = {}
        sales_count = 0
        bhs = BillingHistorySetting.objects.filter(monthpick = m)
        for b in bhs:
            inventory_option = b.setting['data'].values()
            for io in inventory_option:
                for i in invens:
                    temp_value = io.values()[0]
                    if i.id == int(io.keys()[0]):
                        if 8 in temp_value:
                            sales_count += 0
                        elif 1 in temp_value:
                            if 2 in temp_value:
                                if 4 in temp_value:
                                    sales_count = 22000
                                else:
                                    sales_count += 12500
                            else:
                                if 4 in temp_value:
                                    sales_count += 22000
                                else:
                                    sales_count += 11000           
                        else:
                            if 2 in temp_value:
                                if 4 in temp_value:
                                    sales_count += 15000
                                else:
                                    sales_count += 9000
                            else:
                                if 4 in temp_value:
                                    sales_count += 15000
                                else:
                                    sales_count += 7500
        temp_sales['month'] = m
        temp_sales['car'] = car                      
        temp_sales['sales'] = sales_count
            
        contacts.append(temp_sales) 

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
            areaid = Profile.objects.get(user_id = request.user).areaid
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
            areaid = Profile.objects.get(user_id = request.user).areaid    
            branch = Branch.objects.filter(areaid_id = areaid)
            bid = branch[0].id

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
            areaid = Profile.objects.get(user_id = request.user).areaid 
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
@login_required
@user_passes_test(is_not_drivermanager, login_url='/', redirect_field_name=None)
@csrf_exempt
def car_sales_status(request):
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

            area = Area.objects.all()
            if aid > 0:
                if bid > 0:
                    branch = Branch.objects.filter(areaid=aid)
                    car = Car.objects.filter(branchid_id = bid)

                    return render_to_response('salesStatus.html', {'area':area, 'branch':branch, 'car' : car, 'aid':aid, 'bid':bid, 'user':request.user})

                else:
                    branch = Branch.objects.filter(areaid=aid)

                    return render_to_response('salesStatus.html', {'area':area, 'branch':branch, 'aid':aid, 'user':request.user})

            else:
                return render_to_response('salesStatus.html', {'area':area, 'user':request.user})
        else:
            areaid = Profile.objects.get(user_id = request.user).areaid
            branch = Branch.objects.filter(areaid = areaid)

            if request.GET.get('bid'):
                bid = int(request.GET.get('bid'))
            else:
                bid = -1

            if request.GET.get('cid'):
                cid = int(request.GET.get('cid'))
            else:
                cid = -1

            if bid > 0:
                if cid > 0:
                    car = Car.objects.filter(branchid=bid)

                    return render_to_response('salesStatus.html', {'branch':branch,'car':car, 'bid':bid, 'cid': cid, 'user':request.user})
                else:
                    car = Car.objects.filter(branchid=bid)

                    return render_to_response('salesStatus.html', {'branch':branch,'car':car, 'bid':bid, 'user':request.user}) 
            
            return render_to_response('salesStatus.html', {'branch':branch, 'user':request.user})

    else:
        flag = request.POST.get('flag') 

        if flag == "car":
            car = request.POST.get('car')
            contacts = get_sales_status(car)

            return HttpResponse(json.dumps(contacts))



@login_required
@user_passes_test(is_not_drivermanager, login_url='/', redirect_field_name=None)
@csrf_exempt
def salary_management(request):
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
            
            if request.GET.get('cid'):
                cid = int(request.GET.get('cid'))
            else:
                cid = -1

            area = Area.objects.all()
            if aid > 0:
                if bid > 0:
                    if cid > 0:
                        branch = Branch.objects.filter(areaid=aid)
                        car = Car.objects.filter(branchid_id = bid)
                        salary = Salary.objects.filter(carnum_id = cid).order_by('-payment_date')

                        return render_to_response('salaryManagement.html', {'area':area,'branch':branch,'salary':salary,'car':car,'aid':aid,'bid':bid,'cid':cid,'user':request.user})

                    else:
                        branch = Branch.objects.filter(areaid=aid)
                        car = Car.objects.filter(branchid_id = bid)

                        return render_to_response('salaryManagement.html', {'area':area, 'branch':branch, 'car' : car, 'aid':aid, 'bid':bid, 'user':request.user})

                else:
                    branch = Branch.objects.filter(areaid=aid)                

                    return render_to_response('salaryManagement.html', {'area':area, 'branch':branch, 'aid':aid, 'user':request.user})
    
            else:
                return render_to_response('salaryManagement.html', {'area':area, 'user':request.user})
        else:
            areaid = Profile.objects.get(user_id = request.user).areaid
            branch = Branch.objects.filter(areaid = areaid)

            if request.GET.get('bid'):
                bid = int(request.GET.get('bid'))
            else:
                bid = -1

            if request.GET.get('cid'):
                cid = int(request.GET.get('cid'))
            else:
                cid = -1

            if bid > 0:
                if cid > 0:
                    car = Car.objects.filter(branchid=bid)
                    salary = Salary.objects.filter(carnum_id = cid).order_by('-payment_date')

                    return render_to_response('salaryManagement.html', {'branch':branch,'salary' : salary, 'car':car, 'bid':bid, 'cid': cid, 'user':request.user})
                else:
                    car = Car.objects.filter(branchid=bid)

                    return render_to_response('salaryManagement.html', {'branch':branch,'car':car, 'bid':bid, 'user':request.user})
                         
            return render_to_response('salaryManagement.html', {'branch':branch, 'user':request.user})
    else:
        id = request.POST.get('id')
        payment_date = request.POST.get('payment_date')
        p_salary = request.POST.get('p_salary')
        d_salary = request.POST.get('d_salary')
        etc = request.POST.get('etc')
        etc_content = request.POST.get('etc_content')
        cid = int(request.POST.get('cid'))
        flag = request.POST.get('flag')

        if flag == 'create':
            try:
                Salary.objects.create(carnum_id = cid, payment_date = payment_date, p_salary = p_salary, d_salary = d_salary, etc = etc, etc_content = etc_content)
                return HttpResponse(1)
        
            except:
                return HttpResponse(-1)
        elif flag == 'update':
            try:
                Salary.objects.filter(id=id).update(payment_date = payment_date, p_salary = p_salary, d_salary = d_salary, etc = etc, etc_content = etc_content)
                return HttpResponse(1)
            except:
                return HttpResponse(-1)

        elif flag == 'delete':
            try:
                Salary.objects.filter(id=id).delete()
                
                return HttpResponse(1)
            except:
                return HttpResponse(-1)
