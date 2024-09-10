from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('teacher', 'Преподаватель'),
        ('student', 'Студент')
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    video_url = models.URLField()

class Test(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE)
    questions = models.ManyToManyField('Question')

class Question(models.Model):
    text = models.TextField()
    answers = models.ManyToManyField('Answer')

class Answer(models.Model):
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

class Submission(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
