from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework import filters
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from . import serializers
from . import permissions
from . import models

class LoginViewSet(viewsets.ViewSet):
    serializer_class = AuthTokenSerializer

    def create(self, request):
        user = models.UserProfile.objects.filter(email = request.data.get('username')).first()
        if user is None:
            return Response({'message':'No user registered with this email.', 'status':False})
        return ObtainAuthToken().post(request)

class RegisterViewSet(viewsets.ViewSet):
    serializer_class = serializers.UserProfileSerializer

    def create(self, request):
        serializer = serializers.UserProfileSerializer(data = request.data)
        if serializer.is_valid():
            user = models.UserProfile(
                email = serializer.data.get('email'),
                name = serializer.data.get('name')
            )
            user.set_password(request.data.get('password'))
            user.save()
            return Response({'message': 'Register successful', 'status': True, 'data':{
                'name':user.name,
                'email':user.email
            }})
        else:
            return Response({'message': 'An error due to bad request', 'status':False, 'errors': serializer.errors},
                            status= status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ViewSet):
    queryset = models.UserProfile.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.UpdateOnProfile,IsAuthenticated)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'email')

    def list(self, request):
        return Response({'message':'list of all users and you must be authenticated', 'status': True, 'data':[]})



class RundownViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.RundownSerializer
    permission_classes = (permissions.PostOnRundown,IsAuthenticated)

    def list(self, request):
        print("list")
        return Response({'message':'this is a get method', 'status': True, 'data': {}})

    def create(self, request):
        serializer = serializers.RundownSerializer(data = request.data)
        if serializer.is_valid():
            return Response({'message':'this is a post create method', 'status': True, 'data': {}})
        else:
            return Response({'message': 'An error due to bad request', 'status':False, 'errors': serializer.errors},
                            status= status.HTTP_400_BAD_REQUEST)
    def retrieve(self, request, pk = None):
        return Response({'message': 'this is a retrieve method', 'status': True, 'data': {}})

    def update(self, request, pk = None):
        return Response({'message': 'this is an update method', 'status': True, 'data': {}})

    def partial_update(self, request, pk = None):
        return Response({'message': 'this is a patch method', 'status': True, 'data': {}})

    def destroy(self, request, pk = None):
        return Response({'message': 'this is a destroy method', 'status': True, 'data': {}})

