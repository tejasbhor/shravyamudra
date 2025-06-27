from django.urls import path
from . import views

urlpatterns = [
    # Category endpoints
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    
    # Video endpoints
    path('videos/', views.LearnVideoListView.as_view(), name='video-list'),
    path('videos/<int:pk>/', views.LearnVideoDetailView.as_view(), name='video-detail'),
    
    # Progress tracking endpoints
    path('watched/', views.WatchedVideoListCreateView.as_view(), name='watched-list'),
    path('watched/<int:video_id>/', views.WatchedVideoDeleteView.as_view(), name='watched-delete'),
    path('watched/recent/', views.RecentActivityView.as_view(), name='recent-activity'),
    
    # Stats endpoint
    path('stats/', views.LearnStatsView.as_view(), name='learn-stats'),
]
