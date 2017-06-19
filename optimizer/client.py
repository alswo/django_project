#!/usr/bin/python
#_*_ coding:utf-8 _*_


import requests  
import json
#algorithm = ['prim', 'salesman', 'onlytime', 'mintime']
algorithm = ['deviation']
params = {}
url = "http://curtis-tayotayo.edticket.com/optimizer/getRoute"
#url = "http://curtis-tayotayo.edticket.com/optimizer/getRoute"
#data = {'startName': '낙원중학교', 'startX':'14148317.661607', 'startY':'4494878.084352', 'endName':'원마을현대힐스테이트', 'endX':'14148219.329390', 'endY':'4494726.671574', 'viaPoints': [{ 'viaPointName':'낙생고등학교', 'viaPointX':'14148809.322692', 'viaPointY':'4493197.096773'}, {'viaPointName':'판교도서관', 'viaPointX':'14147628.099206', 'viaPointY':'4493893.745713'}]}
data = {'startName': 'A', 'startX':'14148317.661607', 'startY':'4494878.084352', 'endName':'B', 'endX':'14148219.329390', 'endY':'4494726.671574', 'viaPoints': [{ 'viaPointName':'C', 'index':1, 'viaPointX':'14148809.322692', 'viaPointY':'4493197.096773', 'viaPointNumPassenger': 1}, {'viaPointName':'D', 'index':0, 'viaPointX':'14147628.099206', 'viaPointY':'4493893.745713', 'viaPointNumPassenger': 30}]}
strdata = '{"startName":"경기 성남시 분당구 대왕판교로606번길 45 (삼평동, 판교역 푸르지오시티)","startX":"14150027.652674","startY":"4494574.871752","endName":"경기 성남시 분당구 대왕판교로606번길 45 (삼평동, 판교역 푸르지오시티)","endX":"14150027.652674","endY":"4494574.871752","viaPoints":[{"viaPointName":"경기 성남시 분당구 성남대로 지하 333 (정자동, 정자역)","index":0,"viaPointX":"14149604.638609","viaPointY":"4490271.675590","viaPointNumPassenger":"1"},{"viaPointName":"경기 성남시 분당구 성남대로 지하 601 (서현동, 서현역)","index":1,"viaPointX":"14151285.872141","viaPointY":"4492924.676794","viaPointNumPassenger":"1"}]}'
headers = {'content-type': 'application/json'}
for algo in algorithm:
    print "algorithm : ", algo
    params['algorithm'] = algo
    #r=requests.post(url, params=params, data=json.dumps(data), headers=headers)
    r=requests.post(url, params=params, data=strdata, headers=headers)
    print r.text
print "\n\n"
print json.dumps(data)
