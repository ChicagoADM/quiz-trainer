from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    TYPE_CHOICES = [
        ('single', 'Одиночный выбор'),
        ('multiple', 'Множественный выбор'),
        ('text', 'Текстовый ответ'),
        ('ordering', 'Установление последовательности'),
    ]
    text = models.TextField("Текст вопроса")
    question_type = models.CharField(
        "Тип вопроса", max_length=20, choices=TYPE_CHOICES
    )
    # Для текстовых вопросов правильный ответ можно хранить прямо здесь
    correct_text = models.TextField("Правильный текст (для текстового)", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:80]

class Choice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='choices'
    )
    text = models.CharField("Текст варианта", max_length=300)
    # Для single/multiple – флаг правильности
    is_correct = models.BooleanField("Правильный ответ", default=False)
    # Для ordering – порядковый номер правильной последовательности (1, 2, 3...)
    order_index = models.PositiveSmallIntegerField(
        "Порядковый номер (для последовательности)", null=True, blank=True
    )

    def __str__(self):
        return self.text[:60]

class QuizSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    questions_order = models.JSONField(help_text="Список ID вопросов в порядке предъявления")
    current_index = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField()
    completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)

    @property
    def current_question_id(self):
        if self.current_index < self.total_questions:
            return self.questions_order[self.current_index]
        return None

class UserAnswer(models.Model):
    session = models.ForeignKey(
        QuizSession, on_delete=models.CASCADE, related_name='answers'
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    # Для одиночного/множественного выбора – выбранные варианты
    selected_choices = models.ManyToManyField(Choice, blank=True)
    # Для текстового ответа
    answer_text = models.TextField(blank=True)
    # Для последовательности – JSON: {choice_id: введённый_ранг}
    ordering_submitted = models.JSONField(null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)