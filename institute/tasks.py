#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tayo.celery import app
from passenger.models import BillingHistory, Academy
from institute.views import BANKCODES
from django.db import connection
from django.utils import timezone
import sys
import requests
import simplejson
import ast
reload(sys)
sys.setdefaultencoding('utf-8')


@app.task
def updateBillingHistory():
	billinghistorys = BillingHistory.objects.all()


	for b in billinghistorys:
		academys = Academy.objects.filter(id = b.academy_id)
		for a in academys:
			cursor = connection.cursor()
			cursor.execute("SELECT iacct_no FROM vacs_ahst;")
			iacct_nos = cursor.fetchall()

			for acct_no in iacct_nos:
				acct = u"%s" % acct_no
				acct = acct.strip()
				if a.bank003 == acct:
					bank_cd = "기업은행"
					aid = a.id
					ex(acct, bank_cd, aid)

				elif a.bank004 == acct:
					bank_cd = "국민은행"
					aid = a.id
					ex(acct, bank_cd, aid)

				elif a.bank011 == acct:
					bank_cd = "농협은행"
					aid = a.id
					ex(acct, bank_cd, aid)

				elif a.bank020 == acct:
					bank_cd = "우리은행"
					aid = a.id
					ex(acct, bank_cd, aid)

				elif a.bank027 == acct:
					bank_cd = "시티은행"
					aid = a.id
					ex(acct, bank_cd, aid)

				elif a.bank071 == acct:
					bank_cd = "우체국은행"
					aid = a.id
					ex(acct, bank_cd, aid)

				elif a.bank081 == acct:
					bank_cd = "하나은행"
					aid = a.id
					ex(acct, bank_cd, aid)

				elif a.bank088 == acct:
					bank_cd = "신한은행"
					aid = a.id
					ex(acct, bank_cd, aid)

				else:
					print " nothing"

def ex(acct, bank_cd, aid):
	cursor = connection.cursor()
	cursor.execute("SELECT tr_il FROM vacs_ahst WHERE iacct_no = %s" , [acct])
	tr_il = cursor.fetchone()
	tr_il = u"%s" % tr_il
	cursor.execute("UPDATE passenger_billinghistory SET billing_il = %s, billing_bank = %s WHERE academy_id = %s", [tr_il, bank_cd, aid])
	cursor.close()
	connection.commit()
	connection.close()


def plusPenaltyCharge(amt):
	new_amt = int(amt * 1.02 / 100) * 100
	return new_amt

def getStartBillDay():
	return "%04d%02d16" % (timezone.now().year, timezone.now().month)

def getEndBillDay():
	return "%04d%02d31" % (timezone.now().year, timezone.now().month)
	
@app.task
def updatePenaltyCharge():
	billingHistories = BillingHistory.objects.filter(month = '201709').filter(billing_il__isnull = True)
	start_billday = getStartBillDay()
	end_billday = getEndBillDay()
	for billingHistory in billingHistories:
		print billingHistory.academy.name + " : " + str(billingHistory.billing_amount) + " : " + str(plusPenaltyCharge(billingHistory.billing_amount)) 
		billingHistory.billing_amount = plusPenaltyCharge(billingHistory.billing_amount)
		billingHistory.save()

		conn = None
		with connection.cursor() as cursor:
			try:
				for bankcode in BANKCODES:
					field = "bank" + bankcode
					cursor.execute("""UPDATE vacs_vact SET tr_amt = %s, trbegin_il = %s, trend_il = %s WHERE bank_cd = %s AND acct_no = %s;""", (billingHistory.billing_amount, start_billday, end_billday, bankcode, getattr(billingHistory.academy, field)))
			except:
				print "Error Occured"
