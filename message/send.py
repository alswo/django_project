# -*- encoding:utf-8 -*-
import requests
import json
from django.http import HttpResponse 
def sendPin(token, kind, list_to, aname, sname, pin):

    url = 'https://sms.supersms.co:7020/sms/v3/multiple-destinations'
    token = token.encode('utf8')
    text_for_e_customer ="학부모님 안녕하세요?\\n드디어, 셔틀타요 어플리케이션이 출시되었습니다.\\n이제, 아이의 차량 승/하차 시간, 아이가 탑승할 차량의 실시간 위치를 확인할 수 있습니다.\\n스마트폰으로 아래의 링크에 접속하시면 다운로드 할 수 있습니다.\\n앞으로 지속적으로 발전하는 셔틀타요가 되겠습니다.\\n감사합니다.\\n\\n안드로이드 다운로드 링크:\\nwww.tayotayo.net\\n\\n아이폰 다운로드 링크:\\nwww.tayotayo.net\\n\\n" + aname + "학원 " + sname + "의 고유 핀번호: "+ pin

    text_for_n_customer = "학무보님 안녕하세요?\\n셔틀타요 어플리케이션 이용방법을 안내드립니다.\\n이제, 아이의 차량 승/하차 시간, 아이가 탑승할 차량의 실시간 위치를 확인할 수 있습니다.\\n스마트폰으로 아래의 링크에 접속하시면 다운로드 할 수 있습니다.\\n앞으로 지속적으로 발전하는 셔틀타요가 되겠습니다.\\n감사합니다.\\n\\n 안드로이드 다운로드 링크:\\ntayotayo.net\\n\\n아이폰 다운로드 링크:\\ntayotayo.net\\n\\n"  + aname + "학원 " + sname + "의 고유 핀번호: "+ pin
    text_pin_resend = "셔틀타요 어플리케이션 핀번호 재전송\\n"+ aname + "학원 " + sname + "의 고유 핀번호: "+ pin

    if kind == 0:
        text = text_for_n_customer.encode('utf8')
    elif kind == 1:
        text = text_for_n_customer.encode('utf8')
    elif kind == 2:
        text = text_for_e_customer.encode('utf8')
    elif kind == 3:
        text = text_pin_resend.encode('utf8')
    
    list_to = str(list_to)
    
    data = '{"title":"test","from":"07074900210","text":"'+text+'","ttl":"1000","destinations":'+list_to+'}'
    headers = {"Authorization" : token, "Accept" : "application/json", "Content-Type" : "application/json"}

    response = requests.post(url, headers = headers, data = data)

    status = json.loads(response.text)['destinations'][0]['status']

    return status
