from django.contrib import admin
from .models import Student, Question, Response

admin.site.register(Student)
admin.site.register(Question)
admin.site.register(Response)