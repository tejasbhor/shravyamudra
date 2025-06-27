from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import LetterGesture, WordGesture
from django.conf import settings
from urllib.parse import urljoin
import os
import re

class GestureTranslationAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        text = request.data.get('text', '')
        mode = request.data.get('mode', 'hybrid')
        if mode == 'letter':
            # Remove non-alphanumeric characters and split into letters
            letters = [c for c in text if c.isalnum()]
            tokens = []
            missing_letters = []
            for idx, letter in enumerate(letters):
                try:
                    gesture = LetterGesture.objects.get(letter__iexact=letter)
                    video_path = gesture.video.path
                    if not os.path.exists(video_path):
                        missing_letters.append(letter)
                        continue
                    # Add a dummy query param to force unique videoUrl for repeated letters
                    video_url = request.build_absolute_uri(gesture.video.url)
                    video_url = f"{video_url}?idx={idx}"
                    tokens.append({
                        'type': 'letter',
                        'value': letter,
                        'videoUrl': video_url
                    })
                except LetterGesture.DoesNotExist:
                    missing_letters.append(letter)
            if missing_letters:
                return Response({
                    'error': f"No gesture video found for: {', '.join(missing_letters)}"
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({'tokens': tokens}, status=status.HTTP_200_OK)

        elif mode == 'word':
            # Split text into words (ignore punctuation)
            words = re.findall(r'\b\w+\b', text.lower())
            tokens = []
            missing_words = []
            for word in words:
                try:
                    gesture = WordGesture.objects.get(word=word)
                    video_url = request.build_absolute_uri(gesture.video.url)
                    tokens.append({
                        'type': 'word',
                        'value': word,
                        'videoUrl': video_url
                    })
                except WordGesture.DoesNotExist:
                    missing_words.append(word)
            if missing_words:
                return Response({
                    'error': f"No gesture video found for words: {', '.join(missing_words)}"
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({'tokens': tokens}, status=status.HTTP_200_OK)

        elif mode == 'hybrid':
            words = re.findall(r'\b\w+\b', text)
            tokens = []
            missing = []
            for word in words:
                word_lc = word.lower()
                try:
                    gesture = WordGesture.objects.get(word=word_lc)
                    video_url = request.build_absolute_uri(gesture.video.url)
                    tokens.append({
                        'type': 'word',
                        'value': word,
                        'videoUrl': video_url
                    })
                except WordGesture.DoesNotExist:
                    # Fallback to spelling the word with letters
                    missing_letters = []
                    for idx, letter in enumerate(word):
                        if letter.isalnum():
                            try:
                                gesture = LetterGesture.objects.get(letter__iexact=letter)
                                video_url = request.build_absolute_uri(gesture.video.url)
                                # Add a dummy query param to force unique videoUrl for repeated letters
                                video_url = f"{video_url}?idx={idx}"
                                tokens.append({
                                    'type': 'letter',
                                    'value': letter,
                                    'videoUrl': video_url
                                })
                            except LetterGesture.DoesNotExist:
                                missing_letters.append(letter)
                    if missing_letters:
                        missing.append(f"{word} (missing: {', '.join(missing_letters)})")
            if missing:
                return Response({
                    'error': f"No gesture video found for: {', '.join(missing)}"
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({'tokens': tokens}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid mode. Use letter, word, or hybrid.'}, status=status.HTTP_400_BAD_REQUEST)
