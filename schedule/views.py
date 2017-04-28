from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from schedule.models import Inventory, ScheduleTable, Building, Branch, InventoryRequest
from passenger.models import Academy, Group, Student, StudentInfo
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.core import serializers
from passenger.dateSchedule import timeToDate
from rest_framework.parsers import FormParser
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from itertools import chain
import operator
import json

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
        bid = request.GET.get('bid')
        aid = request.GET.get('aid')
        day = request.GET.get('day')
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

        return render_to_response('getSchedule.html', {"contacts": contacts, "bid" : bid, "aid" : aid})

@csrf_exempt
def putSchedule(request):
    if request.method == "GET":
        bid = request.GET.get('bid')
        if bid:
            academy = Academy.objects.filter(bid = bid)
            group = Group.objects.filter(bid = bid)

            return render_to_response('putSchedule.html', {"academy" : academy, "bid" : bid, "group" : group,'user':request.user})

    elif request.method == "POST":
        day = request.POST.get('day')
        carnum = request.POST.get('carnum')
        bid = request.POST.get('bid')
        time = request.POST.getlist('time[]')
        addr = request.POST.getlist('addr[]')
        name = request.POST.getlist('name[]')
        name2 = request.POST.getlist('name[]')
        academy = request.POST.getlist('academy[]')
        load = request.POST.getlist('load[]')

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
        slist_temp3 = list(set(slist_temp2.split(',')))
        slist = []

        studentInfo = StudentInfo.objects.filter(aid__in = [aid for aid in alist]).filter(sname__in = [name for name in slist_temp3])

        for s in studentInfo:
            slist.append(s.id)

        stime = int(time[0].split(':')[0] + time[0].split(':')[1])
        etime = int(time[-1].split(':')[0] + time[-1].split(':')[1])

        anamelist_inven = []

        for aname in alist:
            aca = Academy.objects.get(id = aname)
            anamelist_inven.append(aca.name)


        try:
            inven = Inventory.objects.create(carnum = carnum, bid = bid, snum = snum, day = day , alist=alist, anamelist = anamelist_inven, slist=slist, stime = stime, etime = etime)

        except:
            return HttpResponse("error inventory save")


        iid = inven.id


        for i in range(len(time)):
            if i == 0:
                stable = ScheduleTable(iid_id = iid, time = time[i], addr = addr[i], alist='{}', slist='{}', sname=list(name2[i]), tflag='{}', lflag=2)
                stable.save()

            elif i == len(time) - 1:
                stable = ScheduleTable(iid_id = iid, time = time[i], addr = addr[i], alist='{}', slist='{}', sname=list(name2[i]), tflag='{}', lflag=3)
                stable.save()

            elif 0 < i < len(time) - 1:
                sidlist = []
                temp_aca = academy[i].split(',')
                temp_name = name2[i].split(',')
                student = StudentInfo.objects.filter(aid__in=[ a for a in temp_aca])

                for s in student:
                    for k in temp_name:
                        if s.sname == k:
                            sidlist.append(s.id);

                if len(sidlist) != len(temp_name):
                    return HttpResponse(sidlist)

                temp_lflag = [0 for z in range(len(temp_name))]

                anamelist = []
                for aid in temp_aca:
                    aname = Academy.objects.get(id = aid)
                    anamelist.append(aname.name)

                try:
                    stable = ScheduleTable(iid_id = iid, time = time[i], addr = addr[i], alist=temp_aca, anamelist = anamelist, slist=sidlist, sname=temp_name, tflag=temp_lflag, lflag=load[i])
                    stable.save()
                except:
                    return HttpResponse(academy[i])

        return HttpResponse("success")
