
from models import *
from datetime import timedelta

with app.app_context():
    for contract in Contract.query.all():
        incomplete_enrollments = list(filter(lambda e: not e.completed, contract.enrollments))

        incomplete_enrollments.sort(key=lambda e: e.course_id)

        print(f"found incomplete enrollments for contract {contract.id}:", list(map(lambda ie: ie.course_id, incomplete_enrollments)))