from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, RegisterSerializer

User = get_user_model()

# User Registration
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

# JWT Login (token)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        return token

    def validate(self, attrs):
        username_or_email = attrs.get("username")
        password = attrs.get("password")
        User = get_user_model()
        user = None

        print(f"Login attempt: {username_or_email}")

        try:
            user = User.objects.get(username=username_or_email)
            print("Found by username")
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username_or_email)
                print("Found by email")
            except User.DoesNotExist:
                print("User not found")
                pass

        if user:
            print("User exists, checking password...")
            if user.check_password(password):
                print("Password correct")
                data = super().validate({"username": user.username, "password": password})
                return data
            else:
                print("Password incorrect")
        else:
            print("No user to check password for")

        from rest_framework import serializers
        raise serializers.ValidationError("No active account found with the given credentials")

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = self.get_user(request)
        response.data['token'] = response.data.get('access')
        from .serializers import UserSerializer
        response.data['user'] = UserSerializer(user).data if user else None
        return response

    def get_user(self, request):
        from django.contrib.auth import get_user_model
        username_or_email = request.data.get('username')
        User = get_user_model()
        try:
            user = User.objects.get(username=username_or_email)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                user = None
        return user

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

class UserManagementViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    def list(self, request):
        User = get_user_model()
        users = User.objects.all()
        from .serializers import UserSerializer
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        User = get_user_model()
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)
        from .serializers import UserSerializer
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def create(self, request):
        User = get_user_model()
        from .serializers import UserSerializer
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(**serializer.validated_data)
            user.role = request.data.get('role', 'user')
            user.save()
            # Ensure profile exists
            from profiles.models import Profile
            Profile.objects.get_or_create(user=user)
            return Response(UserSerializer(user).data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        User = get_user_model()
        from .serializers import UserSerializer
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Update role if present
            if 'role' in request.data:
                user.role = request.data['role']
                user.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        User = get_user_model()
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response({'success': 'User deleted.'})
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)

    @action(detail=True, methods=['post'])
    def promote(self, request, pk=None):
        User = get_user_model()
        try:
            user = User.objects.get(pk=pk)
            user.role = 'admin'
            user.is_superuser = True
            user.is_staff = True
            user.save()
            return Response({'success': f'User {user.username} promoted to admin.'})
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)

    @action(detail=True, methods=['post'])
    def demote(self, request, pk=None):
        User = get_user_model()
        try:
            user = User.objects.get(pk=pk)
            user.role = 'user'
            user.is_superuser = False
            user.is_staff = False
            user.save()
            return Response({'success': f'User {user.username} demoted to user.'})
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)

    @action(detail=False, methods=['post'])
    def repair_profiles(self, request):
        User = get_user_model()
        from profiles.models import Profile
        repaired = 0
        for u in User.objects.all():
            if not hasattr(u, 'profile'):
                Profile.objects.create(user=u)
                repaired += 1
        return Response({'success': f'Repaired {repaired} user profiles.'})

# User Profile (GET/PUT/PATCH)
from rest_framework.permissions import IsAuthenticated

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

