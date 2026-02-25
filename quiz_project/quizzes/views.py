from django.shortcuts import render, get_object_or_404
from .models import Quiz

def quiz_list(request):
    quizzes = Quiz.objects.all()
    return render(request, "quizzes/quiz_list.html", {"quizzes": quizzes})


def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == "POST":
        score = 0
        total = quiz.question_set.count()

        for question in quiz.question_set.all():
            selected = request.POST.get(str(question.id))
            correct_option = question.option_set.filter(is_correct=True).first()

            if selected and int(selected) == correct_option.id:
                score += 1

        return render(request, "quizzes/result.html", {
            "score": score,
            "total": total
        })

    return render(request, "quizzes/take_quiz.html", {"quiz": quiz})