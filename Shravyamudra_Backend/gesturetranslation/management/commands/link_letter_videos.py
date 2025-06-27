import os
from django.core.management.base import BaseCommand
from gesturetranslation.models import LetterGesture
from django.conf import settings

class Command(BaseCommand):
    help = 'Auto-link LetterGesture DB entries to matching video files in media/gestures/letters/'

    def handle(self, *args, **options):
        media_dir = os.path.join(settings.MEDIA_ROOT, 'gestures', 'letters')
        count = 0
        for gesture in LetterGesture.objects.all():
            expected_filename = f"{gesture.letter.upper()}.mp4"
            full_path = os.path.join(media_dir, expected_filename)
            if os.path.exists(full_path):
                gesture.video.name = f"gestures/letters/{expected_filename}"
                gesture.save()
                self.stdout.write(self.style.SUCCESS(f"Linked {gesture.letter} to {expected_filename}"))
                count += 1
            else:
                self.stdout.write(self.style.WARNING(f"No video file for {gesture.letter} ({expected_filename})"))
        self.stdout.write(self.style.SUCCESS(f"Linked {count} LetterGesture entries to video files."))
