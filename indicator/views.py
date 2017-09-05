# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.db.models import F, Sum
from indicator.models import ShuttleIndicator
from schedule.models import Car, Area

class ChartData:
	def __init__(self):
		self.date = ""
		self.num = 0
		

# Create your views here.
def shuttleIndicator(request):
	if request.method == 'GET':
		mode = request.GET.get('mode', 'every')
		area = request.GET.get('area')

	areas = Area.objects.all()

	carChartData = {}
	
	if (mode == 'group'):
		shuttleIndicators = ShuttleIndicator.objects.values('car__branchid__areaid__name', 'date').annotate(num = Sum('dayScheduleTableNum'), name = F('car__branchid__areaid__name'))
	else:
		if (area != None):
			shIndicators = ShuttleIndicator.objects.filter(car__branchid__areaid_id = int(area))
		else:
			shIndicators = ShuttleIndicator.objects.all()
		shuttleIndicators = shIndicators.values('date').annotate(num = F('dayscheduletablenum'), name = F('car__carname'))

	for shuttleIndicator in shuttleIndicators:
		chartData = ChartData()
		chartData.date = shuttleIndicator['date']
		chartData.num = shuttleIndicator['num']
		if (not shuttleIndicator['name'] in carChartData):
			carChartData[shuttleIndicator['name']] = list()
		carChartData[shuttleIndicator['name']].append(chartData)
		
	return render(request, 'shuttleIndicator.html', {'carChartData':carChartData, 'areas':areas})
