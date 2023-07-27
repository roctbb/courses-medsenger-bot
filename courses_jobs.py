from courses_bot import *
from logic.lessson_sender import send_actual_lessons
from apscheduler.schedulers.background import BlockingScheduler

scheduler = BlockingScheduler()
scheduler.add_job(send_actual_lessons, 'cron', hour=8, minute=1, second=0, args=(app, ))
scheduler.start()

