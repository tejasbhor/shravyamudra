from django.urls import path
from .views import UserListView, UserDetailView, UserRoleUpdateView, UserActivationView

urlpatterns = [
    path('users/', UserListView.as_view(), name='admin-user-list'),
    path('users/<int:id>/', UserDetailView.as_view(), name='admin-user-detail'),
    path('users/<int:id>/role/', UserRoleUpdateView.as_view(), name='admin-user-role-update'),
    path('users/<int:id>/activate/', UserActivationView.as_view(), name='admin-user-activate'),
]
