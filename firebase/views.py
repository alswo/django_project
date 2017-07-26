from django.shortcuts import render_to_response
from django.http import HttpResponse, JsonResponse
from passenger.models import StudentInfo
import firebase_admin
from firebase_admin import credentials
from jose import jwt
import Crypto.PublicKey.RSA as RSA
from jwt.contrib.algorithms.pycrypto import RSAAlgorithm
from django.views.decorators.csrf import csrf_exempt
import time

"""
service_account_email = "firebase-adminsdk-2raa9@tayo-f698c.iam.gserviceaccount.com"

private_key=RSA.importKey("-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDUYpm/qVkoPF+3\nttm4e6Y0vDyTfOc/CnxKwbMZdsRIkEKCyx8/N2omzxwS0qnZIC7o/z53Vk/G1RX0\nfXWATZoH+jxseg/g0DPmFuT9ebfDdGmXwLb6RzuW0PN4KL7HrWZVu3BzcUepPGq7\nTBqjnvR+N5bqy/g/zsK2smNP88xFRe78R6UOc+nzMEmUxkMmSmRcBW5rntOR0mZ4\nX6AMXAS+FcXS9zyTy/8wvVOig7rcTI3okF9wrSHhncwKXSLgBimCr5lgxACwXdNN\nr60sawqqyMBEJuFy+7xI5vZOFf2AOj0H7ZQsIWlWSVz+rzb4Gnhk55XdIZtl0nSj\ni8LILqCJAgMBAAECggEABYOX1UuKxoomvAjRx0Hik0ztz7B2+oKFrpUv1rHoL7Ab\nIfUvFv+T0HUhF/YDNeFphmAWGZgSkyl2G/Zj5hRdsuZSykgzAFW3ezpN8KzH0hnE\nIg39UismR2ieYZjBN0LvvLsUlNK0lxa7+KflqyjV1S8RSoBILjPqhz7DaFB+la/K\ng5tyXLqNbjPJL4urcaI7YYfW1f0GDsq8UBd8beIDD+CpD6Fpc3ll35OEVwOhnpa+\nMwqaHx4r3mDw6OU/Paua7ptmbHb7+siKLyv+/M/oN1sMRnNheTBMpCv2o/kmO/0C\n+mZ3hzLS08NNc7QT51H1J66FIh40lcbHoc+i5CAYeQKBgQDu8iUVTffLP+y2DxJt\nCjVp56gVOpCUwHgc1lCWjwTurBhMzZqJCJYf2pX1YAWgCIwWuaQCU3e6Ti6lqaFw\nCKtNM8kkb8NaS4FTMKKcUmwxv8M8E9VtvK2bTJdCt0TTR8VSJXwPWXdn17jcom8k\ng+wcFFYtvBvtZ0cdGsP8bFGWZQKBgQDjiygOyP+YFFm1xriTydTh0MlR/uZeI+ia\nTZu1tKQz88pTvUxKF3UpcJNB5Oni0xhwS3booONoi91j8FHB5jKsbnImbIpTOiEJ\nrFUvbEELIXJZ6TRZrEJEuR4BFU52jlRslyYTgUo8r4Soh/QAMFi3sglsPulwT284\nc5nbAdFdVQKBgDbNdLHhMv77x1euN0So/b0vc36C8xwa1LGQeeU+Ihx3fg9HbLUX\nMg9WO+SORFwC+dZQd4xNBn3FZq96K1udsWRAh1aDB6QTAzNISVNfGA+E8ss5pU7I\n4mxm8Z5MmE14/YmsrTp8A4XelTiNTL5sP1/lTiqpJSKa+FV1iRPA6Cl9AoGBAMKM\nnmlVzcNX0wQqrnId5VhVzWvAB3OCPESCCponoyWQUfObLHlE6TXPPPjgImF/n6uT\nuk1YEle3Dkl+lki066qmnA7iSrqyPsEoiYUMh+heZokdbVcmg1qC9HZ0oyuWsfRO\nn42Zw8FzSHdYFnV64L/fB1N3ztvp7uxTWr74JOwpAoGBAOxCZBtDYU7U5KrVISF+\nWaJki2Hcyqsg64MxGtNAHnHKq8GXhG4wIWuukOjK24Kfn9/t34l0TDRYxJJnGjFA\nX0lH6ENF+hJjezxCVB+hPJAA4flTKQex/WRxNrDGOirgUIiZZs7CUbk/G+A41JKc\nWP1C8fv79RdjLmJ2wDggOTK9\n-----END PRIVATE KEY-----\n")
"""
def getResponse(debug, code, msg):
    if (debug == 1):
        return HttpResponse(msg)
    else:
        return JsonResponse({'code': code, 'msg': msg})

@csrf_exempt
def get_token(request):
    if request.method == 'GET':
        return render_to_response('authorizer.html')

    elif request.method == 'POST':
        pin = request.POST.get('pin')
	debug =request.POST.get('debug')

	if (debug):
            debug = 1

	else:
            debug = 0

        try:
            sInfo = StudentInfo.objects.get(pin_number = pin)

        except Exception as e:
            msg = 'PIN does not correct'

	    return getResponse(debug,400,msg)

        # try:
        #     cred = credentials.Certificate("/home/ubuntu/lee/django_project/firebase/tayo-f698c-firebase-adminsdk-2raa9-d658cca556.json")
        #     firebase_admin.initialize_app(cred)
        #
        # except Exception as e:
        #     return HttpResponse(e.message)

        if sInfo != 0:
            # tokenizer = create_custom_token(pin)
            studentInfo = {}
            studentInfo['sid'] = sInfo.id
            studentInfo['aid'] = sInfo.aid
            studentInfo['phone'] = sInfo.phone1
            studentInfo['pin'] = sInfo.pin_number

            return JsonResponse(studentInfo)


# def create_custom_token(uid):
#   try:
#     payload = {
#       "iss": service_account_email,
#       "sub": service_account_email,
#       "aud": "https://identitytoolkit.googleapis.com/google.identity.identitytoolkit.v1.IdentityToolkit",
#       "exp": int(time.time()) + (60*60),
#       "uid": uid
#     }
#
#     return jwt.encode(payload, private_key, algorithm='RS256')
#
#   except Exception as e:
#     print "Error creating custom token: " + e.message
#     return e.message
