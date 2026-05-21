import random
from django.shortcuts import render, redirect, get_object_or_404
from .models import Question, QuizSession, UserAnswer
from .services import check_answer, check_ordering


def start_quiz(request):
    """Создаёт новую тестовую сессию со случайным порядком вопросов."""
    # Удаляем старую незавершённую сессию (если есть)
    old_session = QuizSession.objects.filter(
        session_key=request.session.session_key, completed=False
    ).first()
    if old_session:
        old_session.delete()

    # Получаем все вопросы
    all_questions = list(Question.objects.all())
    if not all_questions:
        return render(request, 'quiz/no_questions.html')

    # Перемешиваем и сохраняем порядок
    random.shuffle(all_questions)
    question_ids = [q.id for q in all_questions]

    # Создаём сессию
    quiz_session = QuizSession.objects.create(
        session_key=request.session.session_key,
        questions_order=question_ids,
        total_questions=len(question_ids)
    )
    request.session['quiz_session_id'] = quiz_session.id
    return redirect('quiz:question')


def take_question(request):
    """Отображает текущий вопрос (GET) или обрабатывает ответ (POST)."""
    session_id = request.session.get('quiz_session_id')
    if not session_id:
        return redirect('quiz:start')

    quiz_session = get_object_or_404(QuizSession, id=session_id, completed=False)

    if request.method == 'POST':
        # --- Обработка ответа ---
        question_id = quiz_session.current_question_id
        if question_id is None:
            return redirect('quiz:final')

        question = get_object_or_404(Question, id=question_id)

        # 1. Сохраняем исходный порядок вариантов для обратной связи
        choices_order_str = request.POST.get('choices_order', '')
        choices_order = []
        if choices_order_str:
            choices_order = [int(x) for x in choices_order_str.split(',') if x.strip().isdigit()]

        # Получаем все варианты вопроса и сортируем их в исходном порядке
        all_choices = list(question.choices.all())
        if choices_order:
            id_to_choice = {c.id: c for c in all_choices}
            sorted_choices = [id_to_choice[cid] for cid in choices_order if cid in id_to_choice]
        else:
            sorted_choices = all_choices

        # 2. Переменные для ответа пользователя
        selected_choice_ids = []      # id выбранных вариантов (для single/multiple)
        user_ordered_ids = []         # порядок id, заданный пользователем (для ordering)
        user_text = ''                # текст ответа (для text)

        # 3. Проверка ответа в зависимости от типа вопроса
        if question.question_type == 'single':
            is_correct, correct_answer_text = check_answer(question, request.POST)
            sel = request.POST.get('choice')
            if sel:
                selected_choice_ids = [int(sel)]

        elif question.question_type == 'multiple':
            is_correct, correct_answer_text = check_answer(question, request.POST)
            selected_choice_ids = [int(x) for x in request.POST.getlist('choices')]

        elif question.question_type == 'text':
            is_correct, correct_answer_text = check_answer(question, request.POST)
            user_text = request.POST.get('text_answer', '')

        elif question.question_type == 'ordering':
            ordering_str = request.POST.get('ordering_list', '')
            user_ordered_ids = [int(x) for x in ordering_str.split(',') if x.strip().isdigit()]
            is_correct, correct_answer_text = check_ordering(question, user_ordered_ids)
            selected_choice_ids = user_ordered_ids  # для отображения пользовательского порядка

        # 4. Сохраняем ответ пользователя в БД
        user_answer = UserAnswer(
            session=quiz_session,
            question=question,
            answer_text=user_text if question.question_type == 'text' else '',
            is_correct=is_correct
        )
        user_answer.save()

        if question.question_type in ('single', 'multiple'):
            if selected_choice_ids:
                user_answer.selected_choices.set(selected_choice_ids)
        elif question.question_type == 'ordering':
            user_answer.ordering_submitted = {'order': user_ordered_ids}
            user_answer.save()

        # 5. Переходим к следующему вопросу
        quiz_session.current_index += 1
        quiz_session.save()

        # 6. Подготовка данных для страницы обратной связи
        correct_choice_ids = []    # id правильных вариантов
        correct_order = []         # QuerySet для правильного порядка (ordering)

        if question.question_type in ('single', 'multiple'):
            correct_choice_ids = list(
                question.choices.filter(is_correct=True).values_list('id', flat=True)
            )
        elif question.question_type == 'ordering':
            correct_order_qs = question.choices.filter(order_index__isnull=False).order_by('order_index')
            correct_choice_ids = list(correct_order_qs.values_list('id', flat=True))
            correct_order = correct_order_qs  # передаём QuerySet для шаблона

        context = {
            'question': question,
            'choices': sorted_choices,               # варианты в том же порядке, что на странице вопроса
            'is_correct': is_correct,
            'correct_answer_text': correct_answer_text,
            'selected_choice_ids': selected_choice_ids,
            'correct_choice_ids': correct_choice_ids,
            'session': quiz_session,
            'has_next': quiz_session.current_index < quiz_session.total_questions,
            'user_text': user_text,
        }
        if question.question_type == 'ordering':
            context['user_ordered_ids'] = user_ordered_ids
            context['correct_order'] = correct_order

        return render(request, 'quiz/answer_feedback.html', context)

    else:
        # --- GET: отображаем очередной вопрос ---
        question_id = quiz_session.current_question_id
        if question_id is None:
            return redirect('quiz:final')

        question = get_object_or_404(Question, id=question_id)
        choices = list(question.choices.all())

        # Перемешиваем варианты (для ordering тоже, чтобы было с чего начать перетаскивание)
        if question.question_type in ('single', 'multiple', 'ordering'):
            random.shuffle(choices)

        context = {
            'question': question,
            'choices': choices,
            'session': quiz_session,
        }
        return render(request, 'quiz/question.html', context)


def final_result(request):
    """Завершает тест и показывает итоговую статистику."""
    session_id = request.session.get('quiz_session_id')
    if not session_id:
        return redirect('quiz:start')

    quiz_session = get_object_or_404(QuizSession, id=session_id)

    # Если сессия ещё не завершена – подсчитываем баллы и закрываем
    if not quiz_session.completed:
        correct_count = quiz_session.answers.filter(is_correct=True).count()
        quiz_session.score = correct_count
        quiz_session.completed = True
        quiz_session.save()

    answers = quiz_session.answers.select_related('question').all()
    return render(request, 'quiz/final.html', {
        'session': quiz_session,
        'answers': answers,
    })


def restart_quiz(request):
    """Сбрасывает текущий тест и перезапускает."""
    session_id = request.session.get('quiz_session_id')
    if session_id:
        QuizSession.objects.filter(id=session_id).delete()
        # Удаляем ключ из сессии
        del request.session['quiz_session_id']
    return redirect('quiz:start')