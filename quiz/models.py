from django.db import models
from django.utils import timezone


class Student(models.Model):
    name = models.CharField(max_length=100)
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Question(models.Model):
    TOPICS = [
        ('Math', 'Math'),
        ('Science', 'Science'),
        ('History', 'History'),
        ('Language', 'Language'),
    ]

    topic = models.CharField(max_length=20, choices=TOPICS)
    difficulty = models.FloatField()
    text = models.TextField()
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    correct = models.CharField(max_length=200)
    explanation = models.TextField()

    def __str__(self):
        return self.text


class Response(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response = models.CharField(max_length=200)
    correct = models.BooleanField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.name} - {self.question.text}"