from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Question(models.Model):
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description

class QuestionOption(models.Model):
    option_description = models.CharField(max_length=255)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')

    def __str__(self):
        return f"{self.option_description} (for {self.question.description})"
        
class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.user.username}'s response to '{self.question.description}'"
