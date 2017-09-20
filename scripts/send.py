#!/usr/bin/python
# -*- coding: utf-8 -*-

from passenger.models import StudentInfo, PersonalInfo
from passenger.dateSchedule import timeToDate
from fcmdev.models import PropOfDevice
from fcm_django.models import FCMDevice
from schedule.models import Inventory, ScheduleTable

from collections import Counter
import sys
import requests
import simplejson
import ast

reload(sys)
sys.setdefaultencoding('utf-8')



def run():
    pushcheck = True
    pin = "tUP3Ebh"
    msg = "오늘 수지이스턴어학원 등원을 위한 15:40 [풍덕천동 삼성4차]승차 외1건의 스케줄이 있습니다."
    print type(msg)
    token = "dHKukmKTKsA:APA91bEpQzGdZA5xMAKV5rraIruTGfkmKd9tHfJzBWcZIvUjAt2ZVQcJ76ywlvrpsMpt8ghqh3llGhkiJxccXBAib4qRccJVp7JJs4Wj1HLPGH3kKAdO00SzibptgCrscXu9WD5s73TI"

    types = "ios"
    url = 'https://fcm.googleapis.com/fcm/send'
    header = {'authorization': 'key=AAAAWVvmwNU:APA91bH0IjidQtMmX6q9SRVekZqzNmWKRR15mdjOFFAt05v3E7PziYRb7sLMbtCtNXZYyKrz--fKvoZdDY94yjOrH9G6z-axN7qWS7H5VMBRUy8Z6-dysdj9ZaCYrESl2wnIfOoSnh7X','content-type': 'application/json'}
    result = {}
    if pushcheck == False:
        print ("he/she doesn't want to receive push message.")
    else:
        if types == 'android':
            payload = '{\n    "to" : "' + token + '","priority" : "high", "content-available" : "true","collapse_key" : "Updates Available" ,"notification": {\t  "body" : "'+msg+'","title" : "shuttle tayo", "sound":"default", "color":"#0066ff"},\t}'
        elif types == 'ios':
            payload = '{\n    "to" : "' + token + '","priority" : "high", "content-available" : "true","collapse_key" : "Updates Available" ,"notification": {\t  "body" : "'+msg+'", "sound":"default", "color":"#0066ff"},\t}'
        try:
            response = requests.request('POST', url, data=payload, headers=header)
            # try:
            #     result = ast.literal_eval(response.text)
            #     status = str(result['success'])
            #     pushurl = 'http://mj.edticket.com/fcmdev/pushConfirmInfo'
            #     data = "pin="+pin+"&confirming="+result+"&status="+status+"&token="+token
            #     headers = {'content-type': "application/x-www-form-urlencoded"}
            #     response = requests.request("POST", pushurl, data=data, headers=headers)
            # except:
            #     print "msg check error"
        except:
            print ("msg send error")
