from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from helpers import *
from manage import app
from flask_migrate import Migrate

db = SQLAlchemy()


class Enrollment(db.Model):
    __tablename__ = 'contract_course'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete='CASCADE'))
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id', ondelete='CASCADE'))
    points = db.Column(db.Integer, default=0)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    diploma_received = db.Column(db.Boolean, server_default="false")
    completed = db.Column(db.Boolean, server_default="false")


    def to_dict(self):
        return {
            "id": self.id,
            "points": self.points,
            "enrolled_on": self.created_on.isoformat(),
            "course": {
                "title": self.course.title,
                "id": self.course.id
            }
        }

    def get_sent_lessons(self):
        return list(filter(lambda sl: sl.course_id == self.course_id, self.contract.sent_lessons))


class SentLesson(db.Model):
    __tablename__ = 'contract_lesson'

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete='CASCADE'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete='CASCADE'))
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id', ondelete='CASCADE'))
    created_on = db.Column(db.DateTime, server_default=db.func.now())

class DoneLesson(db.Model):
    __tablename__ = 'contract_tasks'

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete='CASCADE'))
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id', ondelete='CASCADE'))
    created_on = db.Column(db.DateTime, server_default=db.func.now())

class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=True)

    sent_lessons = db.relationship('Lesson', secondary='contract_lesson', backref=backref('contract', uselist=False),
                                   lazy=True)

    enrollments = db.relationship('Enrollment', backref=backref('contract', uselist=False),
                                  lazy=True, viewonly=True)

    courses = db.relationship('Course', secondary='contract_course', backref=backref('contracts', uselist=False),
                              lazy=True, viewonly=True)

    doctor_agent_token = db.Column(db.String, nullable=True)
    patient_agent_token = db.Column(db.String, nullable=True)

    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __get_tokens(self):
        tokens = medsenger_api.get_agent_token(self.id)
        self.patient_agent_token = tokens['patient_agent_token']
        self.doctor_agent_token = tokens['doctor_agent_token']
        db.session.commit()

    def get_patient_token(self):
        if not self.patient_agent_token:
            self.__get_tokens()
        return self.patient_agent_token

    def get_doctor_token(self):
        if not self.doctor_agent_token:
            self.__get_tokens()
        return self.doctor_agent_token


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(1024), nullable=True)
    lessons = db.relationship('Lesson', backref=backref('course', uselist=True),
                              lazy=True)
    enrollments = db.relationship('Enrollment', backref=backref('course', uselist=False),
                                  lazy=True, viewonly=True)

    show_diploma = db.Column(db.Boolean, default=False)
    show_info_name = db.Column(db.Boolean, default=False)
    show_info_date = db.Column(db.Boolean, default=False)

    diploma_points = db.Column(db.Integer, nullable=True)
    diploma_template = db.Column(db.String(1024), nullable=True)
    
    diploma_name_location = db.Column(db.String(1024), nullable=True)
    diploma_name_size = db.Column(db.Integer, nullable=True)
    diploma_name_x = db.Column(db.Integer, nullable=True)
    diploma_name_y = db.Column(db.Integer, nullable=True)
    diploma_name_color = db.Column(db.String(1024), nullable=True)
    
    diploma_date_location = db.Column(db.String(1024), nullable=True)
    diploma_date_size = db.Column(db.Integer, nullable=True)
    diploma_date_x = db.Column(db.Integer, nullable=True)
    diploma_date_y = db.Column(db.Integer, nullable=True)
    diploma_date_color = db.Column(db.String(1024), nullable=True)

    # diploma fields

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "lessons": [lesson.to_dict() for lesson in sorted(self.lessons, key=lambda l: l.id)]
        }


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(1024), nullable=True)
    text = db.Column(db.Text, nullable=True)
    tasks = db.Column(db.JSON, nullable=True)
    attachments = db.Column(db.JSON, nullable=True)
    day = db.Column(db.Integer, default=0)

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    sents = db.relationship('SentLesson', backref=backref('lesson', uselist=False),
                                  lazy=True, viewonly=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "text": self.text,
            "tasks": self.tasks,
            "day": self.day,
            "attachments": self.attachments
        }

# class Course_lessons(db.Model):
#     for l in Lesson:
#         pass


db.init_app(app)
migrate = Migrate(app, db)
