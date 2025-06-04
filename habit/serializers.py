from rest_framework import serializers
from . models import HabitLog, HabitTarget

class HabitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitLog
        fields = ["value"]

class HabitTargetSerializer(serializers.ModelSerializer):
    habit = serializers.SerializerMethodField()

    class Meta:
        model = HabitTarget
        fields = ['habit','target',"value"]

    def get_habit(self,obj):
        return{
            "name":obj.habit.name,
            "id":obj.habit.id
        }
