from rest_framework import serializers
from . models import Goal, HabitLog, HabitTarget, Schedule, ScheduleSection, UserSchedule

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

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ["id","name","description"]

class ScheduleGoalSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()
    class Meta:
        model = Goal
        fields = ["id","goal","option","completed"]

    def get_completed(self,obj):
        completed = self.context.get("completed",[])
        return obj.id in completed

class ScheduleSectionSerializer(serializers.ModelSerializer):
    gaol = serializers.SerializerMethodField()

    class Meta:
        models = ScheduleSection
        fields = ["name",'goals',"id"]

    def get_goal(self,obj):
        completed = self.context.get("completed",[])
        return ScheduleGoalSerializer(obj.goals.all(),many=True, context={"completed":completed}).data

class UserScheduleSerializer(serializers.ModelSerializer):
    schedule = serializers.SerializerMethodField()
    goals = serializers.SerializerMethodField()

    class Meta:
        model = UserSchedule
        fields = ["id","schedule","goals"]

    def get_schedule(Self,obj):
        return ScheduleSerializer(obj.schedule).data
    
    def get_goals(self,obj):
        only_goals = self.context.get("goals",None)
        completed_goals = obj.completed_info
        data = []
        sections = ScheduleSection.objects.filter(schedule=obj.schedule)
        for section in sections:
            section_goals = section.goals.all()
            completed_section_goals = completed_goals[section.id]

            if only_goals is not None:
                for goal in section_goals:
                    data.append({
                        "section_id":section.id,
                        "goal_id":goal.id,
                        "goal":f"{section.name} {goal.goal}",
                        "type":goal.option,
                        "completed": goal.id in completed_section_goals
                    })
            else:
                data.append(ScheduleSectionSerializer(section,context={"completed":completed_section_goals}).data)

        return data

