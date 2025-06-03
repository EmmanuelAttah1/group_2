from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login,name='Login'),
    path('submit-answer/', views.SubmitAnswerView.as_view(), name='submit-answer'),
    path('api/onboarding-questions/', views.GetOnboardingQuestions.as_view(), name='get-onboarding-questions'),
]