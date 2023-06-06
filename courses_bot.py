from flask import redirect, send_file

from manage import *
from medsenger_api import AgentApiClient
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
    else:
        contract.active = True

    course_ids = request.json.get('params', {}).get('courses', '').split(',')

    for course_id in course_ids:
        course = Course.query.filter_by(id=course_id).first()

        if course and course not in contract.courses:
            contract.courses.append(course)

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


@app.route('/order', methods=['POST'])
@verify_json
def order(data):
    contract_id = data.get('contract_id')
    if data['order'] == 'payment_done':
        order = Order.query.filter_by(payment_id=data['params']['id']).first()

        if order and not order.is_courses:
            medsenger_api.send_message(contract_id, f"Поступила оплата услуги '{order.service.title}'.",
                                       only_patient=True)
            medsenger_api.send_message(contract_id, f"Поступила оплата услуги '{order.service.title}'.",
                                       only_doctor=True)
            order.is_courses = True

            if order.service.order:

                result = medsenger_api.send_order(contract_id, order.service.order, order.service.order_receiver,
                                                  order.service.order_params)

                if result['delivered']:
                    order.is_delivered = True
            else:
                order.is_delivered = True

            db.session.commit()
            return "ok"
    return "not found"


# settings and views
@app.route('/settings', methods=['GET'])
@verify_args
def get_settings(args, form):
    return services()


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


if __name__ == "__main__":
    app.run(HOST, PORT, debug=API_DEBUG)
