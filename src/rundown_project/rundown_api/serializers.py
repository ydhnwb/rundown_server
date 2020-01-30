from rest_framework import serializers
from . import models


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = ("id", "email", "name", "password")
        extra_kwargs = {"password": {"write_only": True}}


class RundownSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Rundown
        fields = ("id", "user_profile", "title", "description", "is_trashed")
        extra_kwargs = {"user_profile": {"read_only": True}}



