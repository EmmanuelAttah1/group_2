from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import Profile, Question, UserResponse
from .serializers import QuestionSerializer


@api_view(["post"])
def register_view(request):
  form = UserCreationForm(request.POST)
  if form.is_valid():
    form.save()  
    token = Token.objects.create(user=form)
    print(token.key) 

    return Response({'Token':token.key})
  
  return Response({'error':form.errors},status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['post'])
def login(request):
    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(username=username, password=password)
    if user:
        token = Token.objects.create(user=user)
        return Response({'token': token.key})
    return Response({'error': 'Invalid credentials'}, status=401)


# New Task

class GetOnboardingQuestions(APIView):
    def get(self, request, format=None):
        questions = Question.objects.all()
        return Response({'questions': QuestionSerializer(questions, many=True).data}, status=status.HTTP_200_OK)

class SubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request, format=None):
        data = request.data  
        try:
            question_id = int(data['id'])       
            answer = data['question']           
            user = request.user                 

            question = Question.objects.get(id=question_id)

            
            profile = Profile.objects.get(user=user)

            
            try:
                old_response = UserResponse.objects.get(Q(question=question) & Q(user=profile))
                old_response.delete()
            except UserResponse.DoesNotExist:
                pass

            
            new_response = UserResponse(
                question=question,
                response=answer,
                user=profile
            )
            new_response.save()

            return Response({'message': 'Response submitted successfully.'}, status=200)

        except KeyError as e:
            return Response({'error': f'Missing field: {str(e)}'}, status=400)
        except Question.DoesNotExist:
            return Response({'error': 'Question not found.'}, status=404)
        except Profile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        
    
class UserInfo(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,format=None):
        user = request.user
        # return a response wih the user information
        return Response({
            "name":f"{user.first_name} {user.last_name}",
            "email":user.email
        },status=status.HTTP_200_OK)
        """
        {}
        first name, last name, email
        
        return Response({"first_name":user.first_name,.........},status=status.HTTP_200_OK)
        """