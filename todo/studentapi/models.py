from django.db import models
from django.contrib.auth.models import User
class StudentModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True)
    email = models.EmailField(null=True)
    currentSemester = models.IntegerField(null=True)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.name    

