# -*- encoding:utf-8 -*-
import requests
import json

def sendPin(token, text, to):
    url = 'https://sms.supersms.co:7020/sms/v3/multiple-destinations'
    token = token.encode('utf8')
    to = to.encode('utf8')
    text = text.encode('utf8')
    data = '{"title":"test", "from" : "07074900210", "text": "'+text+'", "ttl": "1000", "destinations" : [{"to":"82'+to+'"}]}'
    
    headers = {"Authorization" : token, "Accept" : "application/json", "Content-Type" : "application/json"}   
 
    response = requests.post(url, headers = headers, data = data)

    status = json.loads(response.text)['destinations'][0]['status'] 

    return status
