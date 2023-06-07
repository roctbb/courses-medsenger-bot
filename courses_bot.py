import requests
from flask import redirect, send_file

from manage import *
from medsenger_api import *
from helpers import *
from models import *
from sqlalchemy import desc
from werkzeug.security import check_password_hash
from schemas import *

medsenger_api = AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, API_DEBUG)
schemas = Schemas()


@auth.verify_password
def verify_password(username, password):
    if username == EDITOR_LOGIN and check_password_hash(EDITOR_HASH, password):
        return username


@app.route('/')
def index():
    return "Waiting for the thunder"


@app.route('/status', methods=['POST'])
@verify_json
def status(data):
    answer = {
        "is_tracking_data": True,
        "supported_scenarios": [],
        "tracked_contracts": [contract.id for contract in Contract.query.filter_by(active=True).all()]
    }

    return jsonify(answer)


@app.route('/init', methods=['POST'])
@verify_json
def init(data):
    contract_id = data.get('contract_id')
    contract = Contract.query.filter_by(id=contract_id).first()

    if not contract:
        contract = Contract(id=contract_id)
        db.session.add(contract)
        db.session.commit()
    else:
        contract.active = True

    course_ids = request.json.get('params', {}).get('courses', '').split(',')

    for course_id in course_ids:
        course = Course.query.filter_by(id=course_id).first()

        if course and course not in contract.courses:
            db.session.add(Enrollment(contract_id=contract.id, course_id=course.id))

    db.session.commit()

    return "ok"


@app.route('/remove', methods=['POST'])
@verify_json
def remove(data):
    c = Contract.query.filter_by(id=data.get('contract_id')).first()
    if c:
        c.active = False
        db.session.commit()
    return "ok"


# settings and views
@app.route('/settings', methods=['GET'])
@verify_args
def get_settings(args, form):
    return "Не требует настройки"


@app.route('/settings', methods=['POST'])
@verify_args
def set_settings(args, form):
    return ""


@app.route('/editor')
@auth.login_required
def editor():
    return send_file('templates/editor.html')


@app.route('/editor/api/courses', methods=['GET'])
@auth.login_required
def get_courses_list_for_editor():
    return schemas.courses.dump(Course.query.all())


@app.route('/editor/api/courses', methods=['POST'])
@auth.login_required
@validated(schemas.course)
def add_course(course, **kwargs):
    db.session.add(course)
    db.session.commit()

    return schemas.course.dump(course)


@app.route('/editor/api/courses/<int:id>', methods=['PUT'])
@auth.login_required
@validated(schemas.course)
def update_course(course, **kwargs):
    db.session.commit()
    return schemas.course.dump(course)


@app.route('/editor/api/courses/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_course(id, **kwargs):
    course = Course.query.get(id)

    db.session.delete(course)
    db.session.commit()
    return jsonify({'state': 'ok'})


@app.route('/editor/api/courses/<int:course_id>/lessons', methods=['GET'])
@auth.login_required
def get_lessons(course_id):
    course = Course.query.get(course_id)

    if not course:
        return jsonify(mesesage='Object not found'), 404

    return schemas.lessons.dump(course.lessons)


@app.route('/editor/api/courses/<int:course_id>/lessons', methods=['POST'])
@auth.login_required
@validated(schemas.lesson)
def add_lesson(lesson, course_id, **kwargs):
    course = Course.query.get(course_id)

    if not course:
        return jsonify(mesesage='Object not found'), 404

    db.session.add(lesson)
    db.session.commit()

    course.lessons.append(lesson)
    db.session.commit()

    return schemas.lesson.dump(lesson)


@app.route('/editor/api/courses/<int:course_id>/lessons/<int:id>', methods=['PUT'])
@auth.login_required
@validated(schemas.lesson)
def edit_lesson(lesson, course_id, **kwargs):
    db.session.commit()

    return schemas.lesson.dump(lesson)


@app.route('/editor/api/courses/<int:course_id>/lessons/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_lesson(course_id, id, **kwargs):
    lesson = Lesson.query.get(id)
    db.session.delete(lesson)
    db.session.commit()
    return jsonify({'state': 'ok'})


def send_lesson(contract, lesson):
    attachments = []
    materials = []

    for attachment in lesson.attachments:
        try:
            if attachment.store_as_info:
                materials.append({
                    "name": attachment.title,
                    "link": attachment.url
                })

            name = attachment.url.split('/')[-1]
            data = requests.get(attachment.url).content

            attachments.append(prepare_binary(name, data))
        except Exception as e:
            log(e, False)

    medsenger_api.send_message(contract.id, lesson.text, only_patient=True, attachments=attachments)

    if materials:
        medsenger_api.set_info_materials(contract.id, materials)

    if lesson.tasks:
        medsenger_api.send_message(contract.id, "Ответьте на вопросы, чтобы получить баллы.", only_patient=True,
                                   action_name="Ответить", action_link=f'tasks/{lesson.id}', action_onetime=True)

    db.session.add(SentLesson(contract_id=contract.id, lesson_id=lesson.id))


def send_messages(app):
    with app.app_context():
        contracts = Contract.query.filter_by(active=True).all()

        for contract in contracts:
            current_day = (datetime.now() - contract.created_on).days

            for course in contract.courses:
                actual_lessons = [lesson for lesson in
                                  Lesson.query.filter_by(course_id=course.id, day=current_day).all() if
                                  lesson not in contract.sent_lessons]

                for lesson in actual_lessons:
                    send_lesson(contract, lesson)

        db.session.commit()


if __name__ == "__main__":
    app.run(HOST, PORT, debug=API_DEBUG)
