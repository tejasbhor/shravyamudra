from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from learning.models import Category, LearnVideo, LearningProgress, UserLearningStats
from datetime import timedelta
from django.utils import timezone
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with sample learning data'

    def handle(self, *args, **kwargs):
        # Get existing categories
        existing_categories = Category.objects.all()
        self.stdout.write(self.style.SUCCESS(f'Found {existing_categories.count()} existing categories'))

        # Create or update categories only if they don't exist
        categories_data = [
            {'name': 'Alphabets', 'order': 1, 'icon': 'book'},
            {'name': 'Numbers', 'order': 2, 'icon': 'hash'},
            {'name': 'Common Words', 'order': 3, 'icon': 'message-square'},
            {'name': 'Phrases', 'order': 4, 'icon': 'message-circle'},
            {'name': 'Grammar', 'order': 5, 'icon': 'book-open'},
        ]

        categories = []
        for cat_data in categories_data:
            if not Category.objects.filter(name=cat_data['name']).exists():
                category = Category.objects.create(**cat_data)
                self.stdout.write(self.style.SUCCESS(f'Created new category: {category.name}'))
            else:
                category = Category.objects.get(name=cat_data['name'])
                self.stdout.write(self.style.SUCCESS(f'Category already exists: {category.name}'))
            categories.append(category)

        # Create or update sample videos for each category
        for category in categories:
            existing_videos = LearnVideo.objects.filter(category=category)
            self.stdout.write(self.style.SUCCESS(f'Found {existing_videos.count()} existing videos for {category.name}'))

            for i in range(1, 4):  # 3 videos per category
                video_title = f'{category.name} Video {i}'
                if not LearnVideo.objects.filter(title=video_title, category=category).exists():
                    # Create a unique path for each video in the learn directory
                    video_path = os.path.join('learn', 'videos', f'{category.name.lower()}_{i}.mp4')
                    
                    video = LearnVideo.objects.create(
                        title=video_title,
                        category=category,
                        description=f'Learn {category.name.lower()} with this video',
                        video_file=video_path,
                        level='beginner' if i == 1 else 'intermediate' if i == 2 else 'advanced',
                        duration=timedelta(minutes=i * 5),
                        is_featured=(i == 1)
                    )
                    self.stdout.write(self.style.SUCCESS(f'Created new video: {video.title}'))
                    self.stdout.write(self.style.SUCCESS(f'Video path: {video_path}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Video already exists: {video_title}'))

        # Create or update test user
        if not User.objects.filter(username='testuser').exists():
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123'
            )
            self.stdout.write(self.style.SUCCESS('Created test user'))
        else:
            user = User.objects.get(username='testuser')
            self.stdout.write(self.style.SUCCESS('Test user already exists'))

        # Create or update learning progress for the test user
        for category in categories:
            if not LearningProgress.objects.filter(user=user, category=category).exists():
                progress = LearningProgress.objects.create(
                    user=user,
                    category=category,
                    total_time_spent=timedelta()
                )
                self.stdout.write(self.style.SUCCESS(f'Created progress for {category.name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Progress already exists for {category.name}'))

        # Create or update user learning stats
        if not UserLearningStats.objects.filter(user=user).exists():
            stats = UserLearningStats.objects.create(
                user=user,
                total_videos_watched=0,
                total_time_spent=timedelta(),
                current_streak=0,
                longest_streak=0,
                last_activity=timezone.now()
            )
            self.stdout.write(self.style.SUCCESS('Created user learning stats'))
        else:
            self.stdout.write(self.style.SUCCESS('User learning stats already exist'))

        self.stdout.write(self.style.SUCCESS('Successfully populated learning data')) 