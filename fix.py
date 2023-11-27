contract_ids = [9451, 9701, 9731, 10010, 10011, 10012, 10017, 10022, 10033, 10039, 10045, 10046, 10047, 10060, 10073,
                10074, 10075, 10084, 10085, 10086, 10091, 10104, 10131, 10134, 10135, 10139, 10143, 10150, 10160, 10161,
                10177, 10183, 10185, 10188, 10195, 10196, 10201, 10205, 10215, 10216, 10248, 10255, 10276, 10277, 10278,
                10279, 10307, 10332, 10388, 10389, 10409, 10410, 10414, 10422, 10435, 10436]

from models import *
from logic.lessson_sender import send_initial_lessons
from datetime import timedelta

with app.app_context():
    for contract_id in contract_ids:
        enrollment = Enrollment.query.filter_by(contract_id=contract_id, course_id=4).first()

        if enrollment:
            enrollment.created_on = enrollment.created_on + timedelta(days=21)
            print(f"fixed {contract_id}")
    db.session.commit()
