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
from graph import PoiGraph, prim, travelling_salesman
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
    g = PoiGraph()
    result = None

    algorithm = request.GET.get('algorithm')
    onlytime = request.GET.get('onlytime')

    received_json_data = json.loads(request.body)

    g.add_vertex(received_json_data['startName'], received_json_data['startX'], received_json_data['startY'])
    for viaPoint in received_json_data['viaPoints']:
        g.add_vertex(viaPoint['viaPointName'], viaPoint['viaPointX'], viaPoint['viaPointY'])
    g.add_vertex(received_json_data['endName'], received_json_data['endX'], received_json_data['endY'])
     

    g.set_everyweight()
   
    if (onlytime == 'true'):
        result = list()
        result.append(received_json_data['startName'])
        viaPoints = received_json_data['viaPoints']
        viaPoints.sort(cmp_viapoints)
        for viaPoint in viaPoints:
            result.append(viaPoint['viaPointName'])
        result.append(received_json_data['endName'])
    else:
    	if (algorithm == 'salesman'):
        	result = travelling_salesman(g, g.get_vertex(received_json_data['startName']), g.get_vertex(received_json_data['endName']))
    	else:
    		result = prim(g, g.get_vertex(received_json_data['startName']), g.get_vertex(received_json_data['endName']))

    jsonobj = g.get_json(result)
    return HttpResponse(jsonobj)
