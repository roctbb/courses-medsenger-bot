from models import *
from datetime import timedelta

with app.app_context():
    for contract in Contract.query.all():
        if datetime.now() - timedelta(days=21) < contract.created_on:
            continue

        incomplete_enrollments = list(filter(lambda e: not e.completed and e.created_at, contract.enrollments))

        if incomplete_enrollments:
            incomplete_enrollments.sort(key=lambda e: e.course_id)

            print(f"found incomplete enrollments for contract {contract.id}:",
                  list(map(lambda ie: ie.course_id, incomplete_enrollments)))
