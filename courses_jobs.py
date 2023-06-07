from courses_bot import *
from apscheduler.schedulers.background import BlockingScheduler

scheduler = BlockingScheduler()
scheduler.add_job(send_messages, 'cron', hour=8, minute=1, second=0, args=(app,))
scheduler.add_job(send_messages, 'interval', minutes=1, args=(app,))
scheduler.start()

