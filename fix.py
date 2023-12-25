
from models import *
from datetime import timedelta

with app.app_context():
    for sl in SentLesson.query.all():
        sl.course_id = sl.lesson.course_id

    for enrollment in Enrollment.query.all():
        contract = enrollment.contract
        if len(list(filter(lambda sl: sl.course_id == enrollment.course_id, contract.sent_lessons))) >= len(enrollment.course.lessons) - 1:
            enrollment.completed = True

    db.session.commit()