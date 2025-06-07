import datetime
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from .serializers import HabitLogSerializer, HabitTargetSerializer, UserScheduleSerializer

from .models import Goal, Habit, HabitLog, HabitTarget, Schedule, ScheduleSection, UserSchedule
from django.utils import timezone
from django.db.models import Q

"""
    - reminder -- done
    - mark goal as complete -- done
"""


@extend_schema(
    summary="Get goal reminders",
    description="Retrieve today's, tomorrow's, and the day after's goals for the authenticated user.",
    tags=["Goals"],
    responses={
        200: OpenApiResponse(
            description="Goal reminders grouped by day",
            examples=[
                OpenApiExample(
                    'Goal Reminder Example',
                    value={
                        "Today": [
                            {"section_id": 1, "goal_id": 2, "goal": "Take supplement", "type": "supplement", "date": "2025-06-07T08:00:00Z", "completed": False}
                        ],
                        "Tomorrow": [],
                        "Monday": []
                    }
                )
            ]
        )
    }
)
class GetGoalReminder(APIView):
    def get(self,request,format=None):
        user = request.user
        plans = UserSchedule.objects.filter(user=user)

        data = {
            "Today": [],
            "Tomorrow": [],
            (datetime.datetime.now().date() + datetime.timedelta(days=2)).strftime('%A'): []
        }

        today = timezone.now().date()
        tomorrow = today + datetime.timedelta(days=1)
        day_after = today + datetime.timedelta(days=2)


        for plan in plans:
            sections = ScheduleSection.objects.filter(schedule=plan)
            for section in sections:
                completed_section_goals = plan.completed_info.get(str(section.id), [])

                for goal in section.goals.all():
                    goal_date = goal.date.date()  # compare only the date part

                    goal_info = {
                        "section_id":section.id,
                        "goal_id":goal.id,
                        "goal":f"{goal.goal}",
                        "type":goal.option,
                        "date":goal.date,
                        "completed": goal.id in completed_section_goals
                    }

                    if goal_date == today:
                        data["Today"].append(goal_info)
                    elif goal_date == tomorrow:
                        data["Tomorrow"].append(goal_info)
                    elif goal_date == day_after:
                        day_name = day_after.strftime('%A')
                        data[day_name].append(goal_info)
        
        return Response(data)

@extend_schema(
    summary="Get or update user plans and goals",
    description="Retrieve all user plans and goals, or subscribe to a plan. Optionally filter for only goals or all schedules.",
    tags=["Plans"],
    parameters=[
        OpenApiParameter(name="only-goals", type=bool, location=OpenApiParameter.QUERY, description="Return only goals if true"),
        OpenApiParameter(name="subscribe", type=bool, location=OpenApiParameter.QUERY, description="List all schedules with subscription status if true")
    ],
    responses={
        200: OpenApiResponse(
            description="User plans and goals",
            examples=[
                OpenApiExample(
                    'User Plan Example',
                    value=[
                        {"id": 1, "schedule": {"id": 1, "name": "Morning Routine", "description": "Start your day right"}, "goals": []}
                    ]
                )
            ]
        )
    }
)
class GetUserPlanAndGoal(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,format=None):
        only_goals = request.query_params.get("only-goals")
        subscribed = request.query_params.get("subscribe")
        data = []

        if subscribed is not None and subscribed == "true":
            all_schedules = Schedule.objects.all()
            for schedule in all_schedules:
                try:
                    owned = UserSchedule.objects.get(Q(schedule=schedule)&Q(user=request.user))
                    owned = True
                except UserSchedule.DoesNotExist:
                    owned = False
                
                data.append({
                    "name":schedule.name,
                    "id":schedule.id,
                    "owned":owned
                })
        else:
            schedules = UserSchedule.objects.filter(user=request.user)
            data = UserScheduleSerializer(
                schedules,
                many=True, 
                context={"goals":only_goals is not None and only_goals== "true"}
            ).data

        return Response(data)

    def post(self,request,format=None):
        data = request.POST
        id = int(data['schedule_id'])
        goal_id = int(data['goal_id'])
        section_id = int(data['section_id'])

        try:
            schedule = UserSchedule.objects.get(Q(user=request.user)&Q(id=id))
            goal = schedule.goals.get(id=goal_id)
            section = ScheduleSection.objects.get(Q(user=request.user)&Q(id=section_id))

            completed = schedule.completed_info
            
            action = ""
            if goal.id in completed[section.id]:
                completed[section.id].remove(goal.id)
                action = "removed"
            else:
                completed[section.id].append(goal.id)
                action = "add"

            schedule.completed_info = completed
            schedule.save()

            return Response({'action':action})
        except (UserSchedule.DoesNotExist, Goal.DoesNotExist):
            return Response(status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Unlock a plan",
    description="Unlock or purchase a plan for the authenticated user.",
    tags=["Plans"],
    parameters=[OpenApiParameter(name="id", type=int, location=OpenApiParameter.PATH, description="Plan ID")],
    responses={
        200: OpenApiResponse(
            description="Plan unlock status",
            examples=[
                OpenApiExample('Already Purchased', value={"msg": "already purchased"}),
                OpenApiExample('Purchased', value={"msg": "purchased"})
            ]
        ),
        400: OpenApiResponse(description="Plan not found", examples=[OpenApiExample('Error', value={})])
    }
)
@api_view(['get'])
@permission_classes([IsAuthenticated])
def unlock_plan(request,id):
    try:
        plan = Schedule.objects.get(id=id)
        try:
            user_plan = UserSchedule.objects.get(Q(user=request.user)&Q(schedule=plan))
            return Response({"msg":"already purchased"})
        except UserSchedule.DoesNotExist:
            user_plan = UserSchedule(user=request.user, schedule=plan)
            user_plan.save()
            return Response({"msg":"purchased"})
    except Schedule.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    summary="Log a habit value",
    description="Log a value for a habit for the authenticated user.",
    tags=["Habits"],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'habit_id': {'type': 'integer'},
                'value': {'type': 'string'}
            }
        }
    },
    responses={
        201: OpenApiResponse(description="Habit log saved", examples=[OpenApiExample('Success', value={"message": "Habit log saved successfully."})]),
        400: OpenApiResponse(description="Error", examples=[OpenApiExample('Error', value={"error": "Some error message"})])
    }
)
@api_view(['post'])
def log_habit_value(request):
    try:
        user = request.user

        habit_id = request.data.get('habit_id')
        value = request.data.get('value')
        date = timezone.now().date() #current 

        habit = get_object_or_404(Habit, id=habit_id)

        HabitLog.objects.create(
            habit=habit,
            user=user,
            value=value,
            date=date
        )

        return Response({'message': 'Habit log saved successfully.'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Get user average habit value",
    description="Get the average value for a habit for the authenticated user.",
    tags=["Habits"],
    parameters=[OpenApiParameter(name="habit_id", type=int, location=OpenApiParameter.PATH, description="Habit ID")],
    responses={
        200: OpenApiResponse(description="Average value", examples=[OpenApiExample('Average', value={"averages": 5.0})]),
        404: OpenApiResponse(description="No logs found", examples=[OpenApiExample('Not Found', value={"message": "No logs found for user."})]),
        400: OpenApiResponse(description="Error", examples=[OpenApiExample('Error', value={"error": "Some error message"})])
    }
)
@api_view(['get'])
def get_user_average_habit_value(request, habit_id):
    try:
        user = request.user
        logs = HabitLog.objects.filter(Q(user=user)&Q(habit__id=habit_id))

        if not logs.exists():
            return Response({'message': 'No logs found for user.'}, status=status.HTTP_404_NOT_FOUND)

        sum_value = 0

        for habit in logs:
            sum_value += habit.value

        averages = sum_value / logs.count()
            

        return Response({'averages': averages}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Get habit logs",
    description="Get all logs for a habit for the authenticated user, optionally filtered by date.",
    tags=["Habits"],
    parameters=[
        OpenApiParameter(name="habit", type=int, location=OpenApiParameter.QUERY, description="Habit ID"),
        OpenApiParameter(name="date", type=str, location=OpenApiParameter.QUERY, description="Date (YYYY-MM-DD)")
    ],
    responses={
        200: OpenApiResponse(description="Habit logs", examples=[OpenApiExample('Logs', value={"data": [{"value": "10"}]})]),
        400: OpenApiResponse(description="Missing habit ID", examples=[OpenApiExample('Error', value={})])
    }
)
class GetHabitLog(GenericAPIView):
    serializer_class = HabitLogSerializer
    def get(self,request,format=None):
        habit_id = request.query_params.get("habit") #user is sending habit value
        date = request.query_params.get("date") # user is sending date value

        if habit_id == None:
            return Response({},status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        logs = HabitLog.objects.filter(Q(user=user)&Q(habit__id=int(habit_id)))

        if date is not None: # the user is sending value for date
            logs = logs.filter(date=date)

        return Response({'data':HabitLogSerializer(logs, many=True).data}, status=status.HTTP_200_OK)
    
@extend_schema(
    summary="Get or update habit targets",
    description="Get all habit targets for the authenticated user, or update a target value.",
    tags=["Habits"],
    responses={
        200: OpenApiResponse(description="Habit targets", examples=[OpenApiExample('Targets', value={"data": [{"habit": {"name": "Water", "id": 1}, "target": 8, "value": 2}]})]),
        400: OpenApiResponse(description="Error", examples=[OpenApiExample('Error', value={})])
    }
)
class GetHabitTarget(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HabitTargetSerializer
    def get(self,request,format=None):
        all_habit = HabitTarget.objects.filter(user=request.user)
        data = HabitTargetSerializer(all_habit, many=True).data

        return Response({"data":data},status=status.HTTP_200_OK)
    
    def post(self,request,format=None):
        data = request.POST
        value = data['value']
        id = data['habit_target_id']

        try:
            target = HabitTarget.objects.get(id=int(id))
            target.value += int(value)
            target.save()

            return Response({},status=status.HTTP_200_OK)
        except HabitTarget.DoesNotExist:
            return Response({},status=status.HTTP_400_BAD_REQUEST)