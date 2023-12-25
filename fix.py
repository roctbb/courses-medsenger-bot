from models import *
from datetime import timedelta

def is_empty(enrollment):
    return len(enrollment.get_sent_lessons()) == 0

with app.app_context():
    contracts = Contract.query.all()
    contracts.sort(key=lambda contract: contract.id)
    for contract in contracts:
        if datetime.now() - timedelta(days=21) < contract.created_on:
            continue

        incomplete_enrollments = list(filter(lambda e: not e.completed, contract.enrollments))

        if incomplete_enrollments:

            print("contract id:", contract.id)

            incomplete_enrollments.sort(key=lambda e: e.course_id)

            print(f"found incomplete enrollments:",
                  list(map(lambda ie: ie.course_id, incomplete_enrollments)))

            for index, enrollment in enumerate(incomplete_enrollments):
                if not is_empty(enrollment):
                    continue
                break

            print("first empty enrollment:", index)


