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

    jsonobj = g.get_json({'xml':''}, result)
    return HttpResponse(jsonobj)

def getRouteSequential_in(pointlist, payload):
    urlstr = "http://route-tayotayo.edticket.com:8080/routes/routeSequential30?version=1"
    #urlstr = "https://apis.skplanetx.com/tmap/routes/routeSequential30?version=1"
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
    #urlstr = "http://route-tayotayo.edticket.com:8080/routes/routeSequential30?version=1"
    urlstr = "https://apis.skplanetx.com/tmap/routes/routeSequential30?version=1"
    appKey = '9c78e49d-c72c-36a6-8e25-5c249e9291a3'
    headers = {'Content-Type': 'application/json', 'appKey': appKey, 'Accept':'application/xml'}

    payload = json.loads(request.body)
    ## it has almost everything
    payload['startTime'] = '201706231300'

    r = requests.post(urlstr, data=json.dumps(payload), headers=headers)
    if r.status_code == requests.codes.ok:
        response = r.json()
        return HttpResponse("success" + str(response))
        ## weight = response['features'][0]['properties']['totalTime']
    else:
        weight = 0


    return HttpResponse(r.text);
