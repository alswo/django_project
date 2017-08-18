from passenger.models import Academy

def getAcademy(request):
	if request.user.is_active :
		academies = Academy.objects.all().order_by('name')
		displayname = request.session.get('institute', request.user.first_name)
		return {'academies' : academies, 'displayname' : displayname, 'age_range': range(5, 16), 'billing_range': range(1, 32), 'month_range': range(1, 13)}

	return {}
