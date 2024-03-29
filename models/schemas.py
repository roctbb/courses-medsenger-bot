from marshmallow import post_load
from marshmallow.validate import Length
from flask_marshmallow import Marshmallow
from .models import *
import helpers

ma = Marshmallow(app)


class CourseSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Course

    id = ma.auto_field(required=False, default=None, allow_none=True)
    title = ma.auto_field(required=True)

    show_diploma = ma.auto_field(required=False, default=None)
    show_info_name = ma.auto_field(required=False, default=None)
    show_info_date = ma.auto_field(required=False, default=None)

    diploma_points = ma.auto_field(required=False, default=None)
    diploma_template = ma.auto_field(required=False, default=None)
    
    diploma_name_location = ma.auto_field(required=False, default=None)
    diploma_name_size = ma.auto_field(required=False, default=None)
    diploma_name_x = ma.auto_field(required=False, default=None)
    diploma_name_y = ma.auto_field(required=False, default=None)
    diploma_name_color = ma.auto_field(required=False, default=None)
    
    diploma_date_location = ma.auto_field(required=False, default=None)
    diploma_date_size = ma.auto_field(required=False, default=None)
    diploma_date_x = ma.auto_field(required=False, default=None)
    diploma_date_y = ma.auto_field(required=False, default=None)
    diploma_date_color = ma.auto_field(required=False, default=None)
    
    

    @post_load
    def make(self, data, **kwargs):
        return helpers.make(Course, data)


class AttachmentSchema(ma.Schema):
    url = ma.Str(required=True)
    title = ma.Str()
    store_as_info = ma.Boolean()


class VariantSchema(ma.Schema):
    text = ma.Str(required=True)
    points = ma.Integer(required=True)


class TaskSchema(ma.Schema):
    question = ma.Str(required=True)
    image = ma.Str(required=False)
    variants = ma.List(ma.Nested(VariantSchema), required=True, validate=Length(2, 10))


class LessonSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Lesson

    id = ma.auto_field(required=False, default=None, allow_none=True)
    title = ma.auto_field(required=True)
    text = ma.auto_field(required=True)
    attachments = ma.List(ma.Nested(AttachmentSchema), required=True)
    tasks = ma.List(ma.Nested(TaskSchema), required=True)
    day = ma.auto_field(required=True)

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


schemas = Schemas()
