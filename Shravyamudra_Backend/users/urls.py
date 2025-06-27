from django.urls import path, include
from .views import RegisterView, CustomTokenObtainPairView, ProfileView, UserManagementViewSet
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'manage', UserManagementViewSet, basename='usermanage')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', ProfileView.as_view(), name='profile'),
    path('profile/', include('profiles.urls')),
    path('', include(router.urls)),
]
