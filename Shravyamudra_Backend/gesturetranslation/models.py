from django.db import models
from django.core.exceptions import ValidationError
import os
import re

class LetterGesture(models.Model):
    letter = models.CharField(max_length=2, unique=True, help_text="Single letter (A-Z, a-z) or digit (0-9)")
    video = models.FileField(upload_to='gestures/letters/')

    def clean(self):
        # Letter validation
        if not re.fullmatch(r'[A-Za-z0-9]', self.letter):
            raise ValidationError('Letter must be a single character: A-Z, a-z, or 0-9.')
        # Filename validation
        expected_name = f"{self.letter.upper()}{os.path.splitext(self.video.name)[1]}"
        if os.path.basename(self.video.name).lower() != expected_name.lower():
            raise ValidationError(f"Video filename must match the letter (e.g., {expected_name})")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Letter: {self.letter}"

class WordGesture(models.Model):
    word = models.CharField(max_length=32, unique=True, help_text="Lowercase word, numbers, underscores, or hyphens")
    video = models.FileField(upload_to='gestures/words/')

    def clean(self):
        # Word validation
        if not re.fullmatch(r'[a-z0-9_-]+', self.word):
            raise ValidationError('Word must be lowercase, and may include numbers, underscores, or hyphens.')
        # Filename validation
        expected_name = f"{self.word}{os.path.splitext(self.video.name)[1]}"
        if os.path.basename(self.video.name).lower() != expected_name.lower():
            raise ValidationError(f"Video filename must match the word (e.g., {expected_name})")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Word: {self.word}"
