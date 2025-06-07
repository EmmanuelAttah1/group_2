from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login,name='Login'),
    path('submit-answer/', views.SubmitAnswerView.as_view(), name='submit-answer'),
    path('onboarding-questions/', views.GetOnboardingQuestions.as_view(), name='get-onboarding-questions'),
    path("user-info", views.UserInfo.as_view(), name="user_info"),
    path("assessment",views.Assessment.as_view(), name="assessment")
]