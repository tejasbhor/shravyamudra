from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    avatarUrl = serializers.ReadOnlyField()
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = ['bio', 'accountType', 'memberSince', 'avatar', 'avatarUrl']
