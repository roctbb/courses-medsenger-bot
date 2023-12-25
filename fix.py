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

            last_index = max(0, index - 1)
            print("last stopped enrollment:", last_index)

            for index, enrollment in enumerate(incomplete_enrollments):
                if index < last_index:
                    enrollment.completed = True
                    print(f"Will mark course {enrollment.course_id} as completed")

                if index == last_index:
                    sent_count = len(enrollment.get_sent_lessons())
                    start_date = datetime.now() - timedelta(days=sent_count)
                    enrollment.created_on = start_date
                    print(f"Will set start date to {start_date} for course {enrollment.course_id}")

                else:
                    start_date += timedelta(days=21)
                    enrollment.created_on = start_date
                    print(f"Will set start date to {start_date} for course {enrollment.course_id}")

        print()
        print()
