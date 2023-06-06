from marshmallow import post_load
from marshmallow.validate import Length

from models import *
from manage import ma
import helpers


class CourseSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Course

    id = ma.auto_field(required=False, default=None, allow_none=True)
    title = ma.auto_field(required=True)

    @post_load
    def make(self, data, **kwargs):
        return helpers.make(Course, data)


class AttachmentSchema(ma.Schema):
    url = ma.Str(required=True)
    store_as_info = ma.Boolean(required=True)


class VariantSchema(ma.Schema):
    text = ma.Str(required=True)
    points = ma.Integer(required=True)


class TaskSchema(ma.Schema):
    question = ma.Str(required=True)
    variants = ma.List(ma.Nested(VariantSchema), required=True, validate=Length(2,10))


class LessonSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Lesson

    id = ma.auto_field(required=False, default=None, allow_none=True)
    title = ma.auto_field(required=True)
    text = ma.auto_field(required=True)
    attachments = ma.List(ma.Nested(AttachmentSchema), required=True)
    tasks = ma.List(ma.Nested(TaskSchema), required=True)

    @post_load
    def make(self, data, **kwargs):
        return helpers.make(Lesson, data)


class Schemas:
    course = CourseSchema()
    courses = CourseSchema(many=True)

    lesson = LessonSchema()
    lessons = LessonSchema(many=True)

    task = TaskSchema()
    attachment = AttachmentSchema()
    variant = VariantSchema()
