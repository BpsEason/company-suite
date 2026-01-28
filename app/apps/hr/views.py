from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import User
from rest_framework.serializers import ModelSerializer

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'employee_id', 'role', 'email']

class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # 這裡可以實作：只有 ADMIN 和 HR 角色能看全體員工
    permission_classes = [permissions.IsAuthenticated]