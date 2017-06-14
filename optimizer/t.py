#!/usr/bin/python

import requests

 
urlstr = "http://route-tayotayo.edticket.com:8080/routes?version=1"
payload = {'appKey': "9c78e49d-c72c-36a6-8e25-5c249e9291a3", 'version': "1", 'startX' : '14148317.661607', 'startY' : '4494878.084352', 'endX' : '14148809.322692', 'endY' : '4493197.096773'}
r = requests.get(urlstr, params=payload)
if r.status_code == requests.codes.ok:
        response = r.json()
        print response['features'][0]['properties']['totalTime']

