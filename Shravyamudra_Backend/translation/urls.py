from django.urls import path
from .views import GeminiAPIKeyView, TranslationAPIView

urlpatterns = [
    path('keys/gemini/', GeminiAPIKeyView.as_view(), name='gemini-api-key'),
    path('translate/', TranslationAPIView.as_view(), name='translation'),
    path('convert/', TranslationAPIView.as_view(), name='translation-convert'),
]
