from models import *
from datetime import timedelta

with app.app_context():
    contracts = Contract.query.all()
    contracts.sort(key=lambda contract:contract.id)
    for contract in contracts:
        if datetime.now() - timedelta(days=21) < contract.created_on:
            continue

        incomplete_enrollments = list(filter(lambda e: not e.completed, contract.enrollments))

        if incomplete_enrollments:

            print("contract id:", contract.id)

            incomplete_enrollments.sort(key=lambda e: e.course_id)

            print(f"found incomplete enrollments:",
                  list(map(lambda ie: ie.course_id, incomplete_enrollments)))

            first_enrollment = incomplete_enrollments[0]
            print("first enrollment:", first_enrollment.course_id)

            sent_lessons = first_enrollment.get_sent_lessons()

            try:
                last_sent_lesson = sent_lessons[-1]
            except:
                pass


