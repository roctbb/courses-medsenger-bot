import json
import time

from flask import Blueprint

from logic.lessson_sender import send_lesson
from models.schemas import *
from helpers import *
from config import *

medsenger_blueprint = Blueprint('medsenger_endpoints', __name__, template_folder='templates')


@medsenger_blueprint.route('/status', methods=['POST'])
@verify_json
def status(data):
    answer = {
        "is_tracking_data": True,
        "supported_scenarios": [],
        "tracked_contracts": [contract.id for contract in Contract.query.filter_by(active=True).all()]
    }

    return jsonify(answer)


@medsenger_blueprint.route('/init', methods=['POST'])
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

    course_ids = request.json.get('params', {}).get('courses')

    if course_ids:
        for course_id in course_ids.split(','):
            course = Course.query.filter_by(id=course_id).first()

            if course and course not in contract.courses:
                db.session.add(Enrollment(contract_id=contract.id, course_id=course.id))

    db.session.commit()

    return "ok"


@medsenger_blueprint.route('/order', methods=['POST'])
@verify_json
def order(data):
    contract_id = data.get('contract_id')
    contract = Contract.query.filter_by(id=contract_id).first()

    if not contract:
        abort(422)

    try:
        if "add_course_" in data['order']:
            course_id = int(data['order'].lstrip('"add_course_"'))
            course = Course.query.get(course_id)

            if course and course not in contract.courses:
                enrollment = Enrollment(course_id=course_id, contract_id=contract_id)
                db.session.add(enrollment)

        if "remove_course_" in data['order']:
            course_id = int(data['order'].lstrip('"remove_course_"'))
            enrollment = Enrollment.query.filter_by(course_id=course_id, contract_id=contract_id).first()

            if enrollment:
                db.session.delete(enrollment)

        db.session.commit()

    except Exception as e:
        print(e)

    return "ok"


@medsenger_blueprint.route('/remove', methods=['POST'])
@verify_json
def remove(data):
    c = Contract.query.filter_by(id=data.get('contract_id')).first()
    if c:
        c.active = False
        db.session.commit()
    return "ok"


# settings and views
@medsenger_blueprint.route('/preview/<int:id>', methods=['GET'])
@has_token
def preview(args, form, id):
    contract = Contract.query.filter_by(doctor_agent_token=args.get('agent_token')).first()

    if not contract:
        abort(401)

    course = Course.query.get_or_404(id)
    return render_template("preview.html", course=course.to_dict())


@medsenger_blueprint.route('/preview/<int:id>', methods=['POST'])
@has_token
def force_send(args, form, id):
    contract = Contract.query.filter_by(doctor_agent_token=args.get('agent_token')).first()

    if not contract:
        abort(401)

    lesson_id = form.get('lesson_id')
    course = Course.query.get_or_404(id)
    lesson = Lesson.query.get_or_404(lesson_id)

    if course in contract.courses:
        with_test = True
    else:
        with_test = False

    send_lesson(contract, lesson, with_test)

    return render_template("preview.html", course=course, message="Сообщение отправлено!")


@medsenger_blueprint.route('/tasks/<int:lesson_id>', methods=['GET'])
@verify_args
def tasks(args, form, lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)

    return render_template("tasks.html", lesson=lesson)


@medsenger_blueprint.route('/tasks/<int:lesson_id>', methods=['POST'])
@verify_args
def send_tasks(args, form, lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    contract_id = args.get('contract_id')

    enrollment = Enrollment.query.filter_by(course_id=lesson.course_id, contract_id=contract_id).first()

    if not enrollment:
        abort(404)

    points = 0

    for i, task in enumerate(lesson.tasks):
        answer = form.get(f'question_{i}')

        if answer is not None and answer.isnumeric():
            answer = int(answer)

            if answer >= 0 and answer < len(task['variants']):
                variant = task['variants'][answer]
                points += variant['points']

    enrollment.points += points
    db.session.commit()

    medsenger_api.send_message(contract_id,
                               f"Спасибо за заполнение теста! Вы заработали {points} новых баллов, теперь у Вас {enrollment.points} баллов!",
                               action_deadline=int(time.time()) + 60 * 60 * 3, only_patient=True)

    return render_template("done.html")


@medsenger_blueprint.route('/settings', methods=['GET'])
@verify_args
def get_settings(args, form):
    return get_contract_courses(args, form)


@medsenger_blueprint.route('/settings', methods=['POST'])
@verify_args
def set_settings(args, form):
    return save_contract_courses(args, form)


@medsenger_blueprint.route('/courses', methods=['GET'])
@verify_args
def get_courses(args, form):
    return get_contract_courses(args, form)


@medsenger_blueprint.route('/courses', methods=['POST'])
@verify_args
def set_courses(args, form):
    return save_contract_courses(args, form)


def get_contract_courses(args, form):
    contract_id = args.get('contract_id')
    contract = Contract.query.get_or_404(contract_id)
    courses = [{"id": c.id, "title": c.title} for c in Course.query.all()]

    return render_template('settings.html', enrollments_json=json.dumps(to_dict(contract.enrollments)),
                           courses_json=json.dumps(courses), api_host=API_HOST, agent_token=contract.get_doctor_token())


def save_contract_courses(args, form):
    contract_id = args.get('contract_id')
    contract = Contract.query.get_or_404(contract_id)

    course_id = form.get('course_id')
    course = Course.query.get_or_404(course_id)

    if form.get('action_type') == 'add_course':
        if course not in contract.courses:
            enrollment = Enrollment(course_id=course_id, contract_id=contract_id)
            db.session.add(enrollment)
    if form.get('action_type') == 'remove_course':
        if course in contract.courses:
            enrollments = Enrollment.query.filter_by(course_id=course_id, contract_id=contract_id).all()
            for enrollment in enrollments:
                db.session.delete(enrollment)

    db.session.commit()

    return get_contract_courses(args, form)
