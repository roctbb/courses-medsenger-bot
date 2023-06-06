from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

db = SQLAlchemy()

contract_course = db.Table('contract_course',
                           db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
                           db.Column('contract_id', db.Integer, db.ForeignKey('contract.id')),
                           db.Column('points', db.Integer, default=0),
                           db.Column('created_on', db.DateTime, server_default=db.func.now())
                           )

contract_lesson = db.Table('contract_lesson',
                           db.Column('lesson_id', db.Integer, db.ForeignKey('lesson.id')),
                           db.Column('contract_id', db.Integer, db.ForeignKey('contract.id')),
                           db.Column('created_on', db.DateTime, server_default=db.func.now())
                           )


class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=True)
    courses = db.relationship('Course', secondary=contract_course, backref=backref('contract', uselist=False),
                              lazy=True)
    sent_lessons = db.relationship('Lesson', secondary=contract_lesson, backref=backref('contract', uselist=False),
                                   lazy=True)

    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(1024), nullable=True)
    lessons = db.relationship('Lesson', backref=backref('course', uselist=False),
                              lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "lessons": [lesson.to_dict() for lesson in self.lessons]
        }


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(1024), nullable=True)
    text = db.Column(db.Text, nullable=True)
    tasks = db.Column(db.JSON, nullable=True)
    attachments = db.Column(db.JSON, nullable=True)
    day = db.Column(db.Integer, default=0)

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "text": self.text,
            "tasks": self.tasks,
            "attachments": self.attachments
        }
