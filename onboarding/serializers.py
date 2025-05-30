from rest_framework import serializers

from .models import Question, QuestionOption

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
