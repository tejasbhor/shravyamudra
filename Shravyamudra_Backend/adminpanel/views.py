from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import AdminUserSerializer
from .permissions import IsAdminUserRole

User = get_user_model()

# List all users, with optional filtering
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get('role')
        is_active = self.request.query_params.get('is_active')
        if role:
            queryset = queryset.filter(role=role)
        if is_active is not None:
            queryset = queryset.filter(is_active=(is_active.lower() == 'true'))
        return queryset

# Retrieve, update, or delete a user by ID
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdminUserRole]
    lookup_field = 'id'

# Promote/demote user to admin/regular
class UserRoleUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def post(self, request, id):
        user = User.objects.filter(id=id).first()
        if not user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        new_role = request.data.get('role')
        if new_role not in ['user', 'admin']:
            return Response({'detail': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)
        user.role = new_role
        user.save()
        return Response({'detail': f'User role updated to {new_role}.'})

# Activate/deactivate user
class UserActivationView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def post(self, request, id):
        user = User.objects.filter(id=id).first()
        if not user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        is_active = request.data.get('is_active')
        if is_active not in [True, False, 'true', 'false', 'True', 'False']:
            return Response({'detail': 'Invalid is_active value.'}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = str(is_active).lower() == 'true'
        user.save()
        return Response({'detail': f'User active status set to {user.is_active}.'})
