from models import *
from datetime import timedelta

with app.app_context():
    contracts = Contract.query.all()
    contracts.sort(key=lambda contract: contract.id)
    for contract in contracts:
        enrollments = list(sorted(contract.enrollments, key=lambda e: e.created_on))

        if not enrollments or enrollments[-1].course_id < 2:
            continue

        last_enrollment = enrollments[-1]
        last_date = last_enrollment.created_on

        for course_id in range(last_enrollment.course_id + 1, 8):
            last_date += timedelta(days=21)
            print(f"Planning to add enrollment for course {course_id} for contract {contract.id} starting at {last_date}")
            enrollment = Enrollment(course_id=course_id, created_on=last_date, contract_id=contract.id, completed=False)
            db.session.add(enrollment)

    db.session.commit()
