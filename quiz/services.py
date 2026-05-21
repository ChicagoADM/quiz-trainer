from .models import Question, Choice

def check_answer(question, data):
    """Для вопросов single, multiple, text. data – request.POST."""
    qtype = question.question_type
    if qtype == 'single':
        return check_single(question, data)
    elif qtype == 'multiple':
        return check_multiple(question, data)
    elif qtype == 'text':
        return check_text(question, data)
    elif qtype == 'ordering':
        # Не должно вызываться, т.к. ordering проверяется отдельно,
        # но оставим заглушку на всякий случай.
        return False, "Неверный вызов для ordering"
    return False, "Неизвестный тип вопроса"


def check_single(question, data):
    choice_id = data.get('choice')
    correct = question.choices.filter(is_correct=True).first()
    if not correct:
        return False, "Ошибка: не задан правильный ответ"
    if choice_id and int(choice_id) == correct.id:
        return True, correct.text
    return False, correct.text


def check_multiple(question, data):
    selected = set(map(int, data.getlist('choices')))
    correct_qs = question.choices.filter(is_correct=True)
    correct_ids = set(correct_qs.values_list('id', flat=True))
    correct_text = ", ".join(correct_qs.values_list('text', flat=True))
    if not correct_ids:
        return False, "Ошибка: не заданы правильные ответы"
    if selected == correct_ids:
        return True, correct_text
    return False, correct_text


def check_text(question, data):
    user_text = data.get('text_answer', '').strip()
    correct = question.correct_text.strip()
    if not correct:
        return False, "Правильный ответ не задан"
    if user_text.lower() == correct.lower():
        return True, correct
    return False, correct


def check_ordering(question, ordered_ids):
    """
    ordered_ids – список ID вариантов в порядке, заданном пользователем.
    """
    correct_qs = question.choices.filter(order_index__isnull=False).order_by('order_index')
    correct_ids = list(correct_qs.values_list('id', flat=True))
    if not correct_ids:
        return False, "Ошибка: не задан правильный порядок"

    correct_text = " → ".join([c.text for c in correct_qs])

    if ordered_ids == correct_ids:
        return True, correct_text
    else:
        return False, correct_text