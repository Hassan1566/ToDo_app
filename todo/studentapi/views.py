from rest_framework.generics import ListAPIView,RetrieveUpdateDestroyAPIView,CreateAPIView
from rest_framework.viewsets import ModelViewSet
from .models import StudentModel
from .serilaizer import StudentSerializer,NormalUserSerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from django.contrib.auth.models import User


class StudentViewSet(ModelViewSet):
    queryset = StudentModel.objects.all()
    serializer_class = StudentSerializer
    http_method_names = ['get', 'post', 'patch']
    #def get_queryset(self):
    #   return StudentModel.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        elif self.request.user.is_superuser:
            return [IsAdminUser()]
        elif self.request.method == "POST":
            return [IsAdminUser(),IsAuthenticated()]
        elif self.request.method == "DELETE" or self.request.method == "PUT" or self.request.method == "PATCH":
            return [IsAdminUser()]
        else:
            return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return NormalUserSerializer
        else:
            return StudentSerializer

