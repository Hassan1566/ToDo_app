from rest_framework.generics import ListAPIView,RetrieveUpdateDestroyAPIView,CreateAPIView
from .models import StudentModel
from .serilaizer import StudentSerializer,NormalUserSerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny

class StudentList(ListAPIView):
    permission_classes = [AllowAny]
    queryset = StudentModel.objects.all()

    
  
    

class StudentCreate(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = StudentModel.objects.all()
    serializer_class = NormalUserSerializer
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudentRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = StudentModel.objects.all()
    


    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        else:
            return [IsAuthenticated()]

