from django.urls import path
from . import views

urlpatterns = [
    path("log-habit/",views.log_habit_value, name="log_habit"),
    path("avg_habit_log/<int:habit_id>", views.get_user_average_habit_value, name="avg_habit"),
    path('habit-over-time', views.GetHabitLog.as_view(), name="habit_log"),
    path('target',views.GetHabitTarget.as_view(), name="target"),
    path('goals', views.GetGoals.as_view(), name="goals"),
    path("plan",views.GetUserPlan.as_view(),name="plan"),
    path("assessment",views.Assessment.as_view(), name="assessment")
]