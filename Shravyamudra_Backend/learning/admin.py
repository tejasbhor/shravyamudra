from django.contrib import admin
from .models import Category, LearnVideo, WatchedVideo, LearningProgress, UserLearningStats

# Register models with admin site
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'icon')
    search_fields = ('name',)
    ordering = ('order', 'name')
    list_per_page = 20

@admin.register(LearnVideo)
class LearnVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'level', 'duration', 'views', 'likes', 'average_rating', 'is_featured')
    list_filter = ('category', 'level', 'is_featured')
    search_fields = ('title', 'description')
    readonly_fields = ('views', 'likes', 'average_rating')
    list_per_page = 20

@admin.register(WatchedVideo)
class WatchedVideoAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'progress', 'is_completed', 'created_at', 'last_watched_at')
    list_filter = ('is_completed', 'video__category')
    search_fields = ('user__username', 'video__title')
    readonly_fields = ('created_at', 'last_watched_at')
    list_per_page = 20

@admin.register(LearningProgress)
class LearningProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'total_time_spent', 'last_activity')
    list_filter = ('category',)
    search_fields = ('user__username', 'category__name')
    list_per_page = 20

@admin.register(UserLearningStats)
class UserLearningStatsAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_videos_watched', 'total_time_spent', 'current_streak', 'longest_streak', 'last_activity')
    search_fields = ('user__username',)
    readonly_fields = ('current_streak', 'longest_streak', 'last_activity')
    list_per_page = 20
