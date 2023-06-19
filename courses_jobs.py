from courses_bot import *
from logic.lessson_sender import send_actual_lessons
from apscheduler.schedulers.background import BlockingScheduler

scheduler = BlockingScheduler()
scheduler.add_job(send_actual_lessons, 'interval', minutes=1, args=(app,))
scheduler.start()

