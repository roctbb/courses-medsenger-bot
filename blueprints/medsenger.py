import json
from flask import Blueprint
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

    course_ids = request.json.get('params', {}).get('courses', '').split(',')

    for course_id in course_ids:
        course = Course.query.filter_by(id=course_id).first()

        if course and course not in contract.courses:
            db.session.add(Enrollment(contract_id=contract.id, course_id=course.id))

    db.session.commit()

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
def preview(id):
    course = Course.query.get_or_404(id)
    return render_template("preview.html", course=course)


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
                           courses_json=json.dumps(courses), api_host=API_HOST)


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
