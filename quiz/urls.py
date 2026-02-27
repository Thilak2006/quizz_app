from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register_student, name='register'),
    path('student/<int:student_id>', views.student_dashboard, name='student_dashboard'),
    path('quiz/<int:student_id>', views.start_quiz, name='start_quiz'),
    path('question', views.show_question, name='show_question'),
    path('answer', views.process_answer, name='process_answer'),
    path('results', views.quiz_results, name='quiz_results'),
    path('add_question', views.add_question, name='add_question'),   # new
]