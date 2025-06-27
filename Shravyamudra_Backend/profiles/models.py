from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')

    def delete(self, *args, **kwargs):
        # Prevent infinite recursion
        if hasattr(self, '_deleting'): return
        self._deleting = True
        user = self.user
        super().delete(*args, **kwargs)
        if user:
            user.delete()

    bio = models.TextField(blank=True, default='')
    accountType = models.CharField(max_length=50, blank=True, default='Free Plan')
    memberSince = models.CharField(max_length=50, blank=True, default='')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    @property
    def avatarUrl(self):
        if self.avatar:
            request = None
            try:
                from django.utils.deprecation import MiddlewareMixin
                # Try to get request from threadlocals if you use a middleware for that
                from threading import current_thread
                request = getattr(current_thread(), 'request', None)
            except Exception:
                pass
            # If request is available, build absolute URL
            if request:
                return request.build_absolute_uri(self.avatar.url)
            # Fallback: use SITE_DOMAIN from settings or hardcode
            from django.conf import settings
            domain = getattr(settings, 'SITE_DOMAIN', None)
            if domain:
                return f'{domain}{self.avatar.url}'
            # Fallback to relative URL
            return self.avatar.url
        return ''

    def __str__(self):
        return f"Profile({self.user.username})"
