from rest_framework import serializers
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


class RundownSerializer(serializers.ModelSerializer):
    rundown_details = RundownDetailSerializer(read_only=True, many=True)

    class Meta:
        model = models.Rundown
        fields = ("id", "user_profile", "title", "description", "is_trashed", "rundown_details")
        extra_kwargs = {"user_profile": {"read_only": True}}

class FriendSerializer(serializers.ModelSerializer):
    friend = UserProfileSerializer(required=False)
    user = UserProfileSerializer(required=False)

    class Meta:
        model = models.Friend
        fields = ("id", "user", "is_blocked", "is_accepted", "requested_by", "friend")
        extra_kwargs = {"user": {"read_only": True}}

class OptFriendSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(required=False)

    class Meta:
        model = models.Friend
        fields = ("id", "user", "is_blocked", "is_accepted", "requested_by","friend")
        extra_kwargs = {"user": {"read_only": True}}

class ReorderRundownDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    rundown_id = serializers.IntegerField()
    order_num = serializers.IntegerField()