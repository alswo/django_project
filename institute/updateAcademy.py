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

def updateAcademy(request):
    academy = Academy.objects.all()
    cursor = connection.cursor()
    for a in academy:
        if a.bank003 == '0':
            try:
                cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['03','0'])
                giup = cursor.fetchone()
                cursor.execute("UPDATE vacs_vact SET acct_st = %s WHERE acct_no = %s", ['1',giup[0].strip()])
            except Exception, e:
                print ("Can't call Insert", e)

            a.bank003 = giup[0].strip()

        if a.bank004 == '0':
            try:
                cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['04','0'])
                gukmin = cursor.fetchone()
                cursor.execute("UPDATE vacs_vact SET acct_st = %s WHERE acct_no = %s", ['1',gukmin[0].strip()])
            except Exception, e:
                print ("Can't call Insert", e)

            a.bank004 = gukmin[0].strip()

        if a.bank011 == '0':
            try:
                cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['11','0'])
                nonghyup = cursor.fetchone()
                cursor.execute("UPDATE vacs_vact SET acct_st = %s WHERE acct_no = %s", ['1',nonghyup[0].strip()])
            except Exception, e:
                print ("Can't call Insert", e)

            a.bank011 = nonghyup[0].strip()

        if a.bank020 == '0':
            try:
                cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['20','0'])
                woori = cursor.fetchone()
                cursor.execute("UPDATE vacs_vact SET acct_st = %s WHERE acct_no = %s", ['1',woori[0].strip()])
            except Exception, e:
                print ("Can't call Insert", e)

            a.bank020 = woori[0].strip()

        if a.bank027 == '0':
            try:
                cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['27','0'])
                city = cursor.fetchone()
                cursor.execute("UPDATE vacs_vact SET acct_st = %s WHERE acct_no = %s", ['1',city[0].strip()])
            except Exception, e:
                print ("Can't call Insert", e)

            a.bank027 = city[0].strip()

        if a.bank071 == '0':
            try:
                cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['71','0'])
                woochegook = cursor.fetchone()
                cursor.execute("UPDATE vacs_vact SET acct_st = %s WHERE acct_no = %s", ['1',woochegook[0].strip()])
            except Exception, e:
                print ("Can't call Insert", e)

            a.bank071 = woochegook[0].strip()

        if a.bank081 == '0':
            try:
                cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['81','0'])
                hana = cursor.fetchone()
                cursor.execute("UPDATE vacs_vact SET acct_st = %s WHERE acct_no = %s", ['1',hana[0].strip()])
            except Exception, e:
                print ("Can't call Insert", e)

            a.bank081 = hana[0].strip()

        if a.bank088 == '0':
            try:
                cursor.execute("SELECT acct_no  FROM vacs_vact WHERE bank_cd = %s AND acct_st = %s", ['88','0'])
                shinhan = cursor.fetchone()
                cursor.execute("UPDATE vacs_vact SET acct_st = %s WHERE acct_no = %s", ['1',shinhan[0].strip()])
            except Exception, e:
                print ("Can't call Insert", e)

            a.bank088 = shinhan[0].strip()
        cursor.close()
        connection.commit()
        connection.close()
        a.save()
