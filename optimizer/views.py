#_*_ coding:utf-8 _*_
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
from django.core.files import File
from django.utils.crypto import get_random_string
from django.core.files.storage import default_storage
from django.conf import settings
import re
import datetime
import operator
import json
import logging
import collections
import sys
import requests
import copy
from graph import PoiGraph, prim, travelling_salesman, mintime_passenger, standard_deviation
reload(sys)
sys.setdefaultencoding('utf-8')

def cmp_viapoints(a, b):
    if a['index'] > b['index']:
        return 1
    elif a['index'] == b['index']:
        return 0
    else:
        return -1

@csrf_exempt
def getRoute(request):
    algorithm = request.GET.get('algorithm')
    reqCoordType = request.GET.get('reqCoordType')

    g = PoiGraph(reqCoordType)
    result = None


    received_json_data = json.loads(request.body)

    unique_id = get_random_string(length=32)
    tmp_dir = settings.TAYO_TMP_DIR
    with open(tmp_dir + unique_id, 'w') as f:
    	jsonfile = File(f)
	json.dump(received_json_data, jsonfile)
	jsonfile.close()

    g.add_vertex(received_json_data['startName'], received_json_data['startX'], received_json_data['startY'], 0)
    for viaPoint in received_json_data['viaPoints']:
        if 'viaPoints' not in viaPoint:
            numPassenger = '1'
        else:
            numPassenger = viaPoint['viaPointNumPassenger']
        g.add_vertex(viaPoint['viaPointName'], viaPoint['viaX'], viaPoint['viaY'], numPassenger)
    g.add_vertex(received_json_data['endName'], received_json_data['endX'], received_json_data['endY'], 0)
     

    g.set_everyweight()

    #return HttpResponse("XXX")


   
    if (algorithm == 'onlytime'):
        result = list()
        result.append(received_json_data['startName'])
        viaPoints = received_json_data['viaPoints']
        viaPoints.sort(cmp_viapoints)
        for viaPoint in viaPoints:
            result.append(viaPoint['viaPointName'])
        result.append(received_json_data['endName'])
    elif (algorithm == 'salesman'):
        result = travelling_salesman(g, g.get_vertex(received_json_data['startName']), g.get_vertex(received_json_data['endName']))
    elif (algorithm == 'mintime'):
        result = mintime_passenger(g, g.get_vertex(received_json_data['startName']), g.get_vertex(received_json_data['endName']))
    elif (algorithm == 'deviation'):
        result = standard_deviation(g, g.get_vertex(received_json_data['startName']), g.get_vertex(received_json_data['endName']))
    else:
    	result = prim(g, g.get_vertex(received_json_data['startName']), g.get_vertex(received_json_data['endName']))


    #xml = getRouteSequential_in(result, received_json_data)

    jsonobj = g.get_json({'unique_id':unique_id}, result)
    return HttpResponse(jsonobj)

def getRouteSequential_in(pointlist, payload):
    #urlstr = "http://route-tayotayo.edticket.com:8080/routes/routeSequential30?version=1"
    urlstr = "https://apis.skplanetx.com/tmap/routes/routeSequential30?version=1"
    appKey = '9c78e49d-c72c-36a6-8e25-5c249e9291a3'
    headers = {'Content-Type': 'application/json', 'appKey': appKey, 'Accept':'application/xml'}

    payload['startTime'] = '201706231300'

    viaPoints = list()
    viaPoint = {}

    for i in range(1,len(pointlist)-1):
        point = pointlist[i]
        for via in payload['viaPoints']:
            if (point == via['viaPointName']):
                viaPoints.append(copy.deepcopy(via))

    r = requests.post(urlstr, data=json.dumps(payload), headers=headers)
    if r.status_code == requests.codes.ok:
        return r.content

    return  ""

@csrf_exempt
def getRouteSequential(request):
    unique_id = request.GET.get('unique_id')
    urlstr = "https://apis.skplanetx.com/tmap/routes/routeSequential30?version=1&format=xml"
    appKey = '9c78e49d-c72c-36a6-8e25-5c249e9291a3'
    headers = {'Content-Type': 'application/json', 'appKey': appKey, 'Accept':'application/xml'}

    tmp_dir = settings.TAYO_TMP_DIR
    with open(tmp_dir + unique_id, 'r') as f:
    	jsonfile = File(f)
	payload = json.load(jsonfile)

    #payload = json.loads(request.body)
    ## it has almost everything
    payload['startTime'] = '201706231300'

    r = requests.post(urlstr, data=json.dumps(payload), headers=headers)
    if r.status_code == requests.codes.ok:
        response = r.text
	response = re.sub(r'<w>-?\d+</w>', '', response)
	response = re.sub(r'<h>-?\d+</h>', '', response)
	response = re.sub(r'<x>-?\d+</x>', '', response)
	response = re.sub(r'<y>-?\d+</y>', '', response)
	response = re.sub(r'7f00ff00', 'ff0000cc', response)
        return HttpResponse(response, content_type = 'application/xml;charset=utf-8')
        ## weight = response['features'][0]['properties']['totalTime']
    else:
        weight = 0


    return HttpResponse('fail' + r.text);


@csrf_exempt
def getRoute2(request):
    algorithm = 'salesman'
    reqCoordType = 'WGS84GEO'

    g = PoiGraph(reqCoordType)
    result = None


    received_json_data = {"reqCoordType":"WGS84GEO","resCoordType":"WGS84GEO","startName":"롯데슈퍼 마두점1","startX":"126.78855157890416","startY":"37.65634555673625","endName":"롯데슈퍼 마두점2","endX":"126.78855157890416","endY":"37.65634555673625","viaPoints":[{"viaPointName":"신한은행ATM 숲속마을3단지지점1","viaPointId":"신한은행ATM 숲속마을3단지지점","index":0,"viaX":"126.79587345576675","viaY":"37.66746213182238"},{"viaPointName":"초가집부동산2","viaPointId":"초가집부동산","index":1,"viaX":"126.78136699892669","viaY":"37.67008120080965"},{"viaPointName":"냉천초교사거리3","viaPointId":"냉천초교사거리","index":2,"viaX":"126.78628980707647","viaY":"37.66726844410171"},{"viaPointName":"일산풍동성원상떼빌5차아파트4","viaPointId":"일산풍동성원상떼빌5차아파트","index":3,"viaX":"126.79618620241394","viaY":"37.665844531450055"},{"viaPointName":"숲속마을9단지성원상떼빌아파트5","viaPointId":"숲속마을9단지성원상떼빌아파트","index":4,"viaX":"126.80349292119143","viaY":"37.673205346565005"},{"viaPointName":"위시티4단지자이아파트6","viaPointId":"위시티4단지자이아파트","index":5,"viaX":"126.81491126609298","viaY":"37.67979023664351"},{"viaPointName":"요진와이하우스아파트7","viaPointId":"요진와이하우스아파트","index":6,"viaX":"126.78788057333918","viaY":"37.675369262123496"},{"viaPointName":"일산위시티자이1단지아파트8","viaPointId":"일산위시티자이1단지아파트","index":7,"viaX":"126.81193195989","viaY":"37.683425402573185"},{"viaPointName":"신한은행ATM 숲속마을3단지지점9","viaPointId":"신한은행ATM 숲속마을3단지지점","index":8,"viaX":"126.79587345576675","viaY":"37.66746213182238"},{"viaPointName":"초가집10","viaPointId":"초가집","index":9,"viaX":"126.78603613240159","viaY":"37.648372776944214"},{"viaPointName":"성원1차아파트11","viaPointId":"성원1차아파트","index":10,"viaX":"126.7956692115661","viaY":"37.664261523640405"},{"viaPointName":"하늘마을5단지휴먼시아아파트12","viaPointId":"하늘마을5단지휴먼시아아파트","index":11,"viaX":"126.78777150159623","viaY":"37.67703766117442"},{"viaPointName":"하늘마을1단지휴먼시아아파트13","viaPointId":"하늘마을1단지휴먼시아아파트","index":12,"viaX":"126.78003518085113","viaY":"37.680378598312835"}]}
    #received_json_data = {"reqCoordType":"WGS84GEO","resCoordType":"WGS84GEO","startName":"롯데슈퍼 마두점","startX":"126.78855157890416","startY":"37.65634555673625","endName":"롯데슈퍼 마두점","endX":"126.78855157890416","endY":"37.65634555673625","viaPoints":[{"viaPointName":"신한은행ATM 숲속마을3단지지점","viaPointId":"신한은행ATM 숲속마을3단지지점","index":0,"viaX":"126.79587345576675","viaY":"37.66746213182238"},{"viaPointName":"신한은행ATM 숲속마을3단지지점","viaPointId":"신한은행ATM 숲속마을3단지지점","index":8,"viaX":"126.79587345576675","viaY":"37.66746213182238"},{"viaPointName":"초가집","viaPointId":"초가집","index":9,"viaX":"126.78603613240159","viaY":"37.648372776944214"},{"viaPointName":"하늘마을1단지휴먼시아아파트","viaPointId":"하늘마을1단지휴먼시아아파트","index":12,"viaX":"126.78003518085113","viaY":"37.680378598312835"}]}

    unique_id = get_random_string(length=32)
    tmp_dir = settings.TAYO_TMP_DIR
    with open(tmp_dir + unique_id, 'w') as f:
    	jsonfile = File(f)
	json.dump(received_json_data, jsonfile)
	jsonfile.close()

    g.add_vertex(received_json_data['startName'], received_json_data['startX'], received_json_data['startY'], 0)
    for viaPoint in received_json_data['viaPoints']:
        if 'viaPoints' not in viaPoint:
            numPassenger = '1'
        else:
            numPassenger = viaPoint['viaPointNumPassenger']
        g.add_vertex(viaPoint['viaPointName'], viaPoint['viaX'], viaPoint['viaY'], numPassenger)
    g.add_vertex(received_json_data['endName'], received_json_data['endX'], received_json_data['endY'], 0)

     

    g.set_everyweight()

    if (algorithm == 'onlytime'):
        result = list()
        result.append(received_json_data['startName'])
        viaPoints = received_json_data['viaPoints']
        viaPoints.sort(cmp_viapoints)
        for viaPoint in viaPoints:
            result.append(viaPoint['viaPointName'])
        result.append(received_json_data['endName'])
    elif (algorithm == 'salesman'):
        result = travelling_salesman(g, g.get_vertex(received_json_data['startName']), g.get_vertex(received_json_data['endName']))
    elif (algorithm == 'mintime'):
        result = mintime_passenger(g, g.get_vertex(received_json_data['startName']), g.get_vertex(received_json_data['endName']))
    elif (algorithm == 'deviation'):
        result = standard_deviation(g, g.get_vertex(received_json_data['startName']), g.get_vertex(received_json_data['endName']))
    else:
    	result = prim(g, g.get_vertex(received_json_data['startName']), g.get_vertex(received_json_data['endName']))


    #xml = getRouteSequential_in(result, received_json_data)

    jsonobj = g.get_json({'unique_id':unique_id}, result)
    return HttpResponse(jsonobj)

