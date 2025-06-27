from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Category, LearnVideo, WatchedVideo, LearningProgress, UserLearningStats
from .serializers import (
    CategorySerializer, LearnVideoSerializer, WatchedVideoSerializer,
    LearningProgressSerializer, UserLearningStatsSerializer
)
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all().order_by('order', 'name')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class LearnVideoListView(generics.ListCreateAPIView):
    serializer_class = LearnVideoSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        queryset = LearnVideo.objects.all()
        
        # Filter by category
        category_param = self.request.query_params.get('category')
        if category_param:
            try:
                queryset = queryset.filter(category__id=int(category_param))
            except (ValueError, TypeError):
                queryset = queryset.filter(category__name__iexact=category_param)

        # Filter by level
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)

        # Filter by featured
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admin users can create videos")
        serializer.save()

class LearnVideoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LearnVideo.objects.all()
    serializer_class = LearnVideoSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment views when video is retrieved
        instance.views += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Only admin users can update videos")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Only admin users can delete videos")
        return super().destroy(request, *args, **kwargs)

class LearnStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()
        week_ago = now - timedelta(days=7)

        # Get user's learning stats
        user_stats, _ = UserLearningStats.objects.get_or_create(user=user)
        user_stats_serializer = UserLearningStatsSerializer(user_stats)

        # Get category-wise progress
        category_progress = LearningProgress.objects.filter(user=user)
        category_progress_serializer = LearningProgressSerializer(category_progress, many=True)

        # Get recent activity
        recent_activity = WatchedVideo.objects.filter(
            user=user,
            last_watched_at__gte=week_ago
        ).order_by('-last_watched_at')[:5]

        return Response({
            "userStats": user_stats_serializer.data,
            "categoryProgress": category_progress_serializer.data,
            "recentActivity": [
                {
                    "video": {
                        "id": activity.video.id,
                        "title": activity.video.title,
                        "category": activity.video.category.name
                    },
                    "progress": activity.progress,
                    "isCompleted": activity.is_completed,
                    "lastWatched": activity.last_watched_at
                }
                for activity in recent_activity
            ]
        })

class WatchedVideoListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        watched = WatchedVideo.objects.filter(user=request.user)
        serializer = WatchedVideoSerializer(watched, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WatchedVideoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            video = serializer.validated_data['video']
            progress = serializer.validated_data.get('progress', 0)
            is_completed = serializer.validated_data.get('is_completed', False)
            rating = serializer.validated_data.get('rating')

            watched, created = WatchedVideo.objects.update_or_create(
                user=request.user,
                video=video,
                defaults={
                    'progress': progress,
                    'is_completed': is_completed,
                    'rating': rating,
                    'last_watched_at': timezone.now()
                }
            )

            # Update video stats if rating is provided
            if rating:
                video.average_rating = WatchedVideo.objects.filter(
                    video=video
                ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
                video.save()

            # Update learning progress
            self._update_learning_progress(request.user, video.category)
            self._update_user_stats(request.user, video)

            return Response(
                {'detail': 'Progress updated successfully.'},
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _update_learning_progress(self, user, category):
        total_videos = LearnVideo.objects.filter(category=category).count()
        completed_videos = WatchedVideo.objects.filter(
            user=user,
            video__category=category,
            is_completed=True
        ).count()

        # Calculate total time spent in this category
        total_time = timedelta()
        for watched in WatchedVideo.objects.filter(user=user, video__category=category):
            if watched.video.duration:
                total_time += watched.video.duration * (watched.progress / 100)

        LearningProgress.objects.update_or_create(
            user=user,
            category=category,
            defaults={
                'total_videos': total_videos,
                'completed_videos': completed_videos,
                'total_time_spent': total_time,
                'last_activity': timezone.now()
            }
        )

    def _update_user_stats(self, user, video):
        stats, _ = UserLearningStats.objects.get_or_create(user=user)
        
        # Update total videos watched
        stats.total_videos_watched = WatchedVideo.objects.filter(
            user=user,
            is_completed=True
        ).count()

        # Update total time spent
        total_time = timedelta()
        for watched in WatchedVideo.objects.filter(user=user, is_completed=True):
            if watched.video.duration:
                total_time += watched.video.duration

        stats.total_time_spent = total_time

        # Update streak
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        if stats.last_activity.date() == yesterday:
            stats.current_streak += 1
            if stats.current_streak > stats.longest_streak:
                stats.longest_streak = stats.current_streak
        elif stats.last_activity.date() < yesterday:
            stats.current_streak = 1

        stats.last_activity = timezone.now()
        stats.save()

class WatchedVideoDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, video_id):
        try:
            watched = WatchedVideo.objects.get(user=request.user, video_id=video_id)
            video = watched.video
            watched.delete()

            # Update learning progress
            self._update_learning_progress(request.user, video.category)
            self._update_user_stats(request.user, video)

            return Response({'detail': 'Video removed from watched list.'}, status=status.HTTP_200_OK)
        except WatchedVideo.DoesNotExist:
            return Response(
                {'detail': 'Video not found in watched list.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def _update_learning_progress(self, user, category):
        total_videos = LearnVideo.objects.filter(category=category).count()
        completed_videos = WatchedVideo.objects.filter(
            user=user,
            video__category=category,
            is_completed=True
        ).count()

        # Calculate total time spent in this category
        total_time = timedelta()
        for watched in WatchedVideo.objects.filter(user=user, video__category=category):
            if watched.video.duration:
                total_time += watched.video.duration * (watched.progress / 100)

        LearningProgress.objects.update_or_create(
            user=user,
            category=category,
            defaults={
                'total_videos': total_videos,
                'completed_videos': completed_videos,
                'total_time_spent': total_time,
                'last_activity': timezone.now()
            }
        )

    def _update_user_stats(self, user, video):
        stats, _ = UserLearningStats.objects.get_or_create(user=user)
        
        # Update total videos watched
        stats.total_videos_watched = WatchedVideo.objects.filter(
            user=user,
            is_completed=True
        ).count()

        # Update total time spent
        total_time = timedelta()
        for watched in WatchedVideo.objects.filter(user=user, is_completed=True):
            if watched.video.duration:
                total_time += watched.video.duration

        stats.total_time_spent = total_time
        stats.save()

class RecentActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        recent_activity = WatchedVideo.objects.filter(
            user=request.user
        ).select_related('video').order_by('-last_watched_at')[:10]

        return Response([{
            'id': activity.id,
            'video': {
                'id': activity.video.id,
                'title': activity.video.title,
                'thumbnail': activity.video.thumbnail.url if activity.video.thumbnail else None
            },
            'watched_at': activity.last_watched_at
        } for activity in recent_activity])
