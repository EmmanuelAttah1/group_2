from django.contrib import admin
from .models import Profile, Question, QuestionOption, UserResponse


admin.site.register(Profile)
admin.site.register(Question)
admin.site.register(QuestionOption)
admin.site.register(UserResponse)
