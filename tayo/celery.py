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
app.conf.broker_url = 'amqp://guest@localhost//'
app.conf.accept_content = ['application/json']
app.conf.beat_schedule = {
<<<<<<< HEAD
    'today-schedule-notification': {
        'task': 'fcmdev.tasks.today_schedule_notification',
        'schedule': crontab(hour=11, minute=25),
    	},

=======
	#'say-hello': {
		#'task': 'schedule.tasks.say_hello',
		#'schedule': crontab(hour=16, minute='*'),
	#},
	'store-historyschedule': {
		'task': 'schedule.tasks.store_historyschedule',
		'schedule': crontab(hour=23, minute=1),
	},
	'weekly-update': {
		'task': 'schedule.tasks.weekly_update',
		'schedule': crontab(hour=23, minute=30, day_of_week='sun'),
	},
	'resetTodayLoad': {
		'task': 'schedule.tasks.resetTodayLoad',
		'schedule': crontab(hour=23, minute=30, day_of_week='sat'),
	},
>>>>>>> c70c00d3fe12bb407c572f4f2b2738759ab6d307
}
