#from celery import Celery
from celery.schedules import crontab
from flask import current_app as app
from backend.celery.tasks import daily_reminders, monthly_reminders #weekly_reminder

celery_app = app.extensions['celery']

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(30.0, daily_reminders.s()) # 30 sec
    sender.add_periodic_task(60.0, monthly_reminders.s()) # 1 min
