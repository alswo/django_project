# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from passenger.models import Academy, StudentInfo, PersonalInfo, BillingHistory
from schedule.models import Branch, HistoryScheduleTable#, Poi, Placement
from util.PhoneNumber import CleanPhoneNumber, FormatPhoneNumber
from util.PersonalInfoUtil import compareLists, saveNewPersonInfo2, findSamePerson
from django.utils import timezone
import datetime
import re
from django.db.models import Min
from django.db import IntegrityError, transaction
import math

def updateAcaAccount():
    bhs = BillingHistory.objects.all()
    for bh in bhs:
        academy = Academy.objects.get(id = bh.academy_id)
        q = academy.name
        a = academy.bank003
        b = academy.bank003
        c = academy.bank003
        d = academy.bank003
        e = academy.bank003
        f = academy.bank003
        g = academy.bank003
        h = academy.bank003
        amount = bh.billing_amount
        print q
        print amount

        try:
                    cursor = connection.cursor()
                    cursor.execute("UPDATE vacs_vact SET tr_amt = %s, trbegin_il = %s, trend_il = %s WHERE acct_no = %s", [amount, '20171011', '20171031', a])
                    cursor.execute("UPDATE vacs_vact SET tr_amt = %s, trbegin_il = %s, trend_il = %s WHERE acct_no = %s", [amount, '20171011', '20171031', b])
                    cursor.execute("UPDATE vacs_vact SET tr_amt = %s, trbegin_il = %s, trend_il = %s WHERE acct_no = %s", [amount, '20171011', '20171031', c])
                    cursor.execute("UPDATE vacs_vact SET tr_amt = %s, trbegin_il = %s, trend_il = %s WHERE acct_no = %s", [amount, '20171011', '20171031', d])
                    cursor.execute("UPDATE vacs_vact SET tr_amt = %s, trbegin_il = %s, trend_il = %s WHERE acct_no = %s", [amount, '20171011', '20171031', e])
                    cursor.execute("UPDATE vacs_vact SET tr_amt = %s, trbegin_il = %s, trend_il = %s WHERE acct_no = %s", [amount, '20171011', '20171031', f])
                    cursor.execute("UPDATE vacs_vact SET tr_amt = %s, trbegin_il = %s, trend_il = %s WHERE acct_no = %s", [amount, '20171011', '20171031', g])
                    cursor.execute("UPDATE vacs_vact SET tr_amt = %s, trbegin_il = %s, trend_il = %s WHERE acct_no = %s", [amount, '20171011', '20171031', h])
                    cursor.close()
                    connection.commit()
                    connection.close()
        except Exception, e:
                    print ("Can't call Insert", e)
