from rest_framework import permissions

class PostOnRundown(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user_profile.id == request.user.id

class UpdateOnProfile(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id