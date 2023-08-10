def calculate_points(lesson, form):
    points = 0
    for i, task in enumerate(lesson.tasks):
        answer = form.get(f'question_{i}')

        if answer is not None and answer.isnumeric():
            answer = int(answer)

            if answer >= 0 and answer < len(task['variants']):
                variant = task['variants'][answer]
                points += variant['points']

    return points


def calculate_max_points(lesson):
    points = 0

    for task in lesson.tasks:
        points += max(map(lambda variant: variant['points'], task['variants']))

    return points

def get_word_form(word_forms, number):

    if number % 10 == 1 and number % 100 != 11:
        return word_forms[0]
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return word_forms[1]
    else:
        return word_forms[2]
