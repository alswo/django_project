#!/usr/bin/python
#_*_ coding:utf-8 _*_


import requests  
import json
algorithm = ['prim', 'salesman']
url = "http://curtis-tayotayo.edticket.com/optimizer/getRoute"
data = {'startName': '낙원중학교', 'startX':'14148317.661607', 'startY':'4494878.084352', 'endName':'원마을현대힐스테이트', 'endX':'14148219.329390', 'endY':'4494726.671574', 'viaPoints': [{ 'viaPointName':'낙생고등학교', 'viaPointX':'14148809.322692', 'viaPointY':'4493197.096773'}, {'viaPointName':'판교도서관', 'viaPointX':'14147628.099206', 'viaPointY':'4493893.745713'}]}
#data = {'startName': 'A', 'startX':'14148317.661607', 'startY':'4494878.084352', 'endName':'B', 'endX':'14148219.329390', 'endY':'4494726.671574', 'viaPoints': [{ 'viaPointName':'C', 'viaPointX':'14148809.322692', 'viaPointY':'4493197.096773'}, {'viaPointName':'D', 'viaPointX':'14147628.099206', 'viaPointY':'4493893.745713'}]}
headers = {'content-type': 'application/json'}
for algo in algorithm:
    print "algorithm : ", algo
    urlstr = url + "?algorithm=" + algo
    r=requests.post(urlstr, data=json.dumps(data), headers=headers)
    print r.text
print json.dumps(data)
