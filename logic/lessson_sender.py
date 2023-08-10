import urllib.request
import uuid

from medsenger_api import *
from config import *
from helpers import *
from models.models import *
import requests
from PIL import Image, ImageFont, ImageDraw



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
                                   action_name="Ответить", action_link=f'tasks/{contract.id}', action_onetime=True)

    db.session.add(SentLesson(contract_id=contract.id, lesson_id=lesson.id))


def send_actual_lessons(app):
    print(gts(), "running send actual lessons")
    with app.app_context():
        contracts = Contract.query.filter_by(active=True).all()

        for contract in contracts:
            print("contract:", contract.id)
            for enrollment in contract.enrollments:
                current_day = (datetime.now() - enrollment.created_on).days
                print("current_day:", current_day)

                if current_day == 0:
                    continue

                course = enrollment.course
                actual_lessons = [lesson for lesson in
                                  Lesson.query.filter_by(course_id=course.id, day=current_day).all() if
                                  lesson not in contract.sent_lessons]

                if len(contract.sent_lessons) == len(course.lessons):
                    if course.diploma_points >= enrollment.points and not enrollment.diploma_received:

                        d_template = course.diploma_template

                        d_name_location = course.diploma_name_location
                        d_name_size = course.diploma_name_size
                        d_name_x = course.diploma_name_x
                        d_name_y = course.diploma_name_y
                        d_name_color = course.diploma_name_color

                        d_date_location = course.diploma_date_location
                        d_date_size = course.diploma_date_size
                        d_date_x = course.diploma_date_x
                        d_date_y = course.diploma_date_y
                        d_date_color = course.diploma_date_color

                        user_contract = contract.id

                        final_diploma = create_user_diploma(d_template, user_contract, d_name_location, d_name_size, d_name_x, d_name_y, d_name_color, d_date_location, d_date_size, d_date_x, d_date_y, d_date_color)

                        enrollment.diploma_received = True

                        medsenger_api.send_message(contract.id, f'Вы удачно завершили курс "{course.title}", поэтому вы можете получить диплом!',
                                                   only_patient=True, attachments=[prepare_file(final_diploma)])

                        db.session.commit()






                # len(contract.sent_lessons) == len(course.lessons)
                # баллы в курсе = минимальное кол-во
                # запоминать

                for lesson in actual_lessons:
                    send_lesson(contract, lesson)

        db.session.commit()

def send_initial_lessons(contract, course):
        actual_lessons = [lesson for lesson in
                          Lesson.query.filter_by(course_id=course.id, day=0).all()]

        for lesson in actual_lessons:
            send_lesson(contract, lesson)

def create_user_diploma(template, contract_id, name_location, name_size, name_x, name_y, name_color, date_location, date_size, date_x, date_y, date_color):
    image_name = uuid.uuid4()
    download_file = urllib.request.urlretrieve(template, f'./diplomas/{image_name}.png')
    img = Image.open(f'./diplomas/{image_name}.png')
    W, H = img.size

    if name_location == None and date_location == None:
        diploma = f'{image_name}.png'
        return diploma
    elif name_location != None and date_location == None:
        try:
            font = ImageFont.truetype(f"./fonts/Roboto-Black.ttf", size=name_size, encoding='UTF-8')
            draw_text = ImageDraw.Draw(img)
            text = f'{contract_id}'
            #w, h = draw_text.textsize(f'{text}', font=font)
            draw_text.text(
                (name_x, name_y),
                f'{text}',
                fill=name_color,
                font=font,
                align=name_location
            )
            img.save(f'./diplomas/{image_name}.png')
            diploma = f'{image_name}.png'
            return diploma
        except Exception as e:
            print(e)
    elif name_location == None and date_location != None:
        try:
            data = datetime.now()
            day = data.day
            month = data.month
            year = data.year
            day = str(day)
            month = str(month)
            if len(day) == 1:
                day = f'0{day}'
            if len(month) == 1:
                month = f'0{month}'
            font = ImageFont.truetype(f"./fonts/Roboto-Black.ttf", size=date_size, encoding='UTF-8')
            draw_text = ImageDraw.Draw(img)
            text = f'{day}.{month}.{year}'
            w, h = draw_text.textsize(f'{text}', font=font)
            draw_text.text(
                (date_x, date_y),
                f'{text}',
                fill=date_color,
                font=font,
                align=date_location
            )
            img.save(f'{image_name}.png')
            diploma = f'{image_name}.png'
            return diploma
        except Exception as e:
            print(e)
    elif name_location != None and date_location != None:
        try:
            font1 = ImageFont.truetype(f"./fonts/Roboto-Black.ttf", size=name_size, encoding='UTF-8')
            draw_text1 = ImageDraw.Draw(img)
            name_text = f'{contract_id}'
            w, h = draw_text1.textsize(f'{name_text}', font=font1)
            draw_text1.text(
                (name_x, name_y),
                f'{name_text}',
                fill=name_color,
                font=font1,
                align=name_location
            )

            data = datetime.now()
            day = data.day
            month = data.month
            year = data.year
            day = str(day)
            month = str(month)
            if len(day) == 1:
                day = f'0{day}'
            if len(month) == 1:
                month = f'0{month}'
            font2 = ImageFont.truetype(f"./fonts/Roboto-Black.ttf", size=date_size, encoding='UTF-8')
            draw_text2 = ImageDraw.Draw(img)
            date_text = f'{day}.{month}.{year}'
            w, h = draw_text2.textsize(f'{date_text}', font=font2)
            draw_text2.text(
                (date_x, date_y),
                f'{date_text}',
                fill=name_color,
                font=font2,
                align=date_location
            )
            img.save(f'{image_name}.png')
            diploma = f'{image_name}.png'
            return diploma
        except Exception as e:
            print(e)
    else:
        diploma = f'{image_name}.png'
        return diploma