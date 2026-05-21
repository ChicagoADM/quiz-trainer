from django.contrib import admin
from .models import Question, Choice, QuizSession, UserAnswer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1
    fields = ['text', 'is_correct', 'order_index']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'question_type', 'created_at']
    list_filter = ['question_type']
    inlines = [ChoiceInline]

@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'session_key', 'total_questions', 'score', 'completed', 'started_at']

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ['session', 'question', 'is_correct', 'answered_at']