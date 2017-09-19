from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tayo.settings')

app = Celery('tayo')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
app.conf.timezone = 'Asia/Seoul'
app.conf.enable_utc = True
#app.conf.timezone = 'America/Chicago'
#app.conf.timezone = 'Europe/London'
app.conf.beat_schedule = {
	'say-hello': {
		'task': 'schedule.tasks.say_hello',
		'schedule': crontab(hour=16, minute='*'),
	},
	#'store-historyschedule': {
		#'task': 'schedule.tasks.store_historyschedule',
		#'schedule': crontab(hour=11, minute=24),
	#},
}
#CELERY_ENABLE_UTC = False,
#timezone = 'Asia/Seoul',

#app.conf.beat_schedule = {
	#'store-historyschedule': {
		#'task': 'store_historyschedule',
		#'schedule': crontab(hour=18, minute=48),
	#},
#}



@app.task(bind=True)
def debug_task(self):
	print('Request: {0!r}'.format(self.request))
