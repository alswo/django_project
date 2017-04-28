from passenger.models import ShuttleSchedule,ScheduleDate
from passenger.dateSchedule import timeToDate

def main():
    t = timeToDate()
    dmy = t.timeToDmy()
    d = t.timeToD()

    sschedule = ShuttleSchedule.objects.filter(day=d)

    for s in sschedule:
        ds = ScheduleDate(a_name = s.a_name, day = s.day, time = s.time,schedule = s.schedule, gid = s.gid, aid = s.aid, \
slist = s.slist,p_schedule = s.p_schedule, alist = s.alist, memo = s.memo, date = dmy)

        ds.save()
