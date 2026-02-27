import random
from .models import Response, Question


def update_student_performance(student, question, is_correct):
    Response.objects.create(
        student=student,
        question=question,
        response=question.correct if is_correct else "",
        correct=is_correct
    )


def get_next_topic(student):
    responses = Response.objects.filter(student=student)

    topic_accuracy = {}

    for response in responses:
        topic = response.question.topic
        if topic not in topic_accuracy:
            topic_accuracy[topic] = {"correct": 0, "total": 0}
        topic_accuracy[topic]["total"] += 1
        if response.correct:
            topic_accuracy[topic]["correct"] += 1

    if not topic_accuracy:
        return random.choice(["Math", "Science", "History", "Language"])

    weakest_topic = min(
        topic_accuracy,
        key=lambda t: topic_accuracy[t]["correct"] / topic_accuracy[t]["total"]
    )

    return weakest_topic


def get_question(student, asked_ids):
    topic = get_next_topic(student)
    questions = Question.objects.filter(topic=topic).exclude(id__in=asked_ids)

    if questions.exists():
        return random.choice(questions)

    return None