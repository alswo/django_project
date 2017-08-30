# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
import requests
from requests.auth import HTTPBasicAuth
from base64 import b64encode
from passenger.models import StudentInfo
from django.views.decorators.csrf import csrf_exempt
import json

def getToken():
    url = 'https://auth.supersms.co:7000/auth/v3/token'
    headers = {"Accept":"application/json","X-IB-Client-Id":"edticket_msg","X-IB-Client-Passwd":"829NSOB10GZD10UXUJI3"}

    response = requests.post(url, headers = headers)

    access_token = json.loads(response.text)['accessToken']

    return access_token

@csrf_exempt
def sendMessage(request):
    if request.method == "POST":
        sid = request.POST.getlist('sid')
        aid = request.session.get('instituteid')
        kind = request.POST.get('kind')

        return HttpResponse(aid)
        #reqtime = str(datetime.datetime.now())[:16]

        StudentInfo.objects.filter(id__in = sid)

        access_token = getToken()
        token = 'Basic ' + access_token

        url = 'https://sms.supersms.co:7020/sms/v3/multiple-destinations'

        headers = {"Authorization" : token , "Accept" : "application/json", "Content-Type" : "application/json"}
        data = '{"title":"test", "from" : "07074900210", "text": "test message", "ttl": "1000", "destinations" : [{"to" :"821045013555"}]}'

        response = requests.post(url, headers = headers, data = data)
