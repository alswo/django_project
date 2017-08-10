from django.shortcuts import render_to_response, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from passenger.models import Academy, StudentInfo
import re

# Create your views here.

class BeautifyStudent :
	def __init__(self):
		self.info = ''
		self.phonenumber = ''

def beautify_phonenumber(number):
	str_number = str(number)
	return re.sub(r'^(\d{2})(\d+)(\d{4})$', r'0\1-\2-\3', str_number)

@login_required
def setSession(request):
	instituteid = request.GET.get('instituteid')
	try:
		request.session['instituteid'] = int(instituteid)
		request.session['institute'] = Academy.objects.get(id = instituteid).name
	except Academy.DoesNotExist:
		del request.session['institute']
		del request.session['instituteid']

	return HttpResponse(request.session.get('institute', None))

@login_required
def listStudents(request):
	if request.user.is_staff :
		institute = request.session.get('institute', None)
	else :
		institute = request.user.first_name

	if institute:
		academy = Academy.objects.get(name = institute)
		students = StudentInfo.objects.filter(aid__contains = [academy.id]).order_by('sname')
	else:
		students = StudentInfo.objects.all().order_by('sname')

	beautifyStudents = []
	for student in students:
		beautifyStudent = BeautifyStudent()
		beautifyStudent.info = student
		beautifyStudent.phonenumber  = beautify_phonenumber(student.phone1)
		beautifyStudents.append(beautifyStudent)

	return render(request, 'listStudents.html', {'students': beautifyStudents});

@login_required
def addStudentsForm(request):
	return render(request, 'addStudentsForm.html', {'age_range': range(5, 16), 'billing_range': range(1, 31)})

@csrf_exempt
@login_required
def addStudents(request):
	if request.user.is_staff :
		institute = request.GET.get('institute')
	else :
		institute = request.user.first_name

	academy = Academy.objects.filter(name = institute)

	sname = request.POST.get('sname')
	age = request.POST.get('age')
	phonenumbers = request.POST.getlist('phone[]')

	return HttpResponse(len(phonenumbers))

@login_required
def addClassForm(request):
	return render(request, 'addClassForm.html')

