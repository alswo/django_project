# day = request.POST.getlist('day[]')
# carnum = request.POST.get('carnum')
# bid = request.POST.get('bid')
# req = request.POST.get('req')
# time = request.POST.getlist('time[]')
# addr = request.POST.getlist('addr[]')
# name = request.POST.getlist('name[]')
# academy = request.POST.getlist('academy[]')
# load = request.POST.getlist('load[]')
# sid = request.POST.getlist('sid[]')
# week = int(request.POST.get('week'))
from schedule.models import Inventory, ScheduleTable, EditedInven, EditedScheduleTable
from passenger.models import Academy

class UpdateInven:
    def __init__(self,bid,carnum,day,req,academy,time,addr,name,name2,load,sid,week):
        self.bid = bid
        self.carnum = carnum
        self.day = day
        self.req = req
        self.academy = academy
        self.time = time
        self.addr = addr
        self.name = name
        self.name2 = name2
        self.load = load
        self.sid = sid
        self.week = week

    def setAlist(self):

        try:
            alist_temp = list(set([i for i in self.academy if i is not None and i != '']))
            alist_temp2 = ','.join(alist_temp)
            alist_temp3 = list(set(alist_temp2.split(',')))
            alist = []

            for a in alist_temp3:
                alist.append(int(a))

            self.alist = alist

        except:
            return(1)

    def setSlist(self):

        try:
            slist_temp = list(set([i for i in self.sid if i is not None and i != '']))
            slist_temp2 = ','.join(slist_temp)
            slist_temp3 = list(set(slist_temp2.split(',')))
            slist = []

            for s in slist_temp3:
                slist.append(int(s))

            snum = len(slist)

            self.slist = slist
            self.snum = snum

        except:
            return(1)

    def setANameList(self):
        try:
            academyList = Academy.objects.filter(id__in = self.alist)
            anamelist_inven = []

            for a in academyList:
                anamelist_inven.append(a.name)

            self.anamelist_inven = anamelist_inven

        except:
            return(1)

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
            inven = Inventory.objects.create(carnum = self.carnum, bid = self.bid, snum = self.snum, day = d , alist=self.alist, anamelist = self.anamelist_inven, slist=self.slist, stime = self.stime, etime = self.etime, req=self.req, week1 = 0, week2 = 0, week3 = 0)

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
                    temp_aca = [a.strip() for a in self.academy[i].split(',')]
                    temp_name = [n.strip() for n in self.name2[i].split(',')]
                    sidlist = [s.strip() for s in self.sid[i].split(',')]

                    temp_lflag = [0 for z in range(len(temp_name))]

                    anamelist = []

                    for aid in temp_aca:
                        aname = Academy.objects.get(id = aid)
                        anamelist.append(aname.name)

                    stable = ScheduleTable(iid_id = iid, time = self.time[i], addr = self.addr[i], alist = temp_aca, anamelist = anamelist, slist = sidlist, sname = temp_name, tflag = temp_lflag, lflag = self.load[i])
                    stable.save()

    def setWeek1(self):
        for j in range(3):
            for d in self.day:
                ei = EditedInven(carnum = self.carnum, bid = self.bid, snum = self.snum, day = d, alist = self.alist, anamelist = self.anamelist_inven, slist = self.slist, stime = self.stime, etime = self.etime, req = self.req, week = j+1)
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
                        temp_aca = [a.strip() for a in self.academy[i].split(',')]
                        temp_name = [n.strip() for n in self.name2[i].split(',')]
                        sidlist = [s.strip() for s in self.sid[i].split(',')]

                        temp_lflag = [0 for z in range(len(temp_name))]

                        anamelist = []

                        for aid in temp_aca:
                            aname = Academy.objects.get(id = aid)
                            anamelist.append(aname.name)

                        estable = EditedScheduleTable(ieid_id = eiid, time = self.time[i], addr = self.addr[i], alist = temp_aca, anamelist = anamelist, slist = sidlist, sname = temp_name, tflag = temp_lflag, lflag = self.load[i])
                        estable.save()

    def setWeek2(self):
        for j in range(2):
            for d in self.day:
                ei = EditedInven(carnum = self.carnum, bid = self.bid, snum = self.snum, day = d, alist = self.alist, anamelist = self.anamelist_inven, slist = self.slist, stime = self.stime, etime = self.etime, req = self.req, week = j+1)
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
                        temp_aca = [a.strip() for a in self.academy[i].split(',')]
                        temp_name = [n.strip() for n in self.name2[i].split(',')]
                        sidlist = [s.strip() for s in self.sid[i].split(',')]

                        temp_lflag = [0 for z in range(len(temp_name))]

                        anamelist = []

                        for aid in temp_aca:
                            aname = Academy.objects.get(id = aid)
                            anamelist.append(aname.name)

                        estable = EditedScheduleTable(ieid_id = eiid, time = self.time[i], addr = self.addr[i], alist = temp_aca, anamelist = anamelist, slist = sidlist, sname = temp_name, tflag = temp_lflag, lflag = self.load[i])
                        estable.save()

    def setWeek3(self):
        for d in self.day:
            ei = EditedInven(carnum = self.carnum, bid = self.bid, snum = self.snum, day = d, alist = self.alist, anamelist = self.anamelist_inven, slist = self.slist, stime = self.stime, etime = self.etime, req = self.req, week = week)
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
                    temp_aca = [a.strip() for a in self.academy[i].split(',')]
                    temp_name = [n.strip() for n in self.name2[i].split(',')]
                    sidlist = [s.strip() for s in self.sid[i].split(',')]

                    temp_lflag = [0 for z in range(len(temp_name))]

                    anamelist = []

                    for aid in temp_aca:
                        aname = Academy.objects.get(id = aid)
                        anamelist.append(aname.name)

                    estable = EditedScheduleTable(ieid_id = eiid, time = self.time[i], addr = self.addr[i], alist = temp_aca, anamelist = anamelist, slist = sidlist, sname = temp_name, tflag = temp_lflag, lflag = self.load[i])
                    estable.save()
