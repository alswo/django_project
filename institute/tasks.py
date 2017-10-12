#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from tayo.celery import app
from passenger.models import BillingHistory, Academy
from django.db import connection
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
		print b.academy_id.name
		academys = Academy.objects.filter(id = b.academy_id)
		for a in academys:
			cursor = connection.cursor()
			cursor.execute("SELECT iacct_no FROM vacs_ahst;")
			iacct_nos = cursor.fetchall()

			for acct_no in iacct_nos:
				acct = u"%s" % acct_no
				acct = acct.strip()
				if a.bank003 == acct:
					cursor = connection.cursor()
					cursor.execute("SELECT tr_il FROM vacs_ahst WHERE iacct_no = %s" , [acct])
					tr_il = cursor.fetchone()
					tr_il = u"%s" % tr_il
					bank_cd = "기업은행"
					cursor.execute("UPDATE passenger_billinghistory SET billing_il = %s, billing_bank = %s WHERE academy_id = %s", [tr_il, bank_cd, a.id])
					cursor.close()
					connection.commit()
					connection.close()

				elif a.bank004 == acct:
					cursor = connection.cursor()
					cursor.execute("SELECT tr_il FROM vacs_ahst WHERE iacct_no = %s" , [acct])
					tr_il = cursor.fetchone()
					tr_il = u"%s" % tr_i
					bank_cd = "국민은행"
					cursor.execute("UPDATE passenger_billinghistory SET billing_il = %s, billing_bank = %s WHERE academy_id = %s", [tr_il, bank_cd, a.id])
					cursor.close()
					connection.commit()
					connection.close()

				elif a.bank011 == acct:
					cursor = connection.cursor()
					cursor.execute("SELECT tr_il FROM vacs_ahst WHERE iacct_no = %s" , [acct])
					tr_il = cursor.fetchone()
					tr_il = u"%s" % tr_il
					bank_cd = "농협은행"
					cursor.execute("UPDATE passenger_billinghistory SET billing_il = %s, billing_bank = %s WHERE academy_id = %s", [tr_il, bank_cd, a.id])
					cursor.close()
					connection.commit()
					connection.close()

				elif a.bank020 == acct:
					cursor = connection.cursor()
					cursor.execute("SELECT tr_il FROM vacs_ahst WHERE iacct_no = %s" , [acct])
					tr_il = cursor.fetchone()
					tr_il = u"%s" % tr_il
					bank_cd = "우리은행"
					cursor.execute("UPDATE passenger_billinghistory SET billing_il = %s, billing_bank = %s WHERE academy_id = %s", [tr_il, bank_cd, a.id])
					cursor.close()
					connection.commit()
					connection.close()

				elif a.bank027 == acct:
					cursor.execute("SELECT tr_il FROM vacs_ahst WHERE iacct_no = %s" , [acct])
					tr_il = cursor.fetchone()
					tr_il = u"%s" % tr_il
					bank_cd = "시티은행"
					cursor.execute("UPDATE passenger_billinghistory SET billing_il = %s, billing_bank = %s WHERE academy_id = %s", [tr_il, bank_cd, a.id])
					cursor.close()
					connection.commit()
					connection.close()

				elif a.bank071 == acct:
					cursor = connection.cursor()
					cursor.execute("SELECT tr_il FROM vacs_ahst WHERE iacct_no = %s" , [acct])
					tr_il = cursor.fetchone()
					tr_il = u"%s" % tr_il
					bank_cd = "우체국은행"
					cursor.close()
					connection.commit()
					connection.close()

				elif a.bank081 == acct:
					cursor = connection.cursor()
					cursor.execute("SELECT tr_il FROM vacs_ahst WHERE iacct_no = %s" , [acct])
					tr_il = cursor.fetchone()
					tr_il = u"%s" % tr_il
					bank_cd = "하나은행"
					cursor.execute("UPDATE passenger_billinghistory SET billing_il = %s, billing_bank = %s WHERE academy_id = %s", [tr_il, bank_cd, a.id])
					cursor.close()
					connection.commit()
					connection.close()

				elif a.bank088 == acct:
					cursor = connection.cursor()
					cursor.execute("SELECT tr_il FROM vacs_ahst WHERE iacct_no = %s" , [acct])
					tr_il = cursor.fetchone()
					tr_il = u"%s" % tr_il
					bank_cd = "신한은행"
					cursor.execute("UPDATE passenger_billinghistory SET billing_il = %s, billing_bank = %s WHERE academy_id = %s", [tr_il, bank_cd, a.id])
					cursor.close()
					connection.commit()
					connection.close()

				else:
					print "noting"
