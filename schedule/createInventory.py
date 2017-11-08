from schedule.models import Inventory, ScheduleTable, EditedInven, EditedScheduleTable
from passenger.models import Academy, StudentInfo
from schedule.maintainTodayLoad import getTflag 

class CreateInven:
    def __init__(self,bid,carnum,day,req,time,addr,name,name2,load,sid,week,alist):
        self.bid = bid
        self.carnum = carnum
        self.day = day
        self.req = req
        self.time = time
        self.addr = addr
        self.name = name
        self.name2 = name2
        self.load = load
        self.sid = sid
        self.week = week
        #self.alist = alist

    #def setAlist(self):
        #if self.alist == 0:
            #slist_temp = list(set([i for i in self.sid if i is not None and i != '']))
            #slist_temp2 = ','.join(slist_temp)
            #slist_temp3 = list(set(slist_temp2.split(',')))
            #slist = []
 #
            #for s in slist_temp3:
                ##slist.append(int(s))
#
            #slist_temp3 = slist
            #academy = StudentInfo.objects.filter(id__in = slist_temp3)
            #self.alist = [a.aid_id for a in academy]
            #
        #else:
            #self.alist = self.alist

    def setSlist(self):
        try:
            slist_temp = list(set([i for i in self.sid if i is not None and i != '']))
            slist_temp2 = ','.join(slist_temp)
            slist_temp3 = list(set(slist_temp2.split(',')))

            try:
                slist = []
                
                for s in slist_temp3:
                    slist.append(int(s))

                snum = len(slist)

                self.slist = slist
                self.snum = snum

            except:
                self.slist = [0]
                self.snum = 0

        except:
            return(1)

    #def setANameList(self):
        #try:
            #academyList = Academy.objects.filter(id__in = self.alist)
            #anamelist_inven = []
#
            #for a in academyList:
                #anamelist_inven.append(a.name)
#
            #self.anamelist_inven = anamelist_inven

        #except:
            #return(1)

    def setSEtime(self):
        try:
            stime = int(self.time[0].split(':')[0] + self.time[0].split(':')[1])
            etime = int(self.time[-1].split(':')[0] + self.time[-1].split(':')[1])

            self.stime = stime
            self.etime = etime

        except:
            return(1)

    def setWeek0(self):
        for d in self.day:
            inven = Inventory.objects.create(carnum = self.carnum, bid = self.bid, snum = self.snum, day = d , alist=self.alist, anamelist = self.anamelist_inven, slist=self.slist, stime = self.stime, etime = self.etime, req = self.req, week1 = 0, week2 = 0, week3 = 0)

            iid = inven.id

            # lflag load -> 1 unload ->0 start -> 2 end -> 3
            for i in range(len(self.time)):
                if i == 0:
                    stable = ScheduleTable(iid_id = iid, time = self.time[i], addr = self.addr[i], alist='{}', slist='{}', sname=list(self.name2[i]), tflag='{}', lflag=2)
                    stable.save()

                elif i == len(self.time) - 1:
                    stable = ScheduleTable(iid_id = iid, time = self.time[i], addr = self.addr[i], alist='{}', slist='{}', sname=list(self.name2[i]), tflag='{}', lflag=3)
                    stable.save()

                elif 0 < i < len(self.time) - 1:
                    try:
                        academy = StudentInfo.objects.filter(id__in = [int(s) for s in self.sid[i].split(',')])
                        temp_aca = [a.aid_id for a in academy]
                        temp_name = [n.strip() for n in self.name2[i].split(',')]
                        sidlist = [s.strip() for s in self.sid[i].split(',')]

                    except:
                        temp_aca = []
                        temp_name = []
                        sidlist = []
                        temp_aca = filter(None, temp_aca)
                        temp_name = filter(None, temp_name)
                        sidlist = filter(None, sidlist)
                        
                    temp_tflag = [0 for z in range(len(temp_name))]
                     
                    anamelist = []

                    for aid in temp_aca:
                        aname = Academy.objects.get(id = aid)
                        anamelist.append(aname.name)

                    stable = ScheduleTable(iid_id = iid, time = self.time[i], addr = self.addr[i], alist = temp_aca, anamelist = anamelist, slist = sidlist, sname = temp_name, tflag = temp_tflag, lflag = self.load[i])
                    stable.save()

    def setWeek1(self, unloadSidList = 0, iid = -1):
        #called by putSchedule
        if iid == -1:
            inven = Inventory.objects.create(carnum = 0, bid = 0, snum = 0, day = 'fake', alist = '{}', slist = '{}',anamelist='{}', etime = 0, stime = 0, req = self.req, week1 = 1, week2 = 1, week3 = 1)
            iid = inven.id 
        #called by updateSchedule week0
        else:
            iid = iid
            Inventory.objects.filter(id = iid).update(week1 = 1, week2 = 1, week3 = 1) 
        
        for j in range(3):
            for d in self.day:
                ei = EditedInven(iid_id = iid, carnum = self.carnum, bid = self.bid, snum = self.snum, day = d, alist = self.alist, anamelist = self.anamelist_inven, slist = self.slist, stime = self.stime, etime = self.etime,  week = j+1)
                ei.save()
                eiid = ei.id

                # lflag load -> 1 unload ->0 start -> 2 end -> 3
                for i in range(len(self.time)):
                    if i == 0:
                        estable = EditedScheduleTable(ieid_id = eiid, time = self.time[i], addr = self.addr[i], alist='{}', slist='{}', sname=list(self.name2[i]), tflag='{}', lflag=2)
                        estable.save()

                    elif i == len(self.time) - 1:
                        estable = EditedScheduleTable(ieid_id = eiid, time = self.time[i], addr = self.addr[i], alist='{}', slist='{}', sname=list(self.name2[i]), tflag='{}', lflag=3)
                        estable.save()

                    elif 0 < i < len(self.time) - 1:
                        try:
                            academy = StudentInfo.objects.filter(id__in = [int(s) for s in self.sid[i].split(',')])
                            temp_aca = [a.aid_id for a in academy]
                            temp_name = [n.strip() for n in self.name2[i].split(',')]
                            sidlist = [s.strip() for s in self.sid[i].split(',')]

                        except:
                            temp_aca = []
                            temp_name = []
                            sidlist = []
                            temp_aca = filter(None, temp_aca)
                            temp_name = filter(None, temp_name)
                            sidlist = filter(None, sidlist)

                        temp_tflag = [0]*len(sidlist)
                        
                        anamelist = []

                        for aid in temp_aca:
                            aname = Academy.objects.get(id = aid)
                            anamelist.append(aname.name)

                        estable = EditedScheduleTable(ieid_id = eiid, time = self.time[i], addr = self.addr[i], alist = temp_aca, anamelist = anamelist, slist = sidlist, sname = temp_name, tflag = temp_tflag, lflag = self.load[i])
                        estable.save()

    def setWeek2(self):
        inven = Inventory.objects.create(carnum = 0, bid = 0, snum = 0, day = 'fake', alist = '{}', slist = '{}',anamelist='{}', etime = 0, stime = 0, req = self.req, week1 = 0, week2 = 1, week3 = 1)
 
        for j in range(2):
            for d in self.day:
                ei = EditedInven(iid_id = inven.id, carnum = self.carnum, bid = self.bid, snum = self.snum, day = d, alist = self.alist, anamelist = self.anamelist_inven, slist = self.slist, stime = self.stime, etime = self.etime, week = j+1)
                ei.save()
                eiid = ei.id

                # lflag load -> 1 unload ->0 start -> 2 end -> 3
                for i in range(len(self.time)):
                    if i == 0:
                        estable = EditedScheduleTable(ieid_id = eiid, time = self.time[i], addr = self.addr[i], alist='{}', slist='{}', sname=list(self.name2[i]), tflag='{}', lflag=2)
                        estable.save()

                    elif i == len(self.time) - 1:
                        estable = EditedScheduleTable(ieid_id = eiid, time = self.time[i], addr = self.addr[i], alist='{}', slist='{}', sname=list(self.name2[i]), tflag='{}', lflag=3)
                        estable.save()

                    elif 0 < i < len(self.time) - 1:
                        try:
                            academy = StudentInfo.objects.filter(id__in = [int(s) for s in self.sid[i].split(',')])
                            temp_aca = [a.aid_id for a in academy]
                            temp_name = [n.strip() for n in self.name2[i].split(',')]
                            sidlist = [s.strip() for s in self.sid[i].split(',')]

                        except:
                            temp_aca = []
                            temp_name = []
                            sidlist = []
                            temp_aca = filter(None, temp_aca)
                            temp_name = filter(None, temp_name)
                            sidlist = filter(None, sidlist)

                        temp_tflag = [0]*len(sidlist)

                        anamelist = []

                        for aid in temp_aca:
                            aname = Academy.objects.get(id = aid)
                            anamelist.append(aname.name)

                        estable = EditedScheduleTable(ieid_id = eiid, time = self.time[i], addr = self.addr[i], alist = temp_aca, anamelist = anamelist, slist = sidlist, sname = temp_name, tflag = temp_tflag, lflag = self.load[i])
                        estable.save()

    def setWeek3(self):
        inven = Inventory.objects.create(carnum = 0, bid = 0, snum = 0, day = 'fake', alist = '{}', slist = '{}',anamelist='{}', etime = 0, stime = 0, req = self.req, week1 = 0, week2 = 0, week3 = 1)
        
        for d in self.day:
            ei = EditedInven(iid_id = inven.id, carnum = self.carnum, bid = self.bid, snum = self.snum, day = d, alist = self.alist, anamelist = self.anamelist_inven, slist = self.slist, stime = self.stime, etime = self.etime, week = self.week)
            ei.save()
            eiid = ei.id

            # lflag load -> 1 unload ->0 start -> 2 end -> 3
            for i in range(len(self.time)):
                if i == 0:
                    estable = EditedScheduleTable(ieid_id = eiid, time = self.time[i], addr = self.addr[i], alist='{}', slist='{}', sname=list(self.name2[i]), tflag='{}', lflag=2)
                    estable.save()

                elif i == len(self.time) - 1:
                    estable = EditedScheduleTable(ieid_id = eiid, time = self.time[i], addr = self.addr[i], alist='{}', slist='{}', sname=list(self.name2[i]), tflag='{}', lflag=3)
                    estable.save()

                elif 0 < i < len(self.time) - 1:
                    try:
                        academy = StudentInfo.objects.filter(id__in = [int(s) for s in self.sid[i].split(',')])
                        temp_aca = [a.aid_id for a in academy]
                        temp_name = [n.strip() for n in self.name2[i].split(',')]
                        sidlist = [s.strip() for s in self.sid[i].split(',')]

                    except:
                        temp_aca = []
                        temp_name = []
                        sidlist = []
                        temp_aca = filter(None, temp_aca)
                        temp_name = filter(None, temp_name)
                        sidlist = filter(None, sidlist)
                    
                    temp_tflag = [0]*len(sidlist)

                    anamelist = []

                    for aid in temp_aca:
                        aname = Academy.objects.get(id = aid)
                        anamelist.append(aname.name)

                    estable = EditedScheduleTable(ieid_id = eiid, time = self.time[i], addr = self.addr[i], alist = temp_aca, anamelist = anamelist, slist = sidlist, sname = temp_name, tflag = temp_tflag, lflag = self.load[i])
                    estable.save()
