#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
import requests,logging
from datetime import datetime
from send import sendPin
from requests.auth import HTTPBasicAuth
from base64 import b64encode
from passenger.models import StudentInfo, PersonalInfo
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
        sid = request.POST.getlist('sid[]')
        aid = int(request.session.get('instituteid'))
        kind = int(request.POST.get('kind'))

        reqtime = str(datetime.now())[:16]

	access_token = getToken()
        token = 'Basic ' + access_token

        if kind == 0 or 3:
            sInfo = StudentInfo.objects.filter(id__in = sid)
        else:
            sInfo = StudentInfo.objects.filter(aid_id = aid)

        for s in sInfo:
            list_to = []
            temp_to = {}
            pInfo = PersonalInfo.objects.get(id = s.personinfo_id )
            sname = s.sname
            aname = s.aname
            if s.parents_phonenumber:
                to_parents = s.parents_phonenumber[1:]
                temp_to["to"] = ("82"+ to_parents).encode('utf8')
                list_to.append(temp_to)
            
            if s.self_phonenumber:
                to_self = s.self_phonenumber[1:]
                temp_to["to"] = ("82"+to_self).encode('utf8')
                list_to.append(temp_to)

            if s.grandparents_phonenumber:
                to_grandparents = s.grandparents_phonenumber[1:]
                temp_to["to"] = ("82"+ to_grandparents).encode('utf8')
                list_to.append(temp_to)

            if list_to == []:
                temp_to["to"] = ("8201045013555").encode('utf8')
                list_to.append(temp_to)            

            list_to = json.dumps(list_to)
         
            pin = pInfo.pin_number
            status = sendPin(token, kind, list_to, aname, sname, pin)

            if status == 'R000':
                s.sended_time = reqtime
            elif status == 'R001':
                s.sended_time = '일시적 서비스 장애'
            elif status == 'R002':
                s.sended_time = '인증 실패'
            elif status == 'R003':
                s.sended_time = '수신번호 형식 오류'
            elif status == 'R009':
                s.sended_time = '서버 용량 초과, 재시도 요망'
            elif status == 'R013':
                s.sended_time = '발송 가능 건수 초과'
            else:
                s.sended_time ='발송 실패'
            s.save()
 
        return HttpResponse(status)
