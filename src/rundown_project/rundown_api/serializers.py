from rest_framework import serializers, fields
from . import models

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = ("id", "email", "name", "password")
        extra_kwargs = {"password": {"write_only": True}}

class RundownDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RundownDetail
        fields = ("id", "title", "description", "with_date", "order_num", "rundown")
        extra_kwargs = {"rundown": {"read_only": True}}

class RundownSerializer(serializers.ModelSerializer):
    rundown_details = RundownDetailSerializer(read_only=True, many=True)

    class Meta:
        model = models.Rundown
        fields = ("id", "user_profile", "title", "description", "is_trashed", "rundown_details")
        extra_kwargs = {"user_profile": {"read_only": True}}


