# -*- coding: utf-8 -*-
from passenger.models import Academy
from schedule.models import Branch

class AcademyList :
	def __init__(self):
		self.branches = {}

def getAcademy(request):
	if request.user.is_active :
		academies = Academy.objects.all().order_by('name')
		branches = Branch.objects.all().order_by('bname')
		academyPerBranch = {}
		for branch in branches:
			academyPerBranch[branch.bname] = Academy.objects.filter(bid = branch.id).order_by('name')
		weekdaylist = ['월', '화', '수', '목', '금', '토', '일']
		displayname = request.session.get('institute', request.user.first_name)
		instituteid = request.session.get('instituteid')
		return {'branches': branches, 'academies' : academies, 'displayname' : displayname,'instituteid' : instituteid, 'age_range': range(3, 20), 'weekdaylist': weekdaylist, 'billing_range': range(1, 32), 'month_range': range(1, 13), 'maxvehicle_range': range(1, 10), 'academyPerBranch' : sorted(academyPerBranch.iteritems())}

	return {}
