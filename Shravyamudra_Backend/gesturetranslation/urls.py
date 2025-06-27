from django.urls import path
from .views import GestureTranslationAPIView

urlpatterns = [
    path('gesture/', GestureTranslationAPIView.as_view(), name='gesture-translation'),
]
