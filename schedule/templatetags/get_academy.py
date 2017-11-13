from django import template
from passenger.models import StudentInfo
from schedule.models import ScheduleTable

register = template.Library()

@register.filter
def get_academynames(inventory):
	ret = set()
	stables = ScheduleTable.objects.filter(iid = inventory)
	for stable in stables:
		for sid in stable.slist:
			student = StudentInfo.objects.get(id = sid)
			ret.add(student.aid.name)

	return ret
