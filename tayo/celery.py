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
        'schedule': crontab(hour=11, minute=25),
    	},

}
