from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from fertility_project.onboarding.models import Profile, Question, UserResponse
from fertility_project.onboarding.serializers import QuestionSerializer


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
        serialized_questions = QuestionSerializer(questions, many=True)
        return Response({'questions': serialized_questions.data}, status=status.HTTP_200_OK)

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
    

# redempta
class GetOnboardingQuestions(APIView):
  def get(self,request,format=None):
    """
    1) get all the questions in our database
    from .models import Question

    from .serializers import QuestionSerializer, QuestionOptionSerializer

    questions = Question.objects.all() -- all the questions

    serialized_question = QuestionSerializer(questions, many=True).data

    Question - description of the question
    options - [{"id":1, option:option description}]

    2) serialize questions
      - create serializers.py 
      - create a questionSerializer

    3) return the question; send to the frontend
    return Response({'question':serialized_question})
    """

  # Cynthia
  def post(self,request,format=None):
    data = request.POST
    id = int(data['id'])
    answer = data['question']
    user = request.user

      # Authenticated request; the user must be logged in before they can make this request
      # send the user  token along with this request 

    """
      1) get the question that the user is answering
      question = Question.objects.get(id=id) 

      2) check if the user has answered this question before
      try:
        old_response = UserResponse.objects.get(Q(question=question)&Q(user=user))
        # delete old response
        old_response.delete()
      except UserResponse.DoesNotExist:
        pass
        
      3) create our new user response
      new_response = UserResponse()
      new_response.question = .....
      new_response.user = ......
      new_response.save()

      4) return Response({})
    """
  
    