from django.contrib import admin
from .models import LetterGesture, WordGesture

@admin.register(LetterGesture)
class LetterGestureAdmin(admin.ModelAdmin):
    list_display = ('letter', 'video')

@admin.register(WordGesture)
class WordGestureAdmin(admin.ModelAdmin):
    list_display = ('word', 'video')
