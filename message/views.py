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
	
	url = 'https://sms.supersms.co:7020/sms/v3/multiple-destinations'

        if kind == 0:
            sInfo = StudentInfo.objects.filter(id__in = sid)
            for s in sInfo:
                pInfo = PersonalInfo.objects.get(id = s.personinfo_id )
                text = "학부모님 안녕하세요?\\n드디어, 셔틀타요 어플리케이션이 출시되었습니다.\\n이제 아이의 차량 승/하차 시간, 아이가 탑승할 차량의 실시간 위치를 확인할 수 있습니다.\\n스마트폰으로 아래의 링크에 접속하시면 다운로드 할 수 있습니다.\\n앞으로 지속적으로 발전하는 셔틀타요가 되겠습니다.\\n감사합니다.\\n\\n안드로이드 다운로드 링크:\\nwww.tayotayo.net\\n\\n아이폰 다운로드 링크:\\nwww.tayotayo.net\\n\\n"+ s.sname + '의 고유 핀번호:' + pInfo.pin_number     
                text_2 = "학무보님 안녕하세요?\\n셔틀타요 어플리케이션 이용방법을 안내드립니다.\\n" 
                to = s.parents_phonenumber[1:]
                
                status = sendPin(token, text, to)
 
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
            return HttpResponse('selected success') 

        elif kind == 1:
            sInfo = StudentInfo.objects.filter(aid_id = aid)
            for s in sInfo:
                pInfo = PersonalInfo.objects.get(id = s.personinfo_id )
                text = s.sname + '의 핀번호는 ' + pInfo.pin_number +'입니다'
                to = s.parents_phonenumber[1:]

                status = sendPin(token, text, to)

                #data = '{"title":"test", "from" : "07074900210", "text": "test message", "ttl": "1000", "destinations" : [{"to":'+ to +'}]}'
                #response = requests.post(url, headers = headers, data = data)
            return HttpResponse('all send success')
