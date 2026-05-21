from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.start_quiz, name='start'),
    path('question/', views.take_question, name='question'),
    path('final/', views.final_result, name='final'),
    path('restart/', views.restart_quiz, name='restart'),
]