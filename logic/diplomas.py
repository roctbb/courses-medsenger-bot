from PIL import Image, ImageFont, ImageDraw
from medsenger_api import *
from helpers import *
import uuid


def create_user_diploma(course, template, name, name_location, name_size, name_x, name_y, name_color, date_location,
                        date_size, date_x, date_y, date_color):
    image_name = "{} - {}".format(name, course.title)

    try:

        img = Image.open(f'./diploma_templates/{template}').convert('RGB')

        draw_text = ImageDraw.Draw(img)

        if name_location != None:
            text = f'{name}'
            font = ImageFont.truetype(f"./fonts/Roboto-Black.ttf", size=name_size, encoding='UTF-8')
            draw_text.text(
                (name_x, name_y),
                f'{text}',
                fill=name_color,
                font=font,
                align=name_location
            )

        if date_location != None:
            data = datetime.now()
            day = data.day
            month = data.month
            year = data.year
            day = str(day)
            month = str(month)
            font = ImageFont.truetype(f"./fonts/Roboto-Black.ttf", size=date_size, encoding='UTF-8')
            if len(day) == 1:
                day = f'0{day}'
            if len(month) == 1:
                month = f'0{month}'

            text = f'{day}.{month}.{year}'
            draw_text.text(
                (date_x, date_y),
                f'{text}',
                fill=date_color,
                font=font,
                align=date_location
            )

        filename = f'./diplomas/{image_name}.pdf'

        img.save(filename)

        return filename
    except Exception as e:
        print("Error generating diploma:", e)


def send_diploma(enrollment):
    course = enrollment.course
    contract = enrollment.contract

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

    user_name = medsenger_api.get_patient_info(contract.id).get('name')

    final_diploma = create_user_diploma(course, d_template, user_name, d_name_location, d_name_size, d_name_x, d_name_y,
                                        d_name_color, d_date_location, d_date_size, d_date_x, d_date_y, d_date_color)
    if final_diploma:
        enrollment.diploma_received = True

        medsenger_api.send_message(contract.id,
                                   f'Вы удачно завершили курс "{course.title}", поэтому вы можете получить диплом!',
                                   only_patient=True, attachments=[prepare_file(final_diploma)])
