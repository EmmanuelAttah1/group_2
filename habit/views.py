from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import HabitLogSerializer, HabitTargetSerializer

from .models import Habit, HabitLog, HabitTarget
from django.utils import timezone
from django.db.models import Q


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


class GetHabitLog(APIView):
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
    
class GetHabitTarget(APIView):
    permission_classes = [IsAuthenticated]
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


class GetGoals(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,format=None):
        user = request.user
        pass

class GetUserPlan(APIView):
    def get(self,request,format=None):
        pass

class Assessment(APIView):
    def get(self,request,format=None):
        pass

    def post(self,post,format=None):
        pass