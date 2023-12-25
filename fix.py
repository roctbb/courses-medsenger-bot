
from models import *
from datetime import timedelta

with app.app_context():
    for sl in SentLesson.query.all():
        sl.course_id = sl.lesson.course_id

    db.session.commit()