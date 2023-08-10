from medsenger_api import *
from models.models import *
import requests
from logic.diplomas import send_diploma


def send_lesson(contract, lesson, with_test=True):
    attachments = []
    materials = []

    for attachment in lesson.attachments:
        try:
            if attachment.get('store_as_info'):
                materials.append({
                    "name": attachment.get('title'),
                    "link": attachment.get('url')
                })

            name = attachment.get('url').split('/')[-1]
            data = requests.get(attachment.get('url')).content

            attachments.append(prepare_binary(name, data))
        except Exception as e:
            log(e, False)

    medsenger_api.send_message(contract.id, lesson.text, only_patient=True, attachments=attachments)

    if materials:
        medsenger_api.set_info_materials(contract.id, json.dumps(materials))

    if lesson.tasks and with_test:
        medsenger_api.send_message(contract.id, "Ответьте на вопросы, чтобы получить баллы.", only_patient=True,
                                   action_name="Ответить", action_link=f'tasks/{lesson.id}', action_onetime=True)

    db.session.add(SentLesson(contract_id=contract.id, lesson_id=lesson.id))


def send_actual_lessons(app):
    print(gts(), "running send actual lessons")
    with app.app_context():
        contracts = Contract.query.filter_by(active=True).all()

        for contract in contracts:
            print("contract:", contract.id)
            for enrollment in contract.enrollments:
                if enrollment.diploma_received:
                    continue

                current_day = (datetime.now() - enrollment.created_on).days
                print("current_day:", current_day)

                if current_day == 0:
                    continue

                course = enrollment.course
                if len(contract.sent_lessons) == len(course.lessons):
                    print("All lessons sent")
                    if course.diploma_points <= enrollment.points:
                        print("Sending diploma")
                        send_diploma(enrollment)
                else:
                    actual_lessons = [lesson for lesson in
                                      Lesson.query.filter_by(course_id=course.id, day=current_day).all() if
                                      lesson not in contract.sent_lessons]

                    for lesson in actual_lessons:
                        send_lesson(contract, lesson)

        db.session.commit()


def send_initial_lessons(contract, course):
    actual_lessons = [lesson for lesson in
                      Lesson.query.filter_by(course_id=course.id, day=0).all()]

    for lesson in actual_lessons:
        send_lesson(contract, lesson)
