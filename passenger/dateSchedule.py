#_*_ coding:utf-8 _*_
import time
from datetime import datetime, timedelta

class timeToDate:

    def __init__(self):
        self.t = time.localtime()

    def setTime(self, t):
        self.t = t

    def timeToDmy(self):
        fmt ="%m/%d/%Y"
        dmy = time.strftime(fmt,self.t)

        return dmy

    def timeToYmd(self):
        fmt ="%Y-%m-%d"
        dmy = time.strftime(fmt,self.t)

        return dmy

    def timeToHM(self):
        fmt ="%H:%M"
        dmy = time.strftime(fmt,self.t)

        return dmy

    def timeToHMS(self):
        fmt ="%H:%M:%S"
        dmy = time.strftime(fmt,self.t)

        return dmy

    def timeToRawHM(self):
        fmt ="%H%M"
        dmy = time.strftime(fmt,self.t)

        return dmy

    def timeToRawHMS(self):
        fmt ="%H%M%S"
        dmy = time.strftime(fmt,self.t)

        return dmy


    def timeToD(self):
        d = "%a"
        day = time.strftime(d,self.t)

        if day == "Mon":
            return "월"

        elif day == "Tue":
            return "화"

        elif day == "Wed":
            return "수"

        elif day == "Thu":
            return "목"

        elif day == "Fri":
            return "금"

        elif day == "Sat":
            return "토"

        elif day == "Sun":
            return "일"

        return d

    def timeToStartDayOfWeek(self):
	dt = datetime.fromtimestamp(time.mktime(self.t))
	start = dt - timedelta(days = dt.weekday())
	end = start + timedelta(days=6)

	return start

    def timeToDtype(self,time):
        timeList = time.split("/")
        timeDtype = timeList[2]+"-"+timeList[0]+"-"+timeList[1]

        return timeDtype

    def setDiffTime(self,diff):
        self.t = time.localtime(time.mktime(self.t) + diff);
	return self

    def setLastWeekDay(self):
        self.setDiffTime(-7*24*60*60)
	return self
