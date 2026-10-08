from rest_framework import serializers
from .models import StudentModel

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentModel
        fields = ['id','name','age','email','address','city']
        read_only_fields = ['id']

class NormalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentModel
        fields = ['id','name','age','email','currentSemester','address','city']
        read_only_fields = ['id']