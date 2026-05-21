from .models import Question, Choice

def check_answer(question, data):
    """
    data – словарь с присланными из формы данными.
    Возвращает (is_correct: bool, correct_answer: str) – 
    правильный ответ для отображения.
    """
    qtype = question.question_type
    if qtype == 'single':
        return check_single(question, data)
    elif qtype == 'multiple':
        return check_multiple(question, data)
    elif qtype == 'text':
        return check_text(question, data)
    elif qtype == 'ordering':
        return check_ordering(question, data)
    return False, "Неизвестный тип вопроса"

def check_single(question, data):
    choice_id = data.get('choice')
    correct_choice = question.choices.filter(is_correct=True).first()
    if not correct_choice:
        return False, "Ошибка: не задан правильный ответ"
    correct_text = correct_choice.text
    if choice_id and int(choice_id) == correct_choice.id:
        return True, correct_text
    return False, correct_text

def check_multiple(question, data):
    selected_ids = data.getlist('choices')   # список id
    correct_ids = list(
        question.choices.filter(is_correct=True).values_list('id', flat=True)
    )
    correct_texts = list(
        question.choices.filter(is_correct=True).values_list('text', flat=True)
    )
    correct_answer_str = ", ".join(correct_texts)
    if not correct_ids:
        return False, "Ошибка: не заданы правильные ответы"
    # Приводим к множеству целых чисел
    try:
        selected_ids = set(map(int, selected_ids))
    except (TypeError, ValueError):
        selected_ids = set()
    correct_ids = set(correct_ids)
    if selected_ids == correct_ids:
        return True, correct_answer_str
    return False, correct_answer_str

def check_text(question, data):
    user_text = data.get('text_answer', '').strip()
    correct_answer = question.correct_text.strip()
    # Сравнение без учёта регистра и лишних пробелов
    if user_text.lower() == correct_answer.lower():
        return True, correct_answer
    return False, correct_answer

def check_ordering(question, data):
    """
    Ожидаем, что в data пришли поля вида 'order_<choice_id>': ранг.
    Правильный порядок задан через Choice.order_index.
    """
    choices = question.choices.all()
    correct_pairs = {c.id: c.order_index for c in choices if c.order_index is not None}
    if not correct_pairs:
        return False, "Ошибка: не задан правильный порядок"
    user_pairs = {}
    for choice in choices:
        key = f'order_{choice.id}'
        val = data.get(key)
        if val and val.isdigit():
            user_pairs[choice.id] = int(val)
    if user_pairs == correct_pairs:
        # Сформируем строку правильной последовательности
        ordered = sorted(correct_pairs.items(), key=lambda x: x[1])
        correct_text = " → ".join(
            [Choice.objects.get(pk=cid).text for cid, _ in ordered]
        )
        return True, correct_text
    else:
        ordered = sorted(correct_pairs.items(), key=lambda x: x[1])
        correct_text = " → ".join(
            [Choice.objects.get(pk=cid).text for cid, _ in ordered]
        )
        return False, correct_text