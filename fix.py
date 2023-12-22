
from models import *
from datetime import timedelta

with app.app_context():
    for enrollment in Enrollment.query.filter_by(course_id=5).all():
        new_enrollment = Enrollment(contract_id=enrollment.contract_id, course_id=6, created_on=enrollment.created_on + timedelta(days=21))
        db.session.add(new_enrollment)
    db.session.commit()
