from rest_framework import serializers

from .models import Question, QuestionOption
from django.contrib.auth.models import User

# JSON -  Javascript Object Notation
# everything is an object in pyhon

# objects are just entities with attributes
# person
# person.name

# serialization is convert objects from python into JSON

# python datatype    | javascript data type

# integers           | integrs
# string             | string
# boolean
# float
# list               | arrays
# dictionaries
# tuples
# Question           | {desscription : "hxgxjhjhgcjkskchlkjc"}

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']  # Corrected indentation

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class QuestionOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ["option_description","id"]


class QuestionSerializer(serializers.ModelSerializer):
    option = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ["description","option","id"]

    def set_option(self,obj):
        question_option = QuestionOption.objects.filter(question=obj) # get all options for a question
        return QuestionOptionsSerializer(question_option, many=True).data
    
"""
{
    "description" : "description of first question",
    "options":[{"option_description":"option 1", "id":1},{"option_description":"option 1", "id":1}] 
    "id" : 1
  },
"""

class QuestionOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ["option_description","id"]


class QuestionSerializer(serializers.ModelSerializer):
    option = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ["description", "option", "id"]

    def get_option(self, obj):
        question_option = QuestionOption.objects.filter(question=obj)  # get all options for a question
        return QuestionOptionsSerializer(question_option, many=True).data