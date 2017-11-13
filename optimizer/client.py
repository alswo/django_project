#!/usr/bin/python
#_*_ coding:utf-8 _*_


import requests  
import json
#algorithm = ['prim', 'salesman', 'onlytime', 'mintime']
algorithm = ['salesman']
params = {}
url = "http://route2-tayotayo.edticket.com/optimizer/getRoute"
#url = "http://curtis-tayotayo.edticket.com/optimizer/getRoute"
#data = {'startName': '낙원중학교', 'startX':'14148317.661607', 'startY':'4494878.084352', 'endName':'원마을현대힐스테이트', 'endX':'14148219.329390', 'endY':'4494726.671574', 'viaPoints': [{ 'viaPointName':'낙생고등학교', 'viaPointX':'14148809.322692', 'viaPointY':'4493197.096773'}, {'viaPointName':'판교도서관', 'viaPointX':'14147628.099206', 'viaPointY':'4493893.745713'}]}
#strdata = {'startName': 'A', 'startX':'14148317.661607', 'startY':'4494878.084352', 'endName':'B', 'endX':'14148219.329390', 'endY':'4494726.671574', 'viaPoints': [{ 'viaPointName':'C', 'index':1, 'viaPointX':'14148809.322692', 'viaPointY':'4493197.096773', 'viaPointNumPassenger': 1}, {'viaPointName':'D', 'index':0, 'viaPointX':'14147628.099206', 'viaPointY':'4493893.745713', 'viaPointNumPassenger': 30}]}
#strdata = '{"reqCoordType":"WGS84GEO","resCoordType":"WGS84GEO","startName":"롯데슈퍼 마두점","startX":"126.78855157890416","startY":"37.65634555673625","endName":"롯데슈퍼 마두점","endX":"126.78855157890416","endY":"37.65634555673625","viaPoints":[{"viaPointName":"신한은행ATM 숲속마을3단지지점","viaPointId":"신한은행ATM 숲속마을3단지지점","index":0,"viaX":"126.79587345576675","viaY":"37.66746213182238"},{"viaPointName":"초가집부동산","viaPointId":"초가집부동산","index":1,"viaX":"126.78136699892669","viaY":"37.67008120080965"},{"viaPointName":"냉천초교사거리","viaPointId":"냉천초교사거리","index":2,"viaX":"126.78628980707647","viaY":"37.66726844410171"},{"viaPointName":"일산풍동성원상떼빌5차아파트","viaPointId":"일산풍동성원상떼빌5차아파트","index":3,"viaX":"126.79618620241394","viaY":"37.665844531450055"},{"viaPointName":"숲속마을9단지성원상떼빌아파트","viaPointId":"숲속마을9단지성원상떼빌아파트","index":4,"viaX":"126.80349292119143","viaY":"37.673205346565005"},{"viaPointName":"위시티4단지자이아파트","viaPointId":"위시티4단지자이아파트","index":5,"viaX":"126.81491126609298","viaY":"37.67979023664351"},{"viaPointName":"요진와이하우스아파트","viaPointId":"요진와이하우스아파트","index":6,"viaX":"126.78788057333918","viaY":"37.675369262123496"},{"viaPointName":"일산위시티자이1단지아파트","viaPointId":"일산위시티자이1단지아파트","index":7,"viaX":"126.81193195989","viaY":"37.683425402573185"},{"viaPointName":"신한은행ATM 숲속마을3단지지점","viaPointId":"신한은행ATM 숲속마을3단지지점","index":8,"viaX":"126.79587345576675","viaY":"37.66746213182238"}]}'
#strdata = '{"startName":"서울 송파구 문정로 83 (문정동, 문정래미안아파트)","startX":"14152072.529876","startY":"4507516.488767","endName":"서울 송파구 문정로 83 (문정동, 문정래미안아파트)","endX":"14152072.529876","endY":"4507516.488767","viaPoints":[{"viaPointName":"경기 성남시 수정구 복정동 668-9","index":0,"viaPointX":"14152054.595069","viaPointY":"4503629.872582"},{"viaPointName":"서울 송파구 중대로 24 (문정동, 올림픽훼밀리타운)","index":1,"viaPointX":"14149938.287861","viaPointY":"4507365.283172","viaPointNumPassenger":"1"},{"viaPointName":"서울 송파구 동남로 189 (가락동, 가락쌍용아파트)","index":2,"viaPointX":"14151848.654011","viaPointY":"4508423.378414","viaPointNumPassenger":"1"},{"viaPointName":"서울 송파구 송파대로8길 42 (장지동, 송파파인타운12단지)","index":3,"viaPointX":"14152284.964571","viaPointY":"4506050.899633","viaPointNumPassenger":"1"}]}'
strdata = '{"startName":"A","startX":"14152072.529876","startY":"4507516.488767","endName":"B","endX":"14152072.529876","endY":"4507516.488767","viaPoints":[{"viaPointName":"C","viaPointId":"C","index":0,"viaPointX":"14152054.595069","viaPointY":"4503629.872582", "viaX":"14152054.595069", "viaY":"4503629.872582"},{"viaPointName":"D","viaPointId":"D","index":1,"viaPointX":"14149938.287861","viaPointY":"4507365.283172","viaX":"14149938.287861","viaY":"4507365.283172","viaPointNumPassenger":"1"},{"viaPointName":"E","viaPointId":"E","index":2,"viaPointX":"14151848.654011","viaPointY":"4508423.378414","viaX":"14151848.654011", "viaY":"4508423.378414","viaPointNumPassenger":"1"},{"viaPointName":"F","viaPointId":"F","index":3,"viaPointX":"14152284.964571","viaPointY":"4506050.899633","viaX":"14152284.964571","viaY":"4506050.899633","viaPointNumPassenger":"1"}]}'
#strdata = '{"startName":"경기 성남시 분당구 대왕판교로606번길 45 (삼평동, 판교역 푸르지오시티)","startX":"14150027.652674","startY":"4494574.871752","endName":"경기 성남시 분당구 대왕판교로606번길 45 (삼평동, 판교역 푸르지오시티)","endX":"14150027.652674","endY":"4494574.871752","viaPoints":[{"viaPointName":"경기 성남시 분당구 성남대로 지하 601 (서현동, 서현역)","viaPointId":"경기 성남시 분당구 성남대로 지하 601 (서현동, 서현역)","index":0,"viaX":"14151285.872141","viaY":"4492924.676794","viaPointNumPassenger":"1"}]}'
headers = {'content-type': 'application/json'}
for algo in algorithm:
    print "algorithm : ", algo
    params['algorithm'] = algo
    params['unique_id'] = '11133'
    #r=requests.post(url, params=params, data=json.dumps(data), headers=headers)
    r=requests.post(url, params=params, data=strdata, headers=headers)
    print r.status_code
    print "[Response]"
    print r.text
print "\n\n"
#print json.dumps(data)
