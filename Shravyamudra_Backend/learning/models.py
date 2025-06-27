from django.db import models
from django.conf import settings
from datetime import timedelta

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon name from Lucide icons")
    order = models.PositiveIntegerField(default=0, help_text="Order in which categories should appear")

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class LearnVideo(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='learn/videos/')
    thumbnail = models.ImageField(upload_to='learn/thumbnails/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='videos')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    duration = models.DurationField(blank=True, null=True, help_text="Video duration in HH:MM:SS format")
    is_featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0, help_text="Total number of views")
    likes = models.PositiveIntegerField(default=0, help_text="Total number of likes")
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, help_text="Average rating (0-5)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class WatchedVideo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watched_videos')
    video = models.ForeignKey(LearnVideo, on_delete=models.CASCADE, related_name='watched_by')
    progress = models.PositiveIntegerField(default=0, help_text="Progress percentage (0-100)")
    is_completed = models.BooleanField(default=False)
    last_watched_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video')
        ordering = ['-last_watched_at']

    def __str__(self):
        return f"{self.user.username} watched {self.video.title}"

class LearningProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_progress')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='progress')
    total_videos = models.PositiveIntegerField(default=0)
    completed_videos = models.PositiveIntegerField(default=0)
    total_time_spent = models.DurationField(default=timedelta(), help_text="Total time spent watching videos in this category")
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'category')
        verbose_name_plural = "Learning Progress"

    def __str__(self):
        return f"{self.user.username}'s progress in {self.category.name}"

class UserLearningStats(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_stats')
    total_videos_watched = models.PositiveIntegerField(default=0)
    total_time_spent = models.DurationField(default=timedelta(), help_text="Total time spent learning")
    current_streak = models.PositiveIntegerField(default=0, help_text="Current daily streak")
    longest_streak = models.PositiveIntegerField(default=0, help_text="Longest daily streak")
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s learning stats"
