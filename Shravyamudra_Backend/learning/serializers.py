from rest_framework import serializers
from .models import Category, LearnVideo, WatchedVideo, LearningProgress, UserLearningStats
from django.utils import timezone

class CategorySerializer(serializers.ModelSerializer):
    video_count = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'order', 'video_count', 'progress']

    def get_video_count(self, obj):
        return obj.videos.count()

    def get_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = LearningProgress.objects.get(user=request.user, category=obj)
                return {
                    'total': progress.total_videos,
                    'completed': progress.completed_videos,
                    'percentage': int((progress.completed_videos / progress.total_videos * 100) if progress.total_videos > 0 else 0),
                    'time_spent': str(progress.total_time_spent)
                }
            except LearningProgress.DoesNotExist:
                return {'total': 0, 'completed': 0, 'percentage': 0, 'time_spent': '0:00:00'}
        return {'total': 0, 'completed': 0, 'percentage': 0, 'time_spent': '0:00:00'}

class LearnVideoSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=True
    )
    is_completed = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    is_new = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = LearnVideo
        fields = [
            'id', 'title', 'description', 'video_file', 'thumbnail',
            'category', 'category_id', 'level', 'duration', 'is_featured',
            'views', 'likes', 'average_rating', 'created_at', 'updated_at',
            'is_completed', 'progress', 'is_new', 'user_rating'
        ]
        read_only_fields = ['created_at', 'updated_at', 'views', 'likes', 'average_rating']

    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                watched = WatchedVideo.objects.get(user=request.user, video=obj)
                return watched.is_completed
            except WatchedVideo.DoesNotExist:
                return False
        return False

    def get_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                watched = WatchedVideo.objects.get(user=request.user, video=obj)
                return watched.progress
            except WatchedVideo.DoesNotExist:
                return 0
        return 0

    def get_is_new(self, obj):
        # Consider a video new if it was created within the last 7 days
        return (timezone.now() - obj.created_at).days <= 7

    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                watched = WatchedVideo.objects.get(user=request.user, video=obj)
                return watched.rating if hasattr(watched, 'rating') else None
            except WatchedVideo.DoesNotExist:
                return None
        return None

    def validate(self, data):
        errors = {}
        
        if not data.get('video_file'):
            errors['video_file'] = 'Video file is required'
        if not data.get('title'):
            errors['title'] = 'Title is required'
        if not data.get('category'):
            errors['category_id'] = 'Category is required'
            
        if errors:
            raise serializers.ValidationError(errors)
            
        return data

class WatchedVideoSerializer(serializers.ModelSerializer):
    video = LearnVideoSerializer(read_only=True)
    video_id = serializers.PrimaryKeyRelatedField(queryset=LearnVideo.objects.all(), source='video', write_only=True)
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False)

    class Meta:
        model = WatchedVideo
        fields = ['id', 'user', 'video', 'video_id', 'progress', 'is_completed', 'rating', 'last_watched_at', 'created_at']
        read_only_fields = ['user', 'last_watched_at', 'created_at']

    def validate_progress(self, value):
        if not 0 <= value <= 100:
            raise serializers.ValidationError("Progress must be between 0 and 100")
        return value

class LearningProgressSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)

    class Meta:
        model = LearningProgress
        fields = ['id', 'user', 'category', 'category_id', 'total_videos', 'completed_videos', 'total_time_spent', 'last_activity', 'created_at']
        read_only_fields = ['user', 'last_activity', 'created_at']

class UserLearningStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLearningStats
        fields = ['total_videos_watched', 'total_time_spent', 'current_streak', 'longest_streak', 'last_activity', 'created_at']
        read_only_fields = ['last_activity', 'created_at']
