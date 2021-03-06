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
        'today-schedule-notification': {
                'task': 'fcmdev.tasks.today_schedule_notification',
                'schedule': crontab(hour=11, minute=00),
    	},
	#'say-hello': {
		#'task': 'schedule.tasks.say_hello',
		#'schedule': crontab(hour=16, minute='*'),
	#},
       'update-billinghistory': {
		'task': 'institute.tasks.updateBillingHistory',
		'schedule': crontab(hour='10,17', minute=00),
	},
	'store-historyschedule': {
		'task': 'schedule.tasks.store_historyschedule',
		'schedule': crontab(hour=23, minute=1),
	},
	'weekly-update': {
		'task': 'schedule.tasks.weekly_update',
		'schedule': crontab(hour=23, minute=15, day_of_week='sat'),
	},
	'resetTodayLoad': {
		'task': 'schedule.tasks.resetTodayLoad',
		'schedule': crontab(hour=23, minute=30, day_of_week='sat'),
	},
       'update-penaltycharge': {
		'task': 'institute.tasks.updatePenaltyCharge',
		'schedule': crontab(hour=00, minute=01, day_of_month='16'),
	},
}
