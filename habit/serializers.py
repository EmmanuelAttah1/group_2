from rest_framework import serializers
from . models import HabitLog

class HabitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitLog
        fields = ["value"]