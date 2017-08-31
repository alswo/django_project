from passenger.models import Academy
from schedule.models import Branch

def getAcademy(request):
	if request.user.is_active :
		academies = Academy.objects.all().order_by('name')
		branches = Branch.objects.all().order_by('bname')
		displayname = request.session.get('institute', request.user.first_name)
		instituteid = request.session.get('instituteid')
		return {'branches': branches, 'academies' : academies, 'displayname' : displayname,'instituteid' : instituteid, 'age_range': range(5, 20), 'billing_range': range(1, 32), 'month_range': range(1, 13)}

	return {}
