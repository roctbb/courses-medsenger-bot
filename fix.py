contract_ids = [9451,10435,10436,10422,10389,10414,10409,10410,10388,10332,10307,10279,10276,10278,10277,9731]

from models import *
from logic.lessson_sender import send_initial_lessons
from datetime import timedelta

with app.app_context():
    for contract_id in contract_ids:
        enrollment = Enrollment.query.filter_by(contract_id=contract_id, course_id=5).first()

        if enrollment:
            enrollment.created_on = enrollment.created_on + timedelta(days=21)
            print(f"fixed {contract_id}")
    db.session.commit()
