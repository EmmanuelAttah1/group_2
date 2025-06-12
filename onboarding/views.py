from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from django.db.models import Q
from django.contrib.auth import authenticate

from .models import Profile, Question, QuestionOption, UserAssessmentResult, UserResponse
from .serializers import QuestionSerializer, UserRegistrationSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse


@extend_schema(
    summary="Get user assessment result",
    description="Retrieve the assessment result (score) for the authenticated user.",
    tags=["Assessment"],
    responses={
        200: OpenApiResponse(description="Assessment result", examples=[OpenApiExample('Result', value={"result": 80})]),
        400: OpenApiResponse(description="No assessment found", examples=[OpenApiExample('Error', value={})])
    }
)
class Assessment(APIView):
    permission_classes = [IsAuthenticated]
    """Get User assessment result"""
    def get(self,request,format=None):
        try:
            assessment = UserAssessmentResult.objects.get(user=request.user)
            return Response({"result":assessment.score})
        except UserAssessmentResult.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="User registration",
    description="Register a new user and return token.",
    tags=["Auth"],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'email': {'type': 'string'},
                'password': {'type': 'string'},
                'first_name': {'type': 'string'},
                'last_name': {'type': 'string'}
            }
        }
    },
    responses={
        201: OpenApiResponse(description="Registration successful", examples=[OpenApiExample('Token', value={"token": "abc123token"})]),
        400: OpenApiResponse(description="Invalid data", examples=[OpenApiExample('Error', value={"error": "Invalid data"})])
    }
)
class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token,_ = Token.objects.get_or_create(user=user)
            profile = Profile.objects.get(user=user)
            
            return Response({'token': token.key,"finished_onboarding":profile.assessment_result != 0}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    summary="User login",
    description="Authenticate user and return token.",
    tags=["Auth"],
    request={
        'application/x-www-form-urlencoded': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'password': {'type': 'string'}
            }
        }
    },
    responses={
        200: OpenApiResponse(description="Login successful", examples=[OpenApiExample('Token', value={"token": "abc123token"})]),
        401: OpenApiResponse(description="Invalid credentials", examples=[OpenApiExample('Error', value={"error": "Invalid credentials"})])
    }
)
@api_view(['post'])
def login(request):
    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(username=username, password=password)
    if user:
        token,_ = Token.objects.get_or_create(user=user)
        profile = Profile.objects.get(user=user)
        return Response({'token': token.key,"finished_onboarding":profile.assessment_result != 0})
    return Response({'error': 'Invalid credentials'}, status=401)


@extend_schema(
    summary="Get onboarding questions",
    description="Retrieve all onboarding questions with their options.",
    tags=["Onboarding"],
    responses={
        200: OpenApiResponse(
            description="List of onboarding questions",
            examples=[
                OpenApiExample(
                    'Questions Example',
                    value={
                        'questions': [
                            {"id": 1, "description": "How often do you exercise?", "option": [{"option_description": "Daily", "id": 1}, {"option_description": "Weekly", "id": 2}]}
                        ]
                    }
                )
            ]
        )
    }
)
class GetOnboardingQuestions(APIView):
    def get(self, request, format=None):
        questions = Question.objects.all()
        return Response({'questions': QuestionSerializer(questions, many=True).data}, status=status.HTTP_200_OK)

@extend_schema(
    summary="Submit onboarding answer",
    description="Submit an answer to an onboarding question. If 'last' is present, returns assessment result.",
    tags=["Onboarding"],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'question': {'type': 'string'},
                'last': {'type': 'boolean', 'required': False}
            }
        }
    },
    responses={
        200: OpenApiResponse(description="Answer submitted", examples=[OpenApiExample('Submitted', value={"message": "Response submitted successfully."})]),
        201: OpenApiResponse(description="Assessment result", examples=[OpenApiExample('Result', value={"result": 80})]),
        400: OpenApiResponse(description="Missing or invalid data", examples=[OpenApiExample('Error', value={"error": "Missing field: id"})]),
        404: OpenApiResponse(description="Not found", examples=[OpenApiExample('Error', value={"error": "Question not found."})])
    }
)
class SubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request, format=None):
        data = request.data  
        try:
            question_id = int(data['id'])       
            answer = data['question']           
            user = request.user                 

            question = Question.objects.get(id=question_id)

            
            # profile = Profile.objects.get(user=user)

            
            try:
                old_response = UserResponse.objects.get(Q(question=question) & Q(user=user))
                old_response.delete()
            except UserResponse.DoesNotExist:
                pass

            
            new_response = UserResponse(
                question=question,
                response=answer,
                user=user
            )
            new_response.save()

            if "last" in data.keys():
                # create assessment result here
                user_response = UserResponse.objects.filter(user=user)
                max_question_weight = 5
                max_score = user_response.count() * max_question_weight
                user_score = 0

                for response in user_response:
                    try:
                        question = response.question
                        selected_option = QuestionOption.objects.get(Q(question=question)&Q(option_description=response.response))
                        user_score += selected_option.score
                    except QuestionOption.DoesNotExist:
                        pass

                percentage = round(user_score * 100 / max_score)
                assessment = UserAssessmentResult(user=user,score=percentage)
                assessment.save()

                return Response({"result":percentage})

            return Response({'message': 'Response submitted successfully.'}, status=200)

        except KeyError as e:
            return Response({'error': f'Missing field: {str(e)}'}, status=400)
        except Question.DoesNotExist:
            return Response({'error': 'Question not found.'}, status=404)
        except Profile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        
    
@extend_schema(
    summary="Get user info",
    description="Retrieve the authenticated user's info.",
    tags=["User"],
    responses={
        200: OpenApiResponse(
            description="User info",
            examples=[
                OpenApiExample(
                    'User Info Example',
                    value={
                        "name": "John Doe",
                        "email": "john@example.com"
                    }
                )
            ]
        )
    }
)


class UserInfo(APIView):
    permission_classes = [IsAuthenticated]
    def get_profile(self,request):
        try:
            profile = Profile.objects.get(user=request.user)
            return profile
        except Profile.DoesNotExist:
            return None
        
    def get(self,request,format=None):
        profile = self.get_profile(request)

        if profile is None:
            return Response(status=401)
        
        user = request.user
        # return a response wih the user information
        return Response({
            "first_name":user.first_name,
            "last_name":user.last_name,
            "email":user.email,
            "assessment":profile.assessment_result
        },status=status.HTTP_200_OK)
    
    def post(self,request,format=None):
        profile = self.get_profile(request)

        if profile is None:
            return Response(status=401)
        
        data = request.POST
        result = int(data['result'])

        profile.assessment_result = result
        profile.save()

        return Response({"msg":"saved"},status=200)