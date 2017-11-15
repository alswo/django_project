from django import template
from passenger.models import StudentInfo
from schedule.models import ScheduleTable, EditedScheduleTable

register = template.Library()

@register.filter
def get_academynames(c):
    ret = set()
    try:
        if c.get_cname:
            estables = EditedScheduleTable.objects.filter(ieid = c)
            for estable in estables:
                for sid in estable.slist:
                    student = StudentInfo.objects.get(id = sid)
                    ret.add(student.aid.name)
    except:
	stables = ScheduleTable.objects.filter(iid = c)
        for stable in stables:
            for sid in stable.slist:
	        student = StudentInfo.objects.get(id = sid)
                ret.add(student.aid.name)

    return ret

