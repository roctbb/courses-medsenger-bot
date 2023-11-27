contract_ids = [10011, 10012, 10017, 10022, 10033, 10047, 10046, 10045, 10084, 10074, 10086, 10073, 10075, 10150, 10131,
                10215, 10389, 10409, 9701, 10010, 10248, 10195, 10196, 10177, 10134, 10104, 10414, 10039, 10139, 10201,
                10185, 10188, 9451, 9701, 9701, 10135, 10161, 10255, 10205, 9731, 10012, 10160, 10183, 10332, 10279,
                10085, 10011, 10307, 10216, 10278, 10017, 10022, 10033, 10046, 10047, 10045, 10073, 10074, 10075, 10084,
                10086, 10091, 10143, 10091, 10277, 10085, 10060, 10039, 10060, 10276, 10388, 10410, 10422, 10436, 10435]

from models import *
from logic.lessson_sender import send_initial_lessons
from datetime import timedelta

with app.app_context():
    for contract_id in contract_ids:
        enrollment = Enrollment.query.filter_by(contract_id=contract_id, course_id=4).first()

        if enrollment:
            enrollment.created_on = enrollment.created_on - timedelta(days=21)
            print(f"fixed {contract_id}")
    db.session.commit()
