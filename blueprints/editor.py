from flask import Blueprint
from auth import *
from models import *
from helpers import *

editor_blueprint = Blueprint('editor', __name__, template_folder='templates')


@editor_blueprint.route('/')
@auth.login_required
def editor():
    return render_template('editor.html')


@editor_blueprint.route('/api/courses', methods=['GET'])
@auth.login_required
def get_courses_list_for_editor():
    return schemas.courses.dump(Course.query.order_by(models.Course.id).all())


@editor_blueprint.route('/api/courses', methods=['POST'])
@auth.login_required
@validated(schemas.course)
def add_course(course, **kwargs):
    db.session.add(course)
    db.session.commit()

    return schemas.course.dump(course)


@editor_blueprint.route('/api/courses/<int:id>', methods=['PUT'])
@auth.login_required
@validated(schemas.course)
def update_course(course, **kwargs):
    db.session.commit()
    return schemas.course.dump(course)


@editor_blueprint.route('/api/courses/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_course(id, **kwargs):
    course = Course.query.get(id)

    db.session.delete(course)
    db.session.commit()
    return jsonify({'state': 'ok'})


@editor_blueprint.route('/api/courses/<int:course_id>/lessons', methods=['GET'])
@auth.login_required
def get_lessons(course_id):
    course = Course.query.get(course_id)

    if not course:
        return jsonify(mesesage='Object not found'), 404

    return schemas.lessons.dump(course.lessons)


@editor_blueprint.route('/api/courses/<int:course_id>/lessons', methods=['POST'])
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


@editor_blueprint.route('/api/courses/<int:course_id>/lessons/<int:id>', methods=['PUT'])
@auth.login_required
@validated(schemas.lesson)
def edit_lesson(lesson, course_id, **kwargs):
    db.session.commit()

    return schemas.lesson.dump(lesson)


@editor_blueprint.route('/api/courses/<int:course_id>/lessons/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_lesson(course_id, id, **kwargs):
    lesson = Lesson.query.get(id)
    db.session.delete(lesson)
    db.session.commit()
    return jsonify({'state': 'ok'})