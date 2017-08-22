from schedule.models import ScheduleTable

def getUnloadSid(iid):
    sTable = ScheduleTable.objects.filter(iid_id = iid)
    sList = []
    tList = []
    
    for st in sTable:
        sList.extend(st.slist)
        tList.extend(st.tflag)

    indexOfTload = []    
    
    for idx, t in enumerate(tList):
        if t == 1:
            indexOfTload.append(idx)

    unloadSid = []

    for i in indexOfTload:
        unloadSid.append(sList[i])

    return unloadSid

def getTflag(sidlist, unloadSidList):  

    temp_tflag = [0] * len(sidlist)    

    for idx,sid in enumerate(sidlist):
        for unloadSid in unloadSidList:
            if unloadSid == int(sid):
                temp_tflag[idx] = 1
    
    return temp_tflag
