from models import Enrollment
from manage import app
from logic.diplomas import send_diploma

with app.app_context():
    enrollment_id = input('enrollment_id')
    enrollment = Enrollment.query.get(enrollment_id)

    if not enrollment:
        print("Enrollment not found!")
    else:
        send_diploma(enrollment)
        print("Diploma sent!")