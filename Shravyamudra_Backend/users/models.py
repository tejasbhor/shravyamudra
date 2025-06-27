from django.contrib.auth.models import AbstractUser
from django.db import models

# Ensure profile is created with user
import users.signals

class User(AbstractUser):
    def delete(self, *args, **kwargs):
        # Prevent infinite recursion
        if hasattr(self, '_deleting'): return
        self._deleting = True
        try:
            if hasattr(self, 'profile') and self.profile:
                self.profile.delete()
        except Exception:
            pass
        super().delete(*args, **kwargs)

    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    # You can add more fields as needed for extensibility

    def is_admin(self):
        return self.role == 'admin'
