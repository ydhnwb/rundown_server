from rest_framework import permissions

class PostOnRundown(permissions.BasePermission):
    message = {'message':'You do not have permission to do this action', 'status':False, "data":{}}
    def has_object_permission(self, request, view, obj):
        return obj.user_profile.id == request.user.id

class IsTheOwner(permissions.BasePermission):
    message = {'message':'You do not have permission to do this action', 'status':False, "data":{}}
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id

class IsTheOwnerOfFriend(permissions.BasePermission):
    message = {'message': 'You do not have permission to do this action', 'status': False, "data": {}}

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id

