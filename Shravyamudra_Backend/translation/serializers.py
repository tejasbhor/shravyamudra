from rest_framework import serializers
from .models import UserAPIKey

class UserAPIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAPIKey
        fields = ['id', 'user', 'has_key']
        read_only_fields = ['id', 'user', 'has_key']

class UserAPIKeySetSerializer(serializers.Serializer):
    api_key = serializers.CharField(write_only=True, min_length=10, max_length=128)
