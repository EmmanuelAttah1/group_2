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


class HabitTarget(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    target = models.PositiveIntegerField()
    value = models.PositiveIntegerField(default=0, blank=True)

    def __str__(self):
        return self.habit.name
    
    
class Goal(models.Model):
    choices = [
        ("supplement","Supplement"),
        ("excercise", "Excercise"),
        ("appiontment","Appiontment")
    ]
    goal = models.CharField(max_length=200)
    date = models.DateTimeField()
    option = models.CharField(max_length=30, choices=choices)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.goal
    

class Schedule(models.Model):
    name =  models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name

class ScheduleSection(models.Model):
    name = models.CharField(max_length=30)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    goals = models.ManyToManyField(Goal)

    def __str_(self):
        return self.name

class UserSchedule(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_started = models.DateField

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"