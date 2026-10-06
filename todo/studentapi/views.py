from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from .models import StudentModel
from .serilaizer import StudentSerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny

class StudentListCreate(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = StudentModel.objects.all()
    serializer_class = StudentSerializer

    def get_queryset(self):
        if self.request.user:
            return StudentModel.objects.all()
        return StudentModel.objects.filter(name=self.request.user.username)
    
    def get(self, request, *args, **kwargs):
        authentication_classes = []
        permission_classes = [AllowAny]
        return self.list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.user:
            return StudentSerializer
        return NormalUserSerializer

class StudentRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    queryset = StudentModel.objects.all()
    serializer_class = StudentSerializer

    def get_queryset(self):
        if self.request.user:
            return StudentModel.objects.all()
        return StudentModel.objects.filter(name=self.request.user.username)

