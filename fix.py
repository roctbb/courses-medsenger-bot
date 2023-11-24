contract_ids = [10011, 10012, 10017, 10022, 10033, 10047, 10046, 10045, 10084, 10074, 10086, 10073, 10075, 10150, 10131,
                10215, 9701, 10010, 10248, 10195, 10196, 10177, 10134, 10104, 10039, 10139, 10201, 10185, 10188, 9451,
                9701, 9701, 10135, 10161, 10255, 10205, 9731, 10012, 10160, 10183, 10085, 10011, 10216, 10017, 10022,
                10033, 10046, 10047, 10045, 10073, 10074, 10075, 10084, 10086, 10091, 10143, 10091, 10085, 10060, 10039,
                10060]

from models import *
from logic.lessson_sender import send_initial_lessons

with app.app_context():
    course = Course.query.get(4)

    for contract_id in contract_ids:
        contract = Contract.query.get(contract_id)

        if contract:
            print(f"Adding course to {contract_id}...")
            enrollment = Enrollment(course_id=course.id, contract_id=contract_id)
            db.session.add(enrollment)

            send_initial_lessons(contract, course)

            print(f"Done adding to {contract_id}")
    db.session.commit()

