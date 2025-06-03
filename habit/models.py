from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Habit(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name

class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habit_logs')
    value = models.CharField(max_length=150)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.habit.name} on {self.date}"
