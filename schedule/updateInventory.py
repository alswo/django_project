from schedule.models import Inventory, ScheduleTable, EditedInven, EditedScheduleTable
from passenger.models import Academy, StudentInfo
from schedule.maintainTodayLoad import getTflag

class UpdateInven:
    def __init__(self, bid, carnum, day, req, time, stime, etime, addr, name, name2, load, sid, week,snum,slist_temp3,p_memo,memo):
        self.bid = bid
        self.carnum = carnum
        self.day = day
        self.req = req
        self.time = time
        self.stime = stime
        self.etime = etime
        self.addr = addr
        self.name = name
        self.name2 = name2
        self.load = load
        self.sid = sid
        self.week = week
        #self.alist = alist
        self.snum = snum
        #self.anamelist_inven = anamelist_inven
        self.slist_temp3 = slist_temp3
        self.p_memo = p_memo
        self.memo = memo   
 
    def update_inven(self, iid, unloadSidList):
        inven = Inventory.objects.get(id = iid)
        
        inven.snum = self.snum
        #inven.alist = self.alist
        #inven.anamelist = self.anamelist_inven
        inven.slist = self.slist_temp3
        inven.stime = self.stime
        inven.etime = self.etime
        inven.carnum = self.carnum
        inven.req = self.p_memo
        inven.memo = self.memo
        
        inven.save()

        self.create_stable(iid, unloadSidList)

    def update_edited_inven(self, iid, flag):
        
        if flag == 1:
            edited_inven = EditedInven.objects.get(id = iid)
            inven_id = edited_inven.iid_id
        else:
            inven_id = iid 
            self.week = 1

        if self.week == 1:
            edited_inven_obj = EditedInven.objects.filter(iid_id = inven_id)
        elif self.week == 2:
            edited_inven_obj = EditedInven.objects.filter(iid_id = inven_id).exclude(week = 1)
        else:
            edited_inven_obj = EditedInven.objects.filter(iid_id = inven_id).exclude(week__in = [1,2])

        for ei in edited_inven_obj:
            ei.carnum = self.carnum
            ei.bid = self.bid
            ei.snum = self.snum
            ei.day = self.day
            #ei.alist = self.alist
            #ei.anamelist = self.anamelist_inven
            ei.slist_temp3 = self.slist_temp3
            ei.stime = self.stime
            ei.etime = self.etime
            ei.req = self.p_memo
            ei.memo = self.memo
            ei.save()

            delete_estable = EditedScheduleTable.objects.filter(ieid_id = ei.id)
            delete_estable.delete()

            self.create_edited_stable(ei.id)            

    def create_edited_stable(self,eiid):

        for i in range(len(self.time)):
            if i == 0:
                estable = EditedScheduleTable(ieid_id = eiid, time = self.time[i], addr = self.addr[i], req = self.req[i], slist = '{}', sname= list(self.name2[i]), tflag='{}', lflag = 2)
                estable.save()
            elif i == len(self.time) -1:
                estable = EditedScheduleTable(ieid_id = eiid, time = self.time[i], addr = self.addr[i], req = self.req[i], slist = '{}', sname = list(self.name2[i]), tflag = '{}', lflag = 3)
                estable.save()
            else:
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

                #for aid in temp_aca:
                    #aname = Academy.objects.get(id = aid)
                    #anamelist.append(aname.name)

                estable = EditedScheduleTable(ieid_id = eiid, time = self.time[i], addr = self.addr[i], req = self.req[i], slist=sidlist, sname=temp_name, tflag=temp_tflag, lflag=self.load[i])

                estable.save()

    def create_stable(self, iid, unloadSidList):
        # lflag load -> 1 unload ->0 start -> 2 end -> 3
        for i in range(len(self.time)):
            if i == 0:
                stable = ScheduleTable(iid_id = iid, time = self.time[i], addr = self.addr[i], req = self.req[i], slist='{}', sname=list(self.name2[i]), tflag='{}', lflag=2)
                stable.save()

            elif i == len(self.time) - 1:
                stable = ScheduleTable(iid_id = iid, time = self.time[i], addr = self.addr[i], req = self.req[i], slist='{}', sname=list(self.name2[i]), tflag='{}', lflag=3)
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

                temp_tflag = getTflag(sidlist,unloadSidList)

                anamelist = []

                for aid in temp_aca:
                    aname = Academy.objects.get(id = aid)
                    anamelist.append(aname.name)

                stable = ScheduleTable(iid_id = iid, time = self.time[i], addr = self.addr[i], req = self.req[i], slist=sidlist, sname=temp_name, tflag=temp_tflag, lflag=self.load[i])
                stable.save()


