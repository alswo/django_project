#!/usr/bin/python
# -*- coding: utf-8 -*-
from passenger.models import StudentInfo, PersonalInfo
from passenger.dateSchedule import timeToDate
from fcmdev.models import PropOfDevice
from fcm_django.models import FCMDevice
from schedule.models import Inventory, ScheduleTable
from collections import Counter
import sys
import requests
import simplejson
import ast
reload(sys)
sys.setdefaultencoding('utf-8')
#
#
# def check():
#     time = timeToDate()
#     date = time.timeToD()
#     i = 0
#     scheduleTables = []
#     schedules = []
#     inventorys = Inventory.objects.filter(day = date).prefetch_related('scheduletables').reverse()
#     for inventory in inventorys:
#         scheduletables = ScheduleTable.objects.filter(iid = 2956)
#         for scheduletable in scheduletables:
#             schedules.extend(scheduletable.slist)
#
#     for inventory in inventorys:
#         scheduleTables.extend(inventory.scheduletables.all())
#
#     count_slist = []
#
#     for schTable in scheduleTables:
#         if len(schTable.slist) >= 1:
#             count_slist.extend(schTable.slist)
#
#     dict_slist = dict(Counter(count_slist))
#
#     push_content = []
#
#     msg_count = 0
#     error_count = 0
#     for key, value in dict_slist.iteritems():
#         for schTable in scheduleTables:
#             if len(schTable.slist) >= 1:
#                 while(key in schTable.slist):
#                     try:
#                         sInfo = StudentInfo.objects.get(id=key)
#                     except StudentInfo.DoesNotExist:
#                         sInfo = None
#                         break
#                     else:
# 			try:
#
# 				pin = PersonalInfo.objects.get(id = sInfo.personinfo_id)
# 	                        module_push_content = {}
# 				# 안타요를 누른 학생에대해서 메시지 필터링.
# 				temp_tflag = schTable.tflag
# 				offset_list = schTable.slist
# 				temp_index = offset_list.index(sInfo.id)
# 				module_push_content['tflag'] = temp_tflag[temp_index]
#                                 module_push_content['id'] =schTable.id
# 				module_push_content['sname'] = sInfo.sname
# 	                        module_push_content['time'] = schTable.time
# 	                        module_push_content['addr'] = schTable.addr
# 		                module_push_content['lflag'] = schTable.lflag
# 	                        module_push_content['aname'] = sInfo.aname
# 	                        module_push_content['pin'] = pin.pin_number
# 	                        module_push_content['sid'] = key
# 	                        module_push_content['count'] = value
#
# 	                        push_content.append(module_push_content)
# 	                        break
# 			except PersonalInfo.DoesNotExist:
# 			        break
#
#
#
#         sctid = module_push_content['id']
#         count = module_push_content['count']-1
# 	lflag = module_push_content['lflag']
# 	sname = module_push_content['sname']
#         tflag = module_push_content['tflag']
#         if lflag == 0:
#             flag = "하원을 위한"
#
# 	elif lflag == 1:
# 	    flag = "등원을 위한"
# 	else:
# 	    flag = "에 대한"
#         if count == 0:
# 	    i += 1
#             msg = "오늘 " + sname + " 학생의 " + module_push_content['aname'] + " " + flag + " " + module_push_content['time'] + " [" + module_push_content['addr'] + "] 승차 스케줄이 있습니다"
#
# 	    # if tflag == 1:
#         #         print sctid
# 	    # 	print sname+"안타요"
# 	    # elif tflag == 0:
# 	    #     print sctid
#         #         print sname+"타요"
#         else:
# 	    i += 1
#             msg = "오늘 " + sname + " 학생의 " + module_push_content['aname'] + " 등원을 위한 " + module_push_content['time'] + " [" + module_push_content['addr'] + "]승차 외" + str(count) + "건의 스케줄이 있습니다."
#
#     print i
#
#
# def check2():
#     scheduletables = ScheduleTable.objects.filter(iid = 2956)
#     for sc in scheduletables:
#         for slist in sc.slist:
#             sInfo = StudentInfo.objects.get(id=1592)
#
#         # temp_tflag = sc.tflag
#         # offset_list = sc.slist
#         # temp_index = offset_list.index(sInfo.id)


def tt():
    time = timeToDate()
    date = time.timeToD()
    i = 0
    scheduleTables = []
    schedules = []
    inventorys = Inventory.objects.filter(day = date).prefetch_related('scheduletables').reverse()
    for inventory in inventorys:
        scheduletables = ScheduleTable.objects.filter(iid = inventory.id)
        for scheduletable in scheduletables:
            schedules.extend(scheduletable.slist)

    for inventory in inventorys:
        scheduleTables.extend(inventory.scheduletables.all())

    count_slist = []

    for schTable in scheduleTables:
        if len(schTable.slist) >= 1:
            count_slist.extend(schTable.slist)

    dict_slist = dict(Counter(count_slist))

    push_content = []

    msg_count = 0
    error_count = 0
    for key, value in dict_slist.iteritems():
        for schTable in scheduleTables:
            if len(schTable.slist) >= 1:
                while(key in schTable.slist):
                    try:
                        sInfo = StudentInfo.objects.get(id=key)
                    except StudentInfo.DoesNotExist:
                        sInfo = None
                        break
                    else:
			try:

				pin = PersonalInfo.objects.get(id = sInfo.personinfo_id)
	                        module_push_content = {}
				# 안타요를 누른 학생에대해서 메시지 필터링.
				# temp_tflag = schTable.tflag
				# offset_list = schTable.slist
				# temp_index = offset_list.index(sInfo.id)
				# module_push_content['tflag'] = temp_tflag[temp_index]
                #                 module_push_content['id'] =schTable.id
				module_push_content['sname'] = sInfo.sname
	                        module_push_content['time'] = schTable.time
	                        module_push_content['addr'] = schTable.addr
		                module_push_content['lflag'] = schTable.lflag
	                        module_push_content['aname'] = sInfo.aname
	                        module_push_content['pin'] = pin.pin_number
	                        module_push_content['sid'] = key
	                        module_push_content['count'] = value

	                        push_content.append(module_push_content)
	                        break
			except PersonalInfo.DoesNotExist:
			        break



        sctid = module_push_content['id']
        count = module_push_content['count']-1
        # tflag = module_push_content['tflag']
	lflag = module_push_content['lflag']
	sname = module_push_content['sname']
        # if tflag == '1':
        #     count = count - 1
        if lflag == 0:
            flag = "하원을 위한"

	elif lflag == 1:
	    flag = "등원을 위한"
	else:
	    flag = "에 대한"
        if count == 0:
            msg = "오늘 " + sname + " 학생의 " + module_push_content['aname'] + " " + flag + " " + module_push_content['time'] + " [" + module_push_content['addr'] + "] 승차 스케줄이 있습니다"


            #send_msg(module_push_content['sid'], module_push_content['pin'], msg)
	    # if tflag == 1:
        #         print msg
	    # 	print sname+"안타요"
        #
        #     elif tflag == 0:
	    #     pass

        elif count > 0:
            msg = "오늘 " + sname + " 학생의 " + module_push_content['aname'] + " 등원을 위한 " + module_push_content['time'] + " [" + module_push_content['addr'] + "]승차 외" + str(count) + "건의 스케줄이 있습니다."
            print msg

           # send_msg(module_push_content['sid'], module_push_content['pin'], msg)
            # if tflag == 1:
            #     print msg
            #     print sname+"안타요"
            # elif tflag == 0:
            #     pass
