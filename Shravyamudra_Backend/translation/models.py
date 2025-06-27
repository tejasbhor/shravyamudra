from django.db import models
from django.conf import settings

class UserAPIKey(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='api_key')
    gemini_api_key = models.CharField(max_length=128)

    def __str__(self):
        return f"API Key for {self.user.username}"

    @property
    def has_key(self):
        return bool(self.gemini_api_key)
